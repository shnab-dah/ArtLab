import os
import tkinter as tk
from tkinter import messagebox
import serial
import time
import serial.tools.list_ports
import threading
import queue
import subprocess
import digiCamControlPython as dccp
from datetime import datetime

CAPTURES_FOLDER = 'captures'

# setup camera
CAMERA = dccp.Camera()

current_x = 0
current_y = 0

# Queue for serial communication
serial_queue = queue.Queue()

# Function to get available COM ports with their descriptions
def get_com_ports():
    ports = list(serial.tools.list_ports.comports())
    return [(port.device, port.description) for port in ports]

# Function to initialize serial communication with selected port
def initialize_serial():
    global ser
    selected_port = com_port_var.get()

    if selected_port:
        # Extract only the device (e.g., 'COM7') from the selected port tuple
        port_device = selected_port.split(" - ")[0]
        try:
            ser = serial.Serial(port_device, 115200, timeout=1)
            connection_status_label.config(bg="green")  # Change to green on success
            messagebox.showinfo("Success", f"Connected to {port_device}")
            start_reading()  # Start a background thread to read serial data
        except serial.SerialException:
            connection_status_label.config(bg="red")  # Change to red on failure
            messagebox.showerror("Connection Error", f"Failed to connect to {port_device}")
    else:
        messagebox.showerror("No Port Selected", "Please select a COM port.")
        connection_status_label.config(bg="red")  # Change to red if no port selected

# Function to send a command to Arduino
def send_command(command):
    if ser:
        print(f"Sending: {command}")
        ser.write(f"{command}\n".encode())

# Function to move both X and Y axes
def move_xy():
    x_val = x_entry.get()
    y_val = y_entry.get()
    if x_val.isdigit() and y_val.isdigit():
        send_command(f"MOVE {x_val},{y_val}")
    else:
        messagebox.showerror("Invalid Input", "Please enter valid X and Y positions")

def move(x, y, timeout=15):
    send_command(f"MOVE {x},{y}")
    print("waiting")

    start_time = time.time()  # Record start time
    while True:
        if ser and ser.in_waiting:
            data = ser.readline().decode().strip()
            print(f"Received data: {data}")  # Debugging print

            if data.startswith("POSITION"):
                try:
                    _, pos_x, pos_y = data.split()
                    if int(pos_x) == x and int(pos_y) == y:
                        print("Move confirmed.")
                        return  # Exit function on successful move
                except Exception as e:
                    print(f"Error parsing position: {e}")
                    return  # Avoid getting stuck

        # Break loop if timeout is reached
        if time.time() - start_time > timeout:
            print("Move timed out!")
            return

# Function to center motors
def center_motors():
    send_command("CENTER")

# Function to calibrate motors
def calibrate_motors():
    send_command("CALIBRATE")

# Start a background thread to continuously read data from Arduino
def start_reading():
    threading.Thread(target=read_serial_data, daemon=True).start()

# Function to read serial data (in the background thread)
def read_serial_data():
    while True:
        if ser and ser.in_waiting:
            try:
                data = ser.readline().decode().strip()
                print(f"Received data: {data}")  # Optional: Add a print statement to help debug
                if data.startswith("POSITION"):
                    # Example: "POSITION 100,200"
                    _, pos_x, pos_y = data.split()
                    update_position(int(pos_x), int(pos_y))
                elif data.startswith("CALIBRATED"):
                    # Example: "CALIBRATED 3269, 4000,"
                    _, max_x, max_y = data.split()
                    max_x = max_x.strip(',')  # Remove any commas
                    max_y = max_y.strip(',')  # Remove any commas
                    update_calibration(int(max_x), int(max_y))
            except Exception as e:
                print(f"Error reading serial data: {e}")

        time.sleep(0.1)  # Slight delay to prevent 100% CPU usage in the loop

# Function to update position in the GUI
def update_position(x, y):
    global current_x, current_y
    position_label.config(text=f"Position: X={x}, Y={y}")
    current_x = x
    current_y = y

