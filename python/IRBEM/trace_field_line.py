from IRBEM import MagFields
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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
    
    # Initialize the MagFields class
    model = MagFields(options=[0, 0, 0, 0, 0], 
                     kext=7,  # T96 model
                     sysaxes=3)  # GSM coordinates
    
    # Prepare input for field line tracing
    LLA = {
        'x1': position['x1'],
        'x2': position['x2'],
        'x3': position['x3'],
        'dateTime': dateTime
    }
    
    # Trace the field line
    trace_output = model.trace_field_line(LLA, maginput)
    
    print("\nTrace Output Info:")
    for key, value in trace_output.items():
        print(f"{key}: {value.shape if hasattr(value, 'shape') else value}")
    
    if 'POSIT' in trace_output:
        positions = trace_output['POSIT']
        if positions.size > 0:
            plot_field_line(positions)
        else:
            print("Warning: No field line points available for plotting")
    else:
        print("Error: No position data in trace output")

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
    
    plt.show()

if __name__ == '__main__':
    # Define test cases
    test_positions = [
        {'x1': 7.5, 'x2': 3.0, 'x3': 2.0},  # Original position
        {'x1': 4.0, 'x2': 0.0, 'x3': 0.0},  # On X-axis
        {'x1': 3.0, 'x2': 0.0, 'x3': 3.0},  # In X-Z plane
    ]
    
    dateTime = '2024-01-01T00:00:00'
    
    # Magnetic field parameters for T96 model
    maginput = {
        'Pdyn': 2.0,  # Solar wind dynamic pressure (nPa)
        'Dst': 0,     # Dst index (nT)
        'By': 0.0,    # GSM y-component of IMF (nT)
        'Bz': 0.0,    # GSM z-component of IMF (nT)
    }
    
    # Try each test position
    for i, pos in enumerate(test_positions):
        print(f"\nTest Case {i+1}:")
        trace_and_plot_field_line(pos, dateTime, maginput)