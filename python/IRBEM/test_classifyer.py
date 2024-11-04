from IRBEM import MagFields
import numpy as np
import datetime

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
    print("\nDEBUG INFO:")
    print(f"Input position: {position}")
    print(f"DateTime: {dateTime}")
    print(f"Maginput: {maginput}")
    
    # Initialize the MagFields class with desired settings
    model = MagFields(options=[0, 0, 0, 0, 0], 
                     kext=7,
                     sysaxes=3)  # Let's verify sysaxes=3 is correct for your coordinates
    
    LLA = {
        'x1': position['x1'],
        'x2': position['x2'],
        'x3': position['x3'],
        'dateTime': dateTime
    }
    print(f"LLA input: {LLA}")

    stopAlt = 100.0
    hemiFlags = [1, -1]
    footpoints_found = 0

    for hemiFlag in hemiFlags:
        try:
            print(f"\nTrying hemisphere {hemiFlag}")
            output = model.find_foot_point(LLA, maginput, stopAlt, hemiFlag)
            print(f"Raw output for hemiFlag {hemiFlag}:")
            for key, value in output.items():
                print(f"  {key}: {value}")
            
            found = check_if_footpoint_found(output)
            print(f"Footpoint found: {found}")
            footpoints_found += found
        except Exception as e:
            print(f"Error finding footpoint for hemiFlag {hemiFlag}: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            print(traceback.format_exc())

    print(f"\nTotal footpoints found: {footpoints_found}")
    
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

# Example usage
if __name__ == '__main__':
    # Define the position and date/time
    position = {'x1': 7.5, 'x2': 3.0, 'x3': 2.0}  # More realistic values in RE
    dateTime = '2024-01-01T00:00:00'

    # Correct maginput for T96 model (kext=7)
    maginput = {
        'Pdyn': 2.0,  # Solar wind dynamic pressure (nPa)
        'Dst': 0,     # Dst index (nT)
        'By': 0.0,    # GSM y-component of IMF (nT)
        'Bz': 0.0,    # GSM z-component of IMF (nT)
    }

    # Classify the field line
    classification = classify_field_line(position, dateTime, maginput)
    print(f"The field line is classified as: {classification}")