# Function to update maxX and maxY in the GUI
def update_calibration(max_x, max_y):
    calibration_label.config(text=f"Max Position: X={max_x}, Y={max_y}")

# Function to capture
def capture():
    y1 = int(y1_entry.get())
    x1 = int(x1_entry.get())
    y2 = int(y2_entry.get())
    x2 = int(x2_entry.get())

    horizontal_step = int(horizontal_step_entry.get())
    vertical_step = int(vertical_step_entry.get())

    vertical_stops = ((y2 - y1) // vertical_step) + (1 if (y2 - y1) % vertical_step != 0 else 0)
    horizontal_stops = ((x2 - x1) // horizontal_step) + (1 if (x2 - x1) % horizontal_step != 0 else 0)

    print(f'vertical stops: {vertical_stops}\nhorizontal_stops: {horizontal_stops}\ntotal photos: {vertical_stops*horizontal_stops}')

    stops = []

    for n in range(vertical_stops + 1):
        row = []
        for z in range(horizontal_stops + 1):
            dx = x1 + (z * horizontal_step)
            dy = y1 + (n * vertical_step)
            row.append((min(dx, x2), min(dy, y2)))  # Ensure the last row and column reach (x2, y2)

        if n % 2 == 1:  # Reverse order for zigzag effect
            row.reverse()

        stops.extend(row)

    # Ensure the last row is fully included
    if stops[-1][1] < y2:
        for z in range(horizontal_stops + 1):
            stops.append((min(x1 + (z * horizontal_step), x2), y2))

    # setup camera settings
    '''
    session_name = datetime.now().strftime("%Y-%m-%d_%H%M")
    session_name = f"{session_name}-{panorama_name_entry.get()}"
    session_folder = os.path.join(CAPTURES_FOLDER, session_name)
    os.makedirs(session_folder, exist_ok=True)
    CAMERA.set_folder(folder=session_folder)
    '''
    CAMERA.set_transfer(location="Save_to_camera_only")
    CAMERA.set_counter(counter=0)
    CAMERA.set_compression(comp="RAW")

    for stop in stops:
        move(stop[0], stop[1])
        photo = takePhoto()

        if photo == False:
            CAMERA.set_autofocus(status=False)
            CAMERA.capture()
            CAMERA.set_autofocus(status=True)

    print('done')



def takePhoto(retries=3):
    for attempt in range(retries):
        response = CAMERA.capture()

        # Check if the response contains a focus error
        if str(response) == '-1':
            print(f"Focus error detected, retrying... ({attempt + 1}/{retries})")
            time.sleep(1)  # Wait before retrying
        else:
            print("Photo captured successfully.")
            return True# Exit if capture succeeds

    print("Failed to capture photo after multiple attempts.")
    return False

# Function to store current position in x1, y1
def set_x1_y1():
    x1_entry.delete(0, tk.END)
    y1_entry.delete(0, tk.END)
    x1_entry.insert(0, str(current_x))
    y1_entry.insert(0, str(current_y))

# Function to store current position in x2, y2
def set_x2_y2():
    x2_entry.delete(0, tk.END)
    y2_entry.delete(0, tk.END)
    x2_entry.insert(0, str(current_x))
    y2_entry.insert(0, str(current_y))

# Create main window
root = tk.Tk()
root.title("CNC Controller")

# COM Port selection dropdown
com_port_label = tk.Label(root, text="Select COM Port:")
com_port_label.grid(row=0, column=0, padx=5, pady=5)

# Get available COM ports and create a dropdown menu
com_ports = get_com_ports()
com_ports_display = [f"{port[0]} - {port[1]}" for port in com_ports]  # Display both device and description
com_port_var = tk.StringVar(root)
com_port_var.set(com_ports_display[0] if com_ports_display else "")  # Default to the first available port
com_port_menu = tk.OptionMenu(root, com_port_var, *com_ports_display)
com_port_menu.grid(row=0, column=1, padx=5, pady=5)

# Connect button
connect_button = tk.Button(root, text="Connect", command=initialize_serial)
connect_button.grid(row=0, column=2, padx=5, pady=5)

# Connection status indicator (red by default)
connection_status_label = tk.Label(root, width=3, height=1, bg="red")
connection_status_label.grid(row=0, column=3, padx=5, pady=5)

# X and Y input controls placed next to each other using grid
x_label = tk.Label(root, text="Move to X:")
x_label.grid(row=1, column=0, padx=5, pady=5)
x_entry = tk.Entry(root)
x_entry.grid(row=1, column=1, padx=5, pady=5)

y_label = tk.Label(root, text="Move to Y:")
y_label.grid(row=1, column=2, padx=5, pady=5)
y_entry = tk.Entry(root)
y_entry.grid(row=1, column=3, padx=5, pady=5)

# Move button
move_button = tk.Button(root, text="Move", command=move_xy)
move_button.grid(row=2, column=0, columnspan=4, pady=10)

# Center and Calibrate buttons
center_button = tk.Button(root, text="Center", command=center_motors)
center_button.grid(row=2, column=1, columnspan=4, pady=10)

calibrate_button = tk.Button(root, text="Calibrate", command=calibrate_motors)
calibrate_button.grid(row=2, column=2, columnspan=4, pady=5)

# Position and Calibration status labels
position_label = tk.Label(root, text="Position: X=0, Y=0")
position_label.grid(row=3, column=0, columnspan=4, pady=5)

calibration_label = tk.Label(root, text="Max Position: X=0, Y=0")
calibration_label.grid(row=4, column=0, columnspan=4, pady=5)

# x1, y1 entry and button
x1_label = tk.Label(root, text="x1:")
x1_label.grid(row=5, column=0, padx=5, pady=5)
x1_entry = tk.Entry(root)
x1_entry.grid(row=5, column=1, padx=5, pady=5)

y1_label = tk.Label(root, text="y1:")
y1_label.grid(row=5, column=2, padx=5, pady=5)
y1_entry = tk.Entry(root)
y1_entry.grid(row=5, column=3, padx=5, pady=5)

set_x1_y1_button = tk.Button(root, text="Set x1, y1", command=set_x1_y1)
set_x1_y1_button.grid(row=5, column=4, padx=5, pady=5)

# x2, y2 entry and button
x2_label = tk.Label(root, text="x2:")
x2_label.grid(row=6, column=0, padx=5, pady=5)
x2_entry = tk.Entry(root)
x2_entry.grid(row=6, column=1, padx=5, pady=5)

y2_label = tk.Label(root, text="y2:")
y2_label.grid(row=6, column=2, padx=5, pady=5)
y2_entry = tk.Entry(root)
y2_entry.grid(row=6, column=3, padx=5, pady=5)

set_x2_y2_button = tk.Button(root, text="Set x2, y2", command=set_x2_y2)
set_x2_y2_button.grid(row=6, column=4, padx=5, pady=5)

# Step size entry fields
horizontal_step_label = tk.Label(root, text="Horizontal steps:")
horizontal_step_label.grid(row=8, column=0, padx=5, pady=5)
horizontal_step_entry = tk.Entry(root)
horizontal_step_entry.grid(row=8, column=1, padx=5, pady=5)

vertical_step_label = tk.Label(root, text="Vertical steps:")
vertical_step_label.grid(row=8, column=2, padx=5, pady=5)
vertical_step_entry = tk.Entry(root)
vertical_step_entry.grid(row=8, column=3, padx=5, pady=5)

# Start button for capture
start_button = tk.Button(root, text="Start capture", command=capture)
start_button.grid(row=9, column=0, columnspan=4, pady=5)

panorama_name_label = tk.Label(root, text="Name of sessions:")
panorama_name_label.grid(row=10, column=0, columnspan=4, pady=5)
panorama_name_entry = tk.Entry(root)
panorama_name_entry.grid(row=10, column=1, columnspan=4, pady=5)

'''
wait_label = tk.Label(root, text='Wait for X seconds: ')
wait_label.grid(row=9, column=1, columnspan=4, pady=5)
wait_entry = tk.Entry(root)
wait_entry.grid(row=9, column=2, columnspan=4, pady=5)
'''

# Start the Tkinter main loop
root.mainloop()
