
# Importing necessary libraries
import pyvisa
import time
import matplotlib.pyplot as plt
from datetime import datetime
import signal
import sys
from tkinter import Tk, Label, Text, Scrollbar, Toplevel

#####################################################################################
#####################################################################################
#####################################################################################

#Parameters for battery testing.
# Residual discharge
discharge_method="CR"  # "CC" for constant current discharge, "CR for constant resistance discharge.
Curr_res_dis_ch1=1     #set residual discharge current A.
Volt_res_dis_ch1=6     #set residual discharge cutoff voltage V.
resi_res_dis_ch1=3.9   #set capacity test resistance Ω.


#charging
curr_fir_cha_ch1=0.1   #set charging current A.
volt_fir_cha_ch1=9.3   #set max charging voltage V.
durr_fir_cha_ch1=30    #set charging duration s. (16h = 57600s)

#rest period
rest_period=10         #set rest period duration s.(1h = 3600s)

#capacity test
Curr_cap_dis_ch1=2     #set capacity test current A.
resi_res_dis_ch1=3.9   #set capacity test resistance Ω. (only used on 726-0591-01)
volt_cap_dis_ch1=5.7   #set capacity test cutoff voltage V.

#Parameters for battery testing end.
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################

# Initialize pyvisa tools
rm = pyvisa.ResourceManager()
print(rm.list_resources())

# Initialize instruments
DL1 = rm.open_resource('USB0::0x1AB1::0x0E11::DL3A264200978::INSTR')
psu = rm.open_resource('USB0::0x1AB1::0xA4A8::DP9D264301173::INSTR')

# Initialize a list to store voltage readings and timestamps
voltage_readings = []
timestamps = []

# Create a figure for plotting and set up the plot
plt.ion()  # Turn on interactive mode for live updating of the plot
fig, ax = plt.subplots()
line, = ax.plot([], [], label="Voltage")
ax.set_xlabel('Time (seconds)')
ax.set_ylabel('Voltage (V)')
ax.set_title('CH 1 test')
ax.grid(True)

# Function to update the plot dynamically
def update_plot():
    line.set_xdata(timestamps)
    line.set_ydata(voltage_readings)
    ax.relim()  # Recalculate axis limits
    ax.autoscale_view(True, True, True)  # Automatically adjust the view limits
    plt.draw()
    plt.pause(0.2)

# Function to handle discharging phase
def discharge_phase(current, stop_voltage, cumulative_time, resistance):
    if discharge_method == "CC":  # Constant Current Mode
        DL1.write(":FUNC CURR")  # Set the load to constant current mode (check your device's manual)
        DL1.write(f":CURR {current}")  # Set discharge current
    elif discharge_method == "CR":  # Constant Resistance Mode
        DL1.write(":FUNC RES")  # Set the load to constant resistance mode (check your device's manual)
        DL1.write(f":RES {resistance}")  # Set discharge resistance

    DL1.write(":INP ON")  # Turn on the load

    start_time = time.time()  # Record actual start time for discharge
    start_time_dt = datetime.now()  # Start date/time for discharge phase

    while True:
        dl_voltage = float(DL1.query(":MEAS:VOLT?"))
        voltage_readings.append(dl_voltage)  # Store voltage reading
        elapsed_time = time.time() - start_time  # Calculate elapsed time
        timestamps.append(cumulative_time + elapsed_time)  # Use cumulative time for x-axis

        update_plot()  # Update the plot

        time.sleep(0.2)  # Delay between readings

        if dl_voltage < stop_voltage:
            time.sleep(1)
            DL1.write(":INP OFF")  # Turn off the load
            break  # Exit the loop

    elapsed_time = time.time() - start_time  # Calculate total elapsed time for discharge
    end_time_dt = datetime.now()  # End date/time for discharge phase

    minutes, seconds = divmod(int(elapsed_time), 60)
    print(f"Discharge duration CH1: {minutes} minutes, {seconds} seconds.")

    return elapsed_time, start_time_dt, end_time_dt  # Return duration and start/end times

# Function to handle charging phase
def charge_phase(voltage, current, duration, cumulative_time):
    psu.write(":INST:SEL CH1")
    psu.write(f":VOLT {voltage}")  # Set charge voltage
    psu.write(f":CURR {current}")  # Set charge current
    psu.write(":INST:SEL CH1")
    psu.write(":OUTP ON")  # Turn on the output

    start_time = time.time()  # Record start time for charge
    start_time_dt = datetime.now()  # Start date/time for charge phase

    elapsed_time = 0
    while elapsed_time < duration:
        psu_voltage = float(DL1.query(":MEAS:VOLT?"))
        voltage_readings.append(psu_voltage)  # Store voltage reading
        elapsed_time = time.time() - start_time  # Calculate elapsed time
        timestamps.append(cumulative_time + elapsed_time)  # Use cumulative time for x-axis

        update_plot()  # Update the plot

        time.sleep(0.2)  # Delay between readings
    psu.write(":INST:SEL CH1")
    psu.write(":OUTP OFF")  # Turn off the output
    end_time_dt = datetime.now()  # End date/time for charge phase
    return elapsed_time, start_time_dt, end_time_dt, psu_voltage  # Return duration, start/end times, final voltage

