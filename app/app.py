import customtkinter as ctk
import threading
import asyncio
from ble_control import *
discovered_device = None
client = None

motor_direction = 1
motor_enable = 0
motor_speed = 50
angle_delta = 0
UUID = "abcdef01-2345-6789-1234-56789abcdef0"

## ASYNCIO BLE THREAD SETUP -------------------------------------
def run_in_asyncio_thread(coroutine):
    asyncio.run_coroutine_threadsafe(coroutine, asyncio_loop)

def setup_asyncio_thread():
    global asyncio_loop
    asyncio_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(asyncio_loop)
    asyncio_loop.run_forever()

def shutdown_asyncio_thread():
    asyncio_loop.call_soon_threadsafe(asyncio_loop.stop)
    asyncio_thread.join()



# Search & Connect -------------------------------------
def update_device_dropdown(devices):
    global discovered_device
    for d in devices:
        if d[0] == "Rotary_Table":
            device_dropdown.set(d[0])
            discovered_device = d
            break

async def search_devices():
    devices = await discover_devices()
    app.after(0, update_device_dropdown, devices)

def on_search_button_click():
    run_in_asyncio_thread(search_devices())


def update_status():
    connected_label.grid(row=0, column=5, padx=10)

async def connect_device():
    global client
    client = await connect_to_device(discovered_device[1])
    if client:
        app.after(0, update_status)

def on_connect_button_click():
    run_in_asyncio_thread(connect_device())   

def connect_action():
    # This function is called when the connect button is clicked.
    selected_item = device_dropdown.get()
    if selected_item == "No devices found":
        print("Please select a device first.")
    elif discovered_device is None:
        print("Please search for devices first.")
    else:
        print(f"Connecting to: {selected_item}")

# Send Commands to Device
async def command_device():
    await run(client, discovered_device[1], motor_direction, motor_enable, motor_speed, angle_delta, UUID)

# Stop & Start Button
def on_stop_button_click():
    print("Stop button clicked")
    global motor_enable, angle_delta
    motor_enable = 0
    angle_delta = 0
    run_in_asyncio_thread(command_device())

def on_start_button_click():
    print("Start button clicked")
    global motor_enable
    motor_enable = 1
    run_in_asyncio_thread(command_device())

# Direction Dropdown
def on_direction_change(value):
    global motor_direction
    motor_direction = 1 if value == "Clockwise" else 0

# Send Button
def on_send_button_click():
    global motor_direction, motor_speed, angle_delta, motor_enable
    motor_enable = 1
    print(f"motor_speed: {motor_speed}")
    print(f"angle_delta: {angle_delta}")
    print(f"motor_direction: {motor_direction}")
    print(f"motor_enable: {motor_enable}")
    print("--------")
    run_in_asyncio_thread(command_device())

# CLOSING ACTIONS -------------------------------------
async def disconnect_action():
    await disconnect_from_device(client)

def on_closing():
    run_in_asyncio_thread(disconnect_action())
    shutdown_asyncio_thread()
    app.destroy()
    
    
#------------------------------------- Main Setup -------------------------------------
ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = ctk.CTk()  # create CTk window like you do with the Tk window
app.title("Rotary Table Controller")
app.geometry("800x500")
app.protocol("WM_DELETE_WINDOW", on_closing)
app.resizable(False, False)

#------------------------------------- GUI -------------------------------------
default_font = ("Roboto", 12)

# connected status:
connected_label = ctk.CTkLabel(app, text="Status: Connected", font=default_font)

# Create a device menu
options = []
device_dropdown = ctk.CTkComboBox(app, values=options, state="readonly", font=default_font)
device_dropdown.set("No devices found")  # Set default text
device_dropdown.grid(row=0, column=2, padx=10)

# Create a search button
device_search_button = ctk.CTkButton(app, text="Search", command=on_search_button_click, 
                                     width=12, fg_color="white", hover_color="gray", text_color="black",
                                     font=default_font)
