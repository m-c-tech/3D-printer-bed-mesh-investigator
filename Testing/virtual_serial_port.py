import serial

import serial.tools.list_ports
import time

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

ser = serial.Serial(ports[selection].device, 115200) # replace with the correct port and baud rate
output_filename = 'output.txt'

while True:
    data = ser.readline().strip()
    if data == b'M420 V':
        # Read contents of text file
        with open('input.txt', 'r') as f:
            file_data = f.read()
        # Send file contents over serial port
        ser.write(file_data.encode())
        #exit()