# Proper shutdown procedure (turn off PSU and DL1)
def shutdown(signal, frame):
    print("Shutting down the system CH1...")
    psu.write(":OUTP OFF")  # Turn off PSU
    DL1.write(":INP OFF")  # Turn off DL1
    sys.exit(0)  # Exit the script

# Register the shutdown function for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, shutdown)

# Initial cumulative time in seconds
cumulative_time = 0

# Start time of the script
script_start_time = datetime.now()

# Residual discharge
print("Starting residual discharge CH1...")
residual_discharge_duration, residual_discharge_start, residual_discharge_end = discharge_phase(current=Curr_res_dis_ch1, stop_voltage=Volt_res_dis_ch1, cumulative_time=cumulative_time, resistance=resi_res_dis_ch1)
cumulative_time += residual_discharge_duration  # Update cumulative time

print(f"Initial voltage of the battery: {voltage_readings[0]:.2f} V")

# Pause for settle (not added to cumulative time)
pause_duration = 5
time.sleep(pause_duration)

# First charge
print("Starting first charge CH1...")
charge_duration, charge_start, charge_end, charge_voltage = charge_phase(voltage=volt_fir_cha_ch1, current=curr_fir_cha_ch1, duration=durr_fir_cha_ch1, cumulative_time=cumulative_time)
cumulative_time += charge_duration  # Update cumulative time


# Pause for settle (not added to cumulative time)

print("Starting rest period for CH1...")

# Rest period (continue voltage plotting)
rest_duration = rest_period  # Rest period in seconds
rest_start_time = time.time()

while time.time() - rest_start_time < rest_duration:
    psu_voltage = float(DL1.query(":MEAS:VOLT?"))  # Measure voltage during rest
    voltage_readings.append(psu_voltage)  # Store voltage reading
    elapsed_rest_time = time.time() - rest_start_time
    timestamps.append(cumulative_time + elapsed_rest_time)  # Update timestamps with cumulative + rest elapsed time

    update_plot()  # Update the plot dynamically
    time.sleep(0.1)  # Adjust for desired measurement frequency

# Increment cumulative time by the rest duration after the rest period ends
cumulative_time += rest_duration
print("rest period end. CH1")

# Capacity test
print("Starting capacity test CH1...")
capacity_test_duration, capacity_test_start, capacity_test_end = discharge_phase(current=Curr_cap_dis_ch1, stop_voltage=volt_cap_dis_ch1, cumulative_time=cumulative_time, resistance=resi_res_dis_ch1)
cumulative_time += capacity_test_duration  # Update cumulative time

# Pause for settle (not added to cumulative time)
time.sleep(pause_duration)

# Final charge
print("Starting final charge CH1...")
charge_duration, final_charge_start, final_charge_end, final_charge_voltage = charge_phase(voltage=volt_fir_cha_ch1, current=curr_fir_cha_ch1, duration=durr_fir_cha_ch1, cumulative_time=cumulative_time)

# Results summary
print("Battery test sequence completed for CH1.")

def show_results_in_popup(results):
    # Create a new pop-up window
    root = Tk()  # Main Tkinter window
    root.withdraw()  # Hide the main root window

    popup = Toplevel()  # Create a new top-level window
    popup.title("Test Results")
    popup.geometry("500x400")

    # Add a label for the title
    Label(popup, text="Battery Test Results CH 1", font=("Arial", 16, "bold")).pack(pady=10)

    # Create a text widget with a scrollbar for displaying results
    text_area = Text(popup, wrap="word", font=("Courier", 12))
    text_area.pack(expand=True, fill="both", padx=10, pady=10)

    # Add the results to the text widget
    text_area.insert("1.0", results)
    text_area.configure(state="disabled")  # Make the text area read-only

    # Run the pop-up window
    popup.mainloop()

# Prepare the results string
results_string = f"""
Script start time: {script_start_time.strftime('%Y-%m-%d %H:%M:%S')}

Initial voltage of the battery: {voltage_readings[0]:.2f} V
Residual discharge start time: {residual_discharge_start.strftime('%Y-%m-%d %H:%M:%S')}
Residual discharge end time: {residual_discharge_end.strftime('%Y-%m-%d %H:%M:%S')}
Residual discharge duration: {residual_discharge_duration // 60:.0f}m {residual_discharge_duration % 60:.0f}s

1st charge start time: {charge_start.strftime('%Y-%m-%d %H:%M:%S')}
1st charge end time: {charge_end.strftime('%Y-%m-%d %H:%M:%S')}
Voltage at the end of 1st charge: {charge_voltage:.2f} V

Capacity test start time: {capacity_test_start.strftime('%Y-%m-%d %H:%M:%S')}
Capacity test end time: {capacity_test_end.strftime('%Y-%m-%d %H:%M:%S')}
Capacity test duration: {capacity_test_duration // 60:.0f}m {capacity_test_duration % 60:.0f}s

Final charge start time: {final_charge_start.strftime('%Y-%m-%d %H:%M:%S')}
Final charge end time: {final_charge_end.strftime('%Y-%m-%d %H:%M:%S')}
Voltage at the end of final charge: {final_charge_voltage:.2f} V
"""

# Call the pop-up function with results
show_results_in_popup(results_string)

# Final plot display
plt.ioff()  # Turn off interactive mode to stop updates
plt.show()

psu.write(":INST:SEL CH1")
psu.write(f":VOLT {volt_fir_cha_ch1}")  # Set charge voltage
psu.write(f":CURR {0}")  # Set charge current