device_search_button.grid(row=0, column=3, padx=10, pady=10)

# Create a connect button
device_connect_button = ctk.CTkButton(app, text="Connect", command=on_connect_button_click, width=15,
                                      font=default_font)
device_connect_button.grid(row=0, column=4, padx=10)

# stop button
device_stop_button = ctk.CTkButton(app, text="Stop", width=100, height=100, corner_radius=25, fg_color="red", 
                                   hover_color="gray", font=default_font, command=on_stop_button_click)
device_stop_button.grid(row=3, column=5, rowspan=2, columnspan=2, padx=10, pady=20)

# start button 
device_start_button = ctk.CTkButton(app, text="Start", width=100, height=50, corner_radius=12, fg_color="green", 
                                   hover_color="gray", font=default_font, command=on_start_button_click)
device_start_button.grid(row=5, column=5, rowspan=2, columnspan=2, padx=10, pady=20)

# controls
def on_command_change(value):
    global angle_delta

    if value == "Constant Speed":
        angle_delta = 0
        angle_step_label.grid_remove()
        angle_step_entry.grid_remove()
        angle_label.grid_remove()
    elif value == "Angle Step":
        angle_delta = int(angle_step_entry.get())
        angle_step_label.grid(row=5, column=0, padx=10)
        angle_step_entry.grid(row=5, column=1)
        angle_label.grid(row=5, column=2)

controls_label = ctk.CTkLabel(app, text="CONTROLS:", font=("Roboto", 16))
controls_label.grid(row=1, column=0, padx=10, columnspan=2)

dir_options = ["Clockwise", "Counter-Clockwise"]
dir_label = ctk.CTkLabel(app, text="Direction:", font=default_font)
dir_label.grid(row=2, column=0, padx=10)
dir_dropdown = ctk.CTkComboBox(app, values=dir_options, state="readonly", command=on_direction_change, font=default_font)
dir_dropdown.set("Clockwise")
dir_dropdown.grid(row=2, column=1, padx=10)

command_options = ["Constant Speed", "Angle Step"]
command_label = ctk.CTkLabel(app, text="Command:", font=default_font)
command_label.grid(row=3, column=0, padx=10)
command_dropdown = ctk.CTkComboBox(app, values=command_options, state="readonly", command=on_command_change, font=default_font)
command_dropdown.set("Constant Speed")
command_dropdown.grid(row=3, column=1, padx=10)

# variable input fields
def on_speed_change(value):
    global motor_speed
    motor_speed = int(value)
    value = speed_slider.get()
    variable_label.configure(text=str(int(value)))

def on_angle_change(value):
    global angle_delta
    angle_delta = int(value)
    value = angle_step_entry.get()
    angle_label.configure(text=str(int(value)))

speed_label = ctk.CTkLabel(app, text="Speed (%):", font=default_font)
speed_label.grid(row=4, column=0)
speed_slider = ctk.CTkSlider(app, from_=1, to=100, command=on_speed_change)
speed_slider.set(50)
speed_slider.grid(row=4, column=1)
variable_label = ctk.CTkLabel(app, text="50", anchor='e', font=default_font)
variable_label.grid(row=4, column=2)

#TODO: add common and buttons
angle_step_label = ctk.CTkLabel(app, text="Step (°):", font=default_font)
angle_step_entry = ctk.CTkSlider(app, from_=1, to=360, command=on_angle_change)
angle_step_entry.set(30)
angle_label = ctk.CTkLabel(app, text="30", anchor='e', font=default_font)


update_button = ctk.CTkButton(app, text="Send Command", width=100, height=50, corner_radius=12, 
                                   hover_color="gray", font=default_font, command=on_send_button_click)
update_button.grid(row=6, column=1, rowspan=1, columnspan=1)

## RUN MAINS -------------------------------------
asyncio_thread = threading.Thread(target=setup_asyncio_thread, daemon=True)
asyncio_thread.start()

app.mainloop()