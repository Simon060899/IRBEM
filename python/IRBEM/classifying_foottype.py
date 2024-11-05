from IRBEM import MagFields
import numpy as np
import datetime
import pandas as pd
import sys
import os

def classify_field_line(position, dateTime, maginput):
    """
    Classify the magnetic field line passing through a given position.

    Parameters:
        position (dict): Dictionary containing 'x1', 'x2', 'x3' coordinates.
        dateTime (str): Date and time in ISO format, e.g., '2024-01-01T00:00:00'.
        maginput (dict): Magnetic field inputs required for the model.

    Returns:
        str: Classification of the field line ('closed', 'open', 'IMF').
    """
    # Initialize the MagFields class with desired settings
    # Do not set 'kext' explicitly; infer it from 'maginput' based on required fields
    model = MagFields(options=[0, 0, 0, 0, 0], verbose=True,
                      kext=7,
                      sysaxes = 3)
    # Prepare the inputs
    LLA = {
        'x1': position['x1'],
        'x2': position['x2'],
        'x3': position['x3'],
        'dateTime': dateTime
    }

    # Set stopAlt (desired altitude of field-line crossing), e.g., 100 km
    stopAlt = 100.0  # km

    # Define hemisphere flags: +1 for North, -1 for South
    hemiFlags = [1, -1]

    footpoints_found = 0

    for hemiFlag in hemiFlags:
        try:
            output = model.find_foot_point(LLA, maginput, stopAlt, hemiFlag)
            print(f"Output HemiFlag {hemiFlag}: {output}")  # Debugging output
            footpoints_found += check_if_footpoint_found(output)
        except Exception as e:
            print(f"Error finding footpoint for hemiFlag {hemiFlag}: {e}")

    # Classify based on number of footpoints
    if footpoints_found == 2:
        classification = 'closed'
    elif footpoints_found == 1:
        classification = 'open'
    else:
        classification = 'IMF'

    return classification

def check_if_footpoint_found(output):
    """
    Check if a footpoint was found.

    Parameters:
        output (dict): Output dictionary from the find_foot_point function.

    Returns:
        int: 1 if footpoint found, 0 otherwise.
    """
    Xfoot = output.get('XFOOT')  # Should be a list or tuple [altitude, latitude, longitude]
    baddata = [1e+31, -1e+31, -9999, 9999]# 'baddata' values used in IRBEM

    if Xfoot is None:
        return 0  # Footpoint not found

    Xfoot = np.array(Xfoot)
    if np.any(np.isin(Xfoot, baddata)):
        return 0  # Footpoint not found
    else:
        return 1  # Footpoint found

def prepare_maginput(row):
    """Prepare maginput dictionary from dataframe row."""
    return {
        'Dst': row['Dst_index'],
        'Pdyn': row['Pdyn'],
        'ByIMF': row['BY_GSM'],
        'BzIMF': row['BZ_GSM']
    }

def get_numeric_classification(classification):
    """Convert string classification to numeric code."""
    classification_map = {
        'IMF': 1,
        'open': 0,
        'closed': 2
    }
    return classification_map.get(classification, -1)  # -1 for unknown classifications

def process_orbit_data(filepath):
    """Process orbit data file and classify field lines for each point."""
    # Read the data file
    df = pd.read_csv(filepath, delimiter='\t', parse_dates=['datetime'])
    
    # Initialize classification list
    classifications = []
    
    for _, row in df.iterrows():
        position = {
            'x1': row['x(km)'] / 6371.0,
            'x2': row['y(km)'] / 6371.0,
            'x3': row['z(km)'] / 6371.0
        }
        
        datetime_str = row['datetime'].strftime('%Y-%m-%dT%H:%M:%S')
        maginput = prepare_maginput(row)
        
        # Get classification and convert to numeric
        classification = classify_field_line(position, datetime_str, maginput)
        numeric_classification = get_numeric_classification(classification)
        classifications.append(numeric_classification)
    
    # Add numeric classifications to dataframe
    df['field_line_type'] = classifications
    return df

if __name__ == '__main__':
    input_filepath = 'data/base/orbits_SMILE_augmented_2002_3_years_below_5th.txt'
    output_filepath = input_filepath.replace('.txt', '_classified.txt')
    
    # Process the data
    df_classified = process_orbit_data(input_filepath)
    
    # Save results with same format as input
    df_classified.to_csv(output_filepath, sep='\t', index=False)
    
    # Print summary
    print("\nClassification Summary:")
    classification_counts = df_classified['field_line_type'].value_counts()
    print("0 (open):", classification_counts.get(0, 0))
    print("1 (IMF):", classification_counts.get(1, 0))
    print("2 (closed):", classification_counts.get(2, 0))
