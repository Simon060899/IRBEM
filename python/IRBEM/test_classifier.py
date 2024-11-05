from IRBEM import MagFields
import numpy as np
import datetime
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def classify_field_line(position, dateTime, maginput, plot=False):
    """
    Classify the magnetic field line passing through a given position.

    Parameters:
        position (dict): Dictionary containing 'x1', 'x2', 'x3' coordinates.
        dateTime (str): Date and time in ISO format, e.g., '2024-01-01T00:00:00'.
        maginput (dict): Magnetic field inputs required for the model.
        plot (bool): Whether to plot the field line.

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

    # Add field line tracing before footpoint calculation
    trace_output = model.trace_field_line(LLA, maginput)
    
    if plot and 'POSIT' in trace_output:
        plot_field_line(trace_output['POSIT'])

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

def plot_field_line(positions):
    """
    Plot the traced field line in 3D.
    
    Parameters:
        positions (numpy.ndarray): Array of positions along field line (shape: [3, N])
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot the field line
    ax.plot(positions[0], positions[1], positions[2], 'b-', label='Field Line')
    
    # Plot Earth (simplified as a sphere)
    r = 1.0  # Earth radius in RE
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = r * np.outer(np.cos(u), np.sin(v))
    y = r * np.outer(np.sin(u), np.sin(v))
    z = r * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color='lightblue', alpha=0.3)
    
    # Set labels and title
    ax.set_xlabel('X (RE)')
    ax.set_ylabel('Y (RE)')
    ax.set_zlabel('Z (RE)')
    ax.set_title('Magnetic Field Line Trace')
    
    # Set equal aspect ratio
    ax.set_box_aspect([1,1,1])
    
    plt.show()

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

    # Classify the field line and generate plot
    classification = classify_field_line(position, dateTime, maginput, plot=True)
    print(f"The field line is classified as: {classification}")
    
