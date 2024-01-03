import serial.tools.list_ports
import time
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider

# Find available COM ports
ports = serial.tools.list_ports.comports()
if len(ports) == 0:
    print("No COM ports available.")
    exit()

# Display available COM ports to the user
print("Available COM ports:")
for i, port in enumerate(ports):
    print(f"{i}: {port.device}")

# Prompt the user to select a COM port
selection = int(input("Select a port: "))
if selection < 0 or selection >= len(ports):
    print("Invalid selection.")
    exit()

# Connect to the selected COM port
port = serial.Serial(ports[selection].device, 115200, timeout=1)

# Send the M420 V command
port.write(b'M420 V\n')

# Wait for response
time.sleep(1)
response = port.readlines()
lines=np.array([x.decode() for x in response])

# Create a list to store the data
data = []

i = 0
while i < len(lines):
    line = lines[i].strip()
    if line == 'Subdivided with CATMULL ROM Leveling Grid:':
        i += 1
        header = lines[i].strip().split()
        i += 1
        for j in range(len(header)):
            row = [header[j]]
            for k in range(len(header)):
                row.append(lines[i].strip().split()[k])
            data.append(row)
            i += 1
    else:
        i += 1
# Scrub the leftover empty columns
points_list = [sublist[2:] for sublist in data]

# Write the data to a CSV file
with open('output.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(points_list)

# Load the data from a csv file
data = pd.read_csv('output.csv', header=None).values

# Compute the x and y coordinates of the grid points
x, y = np.meshgrid(np.arange(data.shape[1]), np.arange(data.shape[0]))

# Fit a plane to the data using linear regression
X = np.column_stack((x.ravel(), y.ravel()))
model = LinearRegression().fit(X, data.ravel())
plane = model.predict(X).reshape(data.shape)

# Subtract the plane from the data to flatten out the angled plane
flattened_data = data - plane

# np.savetxt('normalized_points.csv', flattened_data, delimiter=',')

def plot_surface(heights):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x, y = np.meshgrid(np.arange(heights.shape[1]), np.arange(heights.shape[0]))
    surf = ax.plot_surface(x, y, heights, cmap='coolwarm')
    
    # Add a slider to control the z-axis graph limits
    ax_zlim = plt.axes([0.25, 2*heights.min(), 0.65, 2*heights.max()]) # [left, bottom, width, height]
    zlim_slider = Slider(ax_zlim, 'Z-Lim', 10*heights.min(), -0.05, valinit=heights.min())
    
    def update_zlim(val):
        ax.set_zlim(zlim_slider.val, -1*zlim_slider.val)
        fig.canvas.draw_idle()
        
    zlim_slider.on_changed(update_zlim)
    
    # Add axis labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    plt.show()
    
# flattened_data is your 2D array of flattened heights
plot_surface(flattened_data)