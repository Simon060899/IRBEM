from IRBEM import MagFields
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys

def trace_and_plot_field_line(position, dateTime, maginput):
    """
    Trace and plot a magnetic field line from a given position.

    Parameters:
        position (dict): Dictionary containing 'x1', 'x2', 'x3' coordinates in RE.
        dateTime (str): Date and time in ISO format, e.g., '2024-01-01T00:00:00'.
        maginput (dict): Magnetic field inputs required for the model.
    """
    print("\nInput Parameters:")
    print(f"Position: {position}")
    print(f"DateTime: {dateTime}")
    print(f"Maginput: {maginput}")
    
    # Initialize the MagFields class with debugging enabled
    model = MagFields(options=[0, 0, 0, 0, 0], 
                     kext=7,  # T96 model
                     sysaxes=3,  # GEO coordinates
                     verbose=True)
    
    # Prepare input for field line tracing
    LLA = {
        'x1': position['x1'],
        'x2': position['x2'],
        'x3': position['x3'],
        'dateTime': dateTime
    }
    
    # First check if the position is valid (inside magnetosphere)
    r = np.sqrt(position['x1']**2 + position['x2']**2 + position['x3']**2)
    if r < 1.0:
        print("Error: Position is inside the Earth!")
        return
    if r > 10.0:
        print("Warning: Position might be outside the magnetosphere")
    
    try:
        # Trace the field line
        trace_output = model.trace_field_line(LLA, maginput)
        
        print("\nTrace Output Info:")
        print(f"Number of points (Nposit): {trace_output['Nposit']}")
        print(f"L shell parameter (lm): {trace_output['lm']}")
        print(f"Minimum B value (bmin): {trace_output['bmin']}")
        
        if trace_output['Nposit'] > 0:
            positions = trace_output['POSIT']
            print(f"Position array shape: {positions.shape}")
            plot_field_line(positions)
        else:
            print("Warning: No field line points available for plotting")
            print("This might indicate that:")
            print("1. The field line is open (extends into interplanetary space)")
            print("2. The starting position is invalid")
            print("3. The magnetic field model parameters are incorrect")
            print(f"Raw trace output: {trace_output}")
    except Exception as e:
        print(f"Error during field line tracing: {str(e)}")

def plot_field_line(positions):
    """
    Plot the traced field line in 3D with Earth.
    
    Parameters:
        positions (numpy.ndarray): Array of positions along field line (shape: [3, N])
    """
    print(f"\nPlotting field line with shape: {positions.shape}")
    
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot the field line
    ax.plot(positions[0], positions[1], positions[2], 'b-', linewidth=2, label='Field Line')
    
    # Plot starting point
    ax.scatter(positions[0,0], positions[1,0], positions[2,0], 
              color='red', s=100, label='Start Point')
    
    # Plot Earth as a sphere
    r = 1.0  # Earth radius in RE
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = r * np.outer(np.cos(u), np.sin(v))
    y = r * np.outer(np.sin(u), np.sin(v))
    z = r * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color='lightblue', alpha=0.3)
    
    # Add coordinate axes
    max_range = np.max(np.abs(positions))
    ax.quiver(-max_range, 0, 0, 2*max_range, 0, 0, color='gray', alpha=0.5)
    ax.quiver(0, -max_range, 0, 0, 2*max_range, 0, color='gray', alpha=0.5)
    ax.quiver(0, 0, -max_range, 0, 0, 2*max_range, color='gray', alpha=0.5)
    
    # Set labels and title
    ax.set_xlabel('X (RE)')
    ax.set_ylabel('Y (RE)')
    ax.set_zlabel('Z (RE)')
    ax.set_title('Magnetic Field Line Trace')
    
    # Set equal aspect ratio and limits
    ax.set_box_aspect([1,1,1])
    limit = max(max_range, 1.5)  # Make sure Earth is visible
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)
    
    # Add legend
    ax.legend()
    
    plt.savefig(f'field_line_trace_{i+1}.png')
    plt.close()

if __name__ == '__main__':
    # Test magnetic field model initialization
    try:
        test_model = MagFields(options=[0, 0, 0, 0, 0], 
                             kext=7,
                             sysaxes=3,
                             verbose=True)
        print("Successfully initialized magnetic field model")
    except Exception as e:
        print(f"Error initializing magnetic field model: {str(e)}")
        sys.exit(1)

    # Define test cases with more conservative positions
    test_positions = [
        {'x1': 4.0, 'x2': 0.0, 'x3': 0.0},  # Equatorial point at 4 RE
        {'x1': 2.0, 'x2': 0.0, 'x3': 1.0},  # Closer to Earth
        {'x1': 3.0, 'x2': 1.0, 'x3': 1.0},  # Off-axis position
    ]
    
    dateTime = '2024-01-01T00:00:00'
    
    # Magnetic field parameters for T96 model need specific keys
    maginput = {
        'Pdyn': 2.0,    # Solar wind dynamic pressure (nPa)
        'Dst': -20,     # Dst index (nT)
        'ByIMF': 2.0,   # IMF By (nT) - note the key change from 'By' to 'ByIMF'
        'BzIMF': -2.0,  # IMF Bz (nT) - note the key change from 'Bz' to 'BzIMF'
    }
    
    # Try each test position
    for i, pos in enumerate(test_positions):
        print(f"\nTest Case {i+1}:")
        trace_and_plot_field_line(pos, dateTime, maginput)