import tkinter as tk
from matplotlib.animation import FuncAnimation
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from test_sequence import test_sequences
import tkinter.messagebox as MessageBox
from datetime import datetime
from header import Header
import threading
import subprocess
import collections
from multiprocessing import Process
import time

from matplotlib.animation import FuncAnimation


class BatteryTestApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Battery Test GUI")
        self.root.geometry("900x700")
        self.root.minsize(600, 500)
        self.header = Header(self.root)
        #self.setup_header()
        #self.setup_channels()
        #self.setup_plots()
        #self.voltage_data = collections.deque(maxlen=1000000)
        #self.time_data = collections.deque(maxlen=1000000)
        #self.ani = None

    def setup_channels(self):
        self.channels_frame = tk.Frame(self.root)
        self.channels_frame.pack(fill=tk.BOTH, pady=20, padx=10)
        self.channels_frame.columnconfigure(0, weight=1, uniform="equal")
        self.channels_frame.columnconfigure(1, weight=1, uniform="equal")
        self.create_channel_widgets("Channel 1", self.channels_frame, column=0)
        self.create_channel_widgets("Channel 2", self.channels_frame, column=1)

    def setup_plots(self):
        self.plots_frame = tk.Frame(self.root)
        self.plots_frame.pack(fill=tk.BOTH, pady=20, padx=10)
        self.plots_frame.columnconfigure(0, weight=1)
        self.plots_frame.columnconfigure(1, weight=1)
        self.channel1_canvas = FigureCanvasTkAgg(plt.figure(figsize=(5, 4)), master=self.plots_frame)
        self.channel1_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10)
        self.channel2_canvas = FigureCanvasTkAgg(plt.figure(figsize=(5, 4)), master=self.plots_frame)
        self.channel2_canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=10)

        self.fig1 = self.channel1_canvas.figure
        self.ax1 = self.fig1.add_subplot(111)
        self.ax1.set_title("Voltage Profile")
        self.ax1.set_ylabel("Voltage (V)")

        self.fig2 = self.channel2_canvas.figure
        self.ax2 = self.fig2.add_subplot(111)
        self.ax2.set_title("Voltage Profile")
        self.ax2.set_ylabel("Voltage (V)")

        self.line1 = self.ax1.plot([], [])
        self.line2 = self.ax2.plot([], [])

    def create_channel_widgets(self, channel_name, parent_frame, column):
        channel_frame = tk.Frame(parent_frame)
        channel_frame.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        parent_frame.grid_rowconfigure(0, weight=1)

        tk.Label(channel_frame, text=channel_name).pack()
        tk.Label(channel_frame, text="Select Battery").pack()

        battery_options = ['', 'Manual'] + list(test_sequences.keys())
        battery_combobox = ttk.Combobox(channel_frame, values=battery_options)
        battery_combobox.pack(fill=tk.X)
        battery_combobox.bind("<<ComboboxSelected>>", lambda event, combobox=battery_combobox, channel=channel_name: self.update_sequence(event, combobox, channel))
        setattr(self, f"{channel_name.lower()}_battery_combobox", battery_combobox)

        sequence_frame = tk.Frame(channel_frame)
        sequence_frame.pack(fill=tk.X, anchor='w')

        sequence_label = tk.Label(sequence_frame, text="", justify="left", anchor='w')
        setattr(self, f"{channel_name.lower()}_sequence_label", sequence_label)
        sequence_label.pack(fill=tk.X, anchor='w')

        input_frame = tk.Frame(channel_frame)
        input_frame.pack(fill=tk.X)
        for field in ["WO", "WC", "S/N", "3-Letter Code"]:
            self.create_input_field(input_frame, channel_name, field)

        button_frame = tk.Frame(channel_frame)
        button_frame.pack(pady=10, fill=tk.X)
        start_button = tk.Button(button_frame, text=f"Start Test {channel_name}", command=lambda: self.start_test(channel_name))
        start_button.pack(side=tk.LEFT, padx=5, fill=tk.X)
        stop_button = tk.Button(button_frame, text=f"Stop Test {channel_name}", command=lambda: self.stop_test(channel_name))
        stop_button.pack(side=tk.LEFT, padx=5, fill=tk.X)
        setattr(self, f"{channel_name.lower()}_start_button", start_button)
        setattr(self, f"{channel_name.lower()}_stop_button", stop_button)

        date_label = tk.Label(channel_frame, text="Test Started on: Not Started")
        setattr(self, f"{channel_name.lower()}_date_label", date_label)
        date_label.pack(fill=tk.X)

    def create_input_field(self, parent_frame, channel_name, field_name):
        field_frame = tk.Frame(parent_frame)
        field_frame.pack(side=tk.LEFT, padx=5, fill=tk.X)
        tk.Label(field_frame, text=field_name).pack(side=tk.LEFT)
        entry = tk.Entry(field_frame, width=10)
        entry.pack(side=tk.LEFT, fill=tk.X)
        setattr(self, f"{channel_name.lower()}_{field_name.lower().replace('-', '_')}_entry", entry)

    def update_sequence(self, event, combobox, channel_name):
        selected_battery = combobox.get()
        sequence_label = getattr(self, f"{channel_name.lower()}_sequence_label")
        if selected_battery == 'Manual':
            sequence_label.config(text="")
            self.show_manual_options(channel_name)
        else:
            self.hide_manual_options(channel_name)
            sequence = test_sequences.get(selected_battery, [])
            sequence_text = "\n".join(sequence) if sequence else "No sequence found"
            sequence_label.config(text=sequence_text, anchor='w', justify='left')

    def show_manual_options(self, channel_name):
        manual_frame = getattr(self, f"{channel_name.lower()}_manual_frame", None)
        if manual_frame:
            manual_frame.destroy()
        manual_frame = tk.Frame(getattr(self, f"{channel_name.lower()}_battery_combobox").master)
        manual_frame.pack(fill=tk.X)
        setattr(self, f"{channel_name.lower()}_manual_frame", manual_frame)

        fields = [
            ("Battery P/N", None),
            ("Battery S/N", None),
            ("Residual Discharge", ["CC", "CR"]),
            ("Discharge Value", 'numeric'),
            ("Cutoff Voltage", 'numeric'),
            ("Charging Time (hours)", 'numeric'),
            ("Rest Time (hours)", 'numeric'),
            ("Capacity Test Current", 'numeric'),
            ("Maximum Charging Voltage", 'numeric'),
            ("Capacity Test Cutoff Voltage", 'numeric'),
            ("Final Charge Time (hours)", 'numeric')
        ]

        for field, input_type in fields:
            field_frame = tk.Frame(manual_frame)
            field_frame.pack(fill=tk.X)
            tk.Label(field_frame, text=field, width=25, anchor="w").pack(side=tk.LEFT)
            if input_type == ["CC", "CR"]:
                ttk.Combobox(field_frame, values=input_type, width=15).pack(side=tk.LEFT, fill=tk.X)
            else:
                vcmd = (self.root.register(lambda action, value, type=input_type: self.on_validate(action, value, type)), '%d', '%P')
                tk.Entry(field_frame, width=15, validate="key", validatecommand=vcmd).pack(side=tk.LEFT, fill=tk.X)

    def hide_manual_options(self, channel_name):
        manual_frame = getattr(self, f"{channel_name.lower()}_manual_frame", None)
        if manual_frame:
            manual_frame.destroy()
            delattr(self, f"{channel_name.lower()}_manual_frame")

    def validate_input(self, value, input_type):
        if input_type == 'numeric':
            return value.replace('.', '', 1).isdigit()
        elif input_type == 'cc_cr':
            return value in ['CC', 'CR']
        return True

    def on_validate(self, action, value, input_type):
        if action == '1':  # insert
            return self.validate_input(value, input_type)
        return True

    def validate_manual_inputs(self, widgets):
        input_types = [None, None, ["CC", "CR"]] + ['numeric'] * 8
        for widget, input_type in zip(widgets, input_types):
            value = widget.get()
            if input_type == ["CC", "CR"] and value not in ["CC", "CR"]:
                return False
            elif input_type == 'numeric' and not value.replace('.', '', 1).isdigit():
                return False
        return True

    def start_test(self, channel_name):
        # Check if the test is already running on the respective channel
        if getattr(self, f"{channel_name.lower()}_test_running", False):
            return  # Prevent starting the test if it's already running

        battery_combobox = getattr(self, f"{channel_name.lower()}_battery_combobox")
        selected_battery = battery_combobox.get()
        if not selected_battery:
            MessageBox.showerror("Error", "Please select a battery before starting the test.")
            return

        # Check if all mandatory fields (card info) are filled
        mandatory_fields = ["WO", "WC", "S/N", "3-Letter Code"]
        for field in mandatory_fields:
            entry = getattr(self, f"{channel_name.lower()}_{field.lower().replace('-', '_')}_entry")
            if not entry.get():
                MessageBox.showerror("Error", f"Please fill in the {field} field before starting the test.")
                return

        # Check if manual fields are filled and valid if 'Manual' battery is selected
        if selected_battery == 'Manual':
            manual_frame = getattr(self, f"{channel_name.lower()}_manual_frame", None)
            if manual_frame:
                widgets = [frame.winfo_children()[-1] for frame in manual_frame.winfo_children()]
                if any(not w.get() for w in widgets):
                    MessageBox.showerror("Error", "Please fill in all manual input fields before starting the test.")
                    return
                if not self.validate_manual_inputs(widgets):
                    MessageBox.showerror("Error", "Invalid input in manual fields. Please check and try again.")
                    return

                # Lock input fields during testing
                self.lock_fields(channel_name, widgets)

        # Lock input fields during testing (always lock card info fields)
        self.lock_fields(channel_name)

        if getattr(self, f"{channel_name.lower()}_test_running", False):
            return

        # Set test running state
        setattr(self, f"{channel_name.lower()}_test_running", True)

        # Disable start button and battery combobox
        start_button = getattr(self, f"{channel_name.lower()}_start_button")
        start_button.config(state=tk.DISABLED)
        battery_combobox.config(state='disabled')

        # Record the test start date and update label
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_label = getattr(self, f"{channel_name.lower()}_date_label")
        date_label.config(text=f"Test Started on: {current_date}")
        setattr(self, f"{channel_name.lower()}_start_date", current_date)

        self.start_time = time.time()

        # Call the function to turn on the PSU for the respective channel
        if channel_name == "Channel 1":
            from CH_1_test import start_test
            start_test()

        elif channel_name == "Channel 2":
            from CH_2_test import start_test
            start_test()

        # Print the test sequence for debugging or reference
        print(f"Test Sequence for {channel_name}: {test_sequences.get(selected_battery, [])}")

    def start_plotting(self):
        self.voltage_data.clear()
        self.time_data.clear()
        if (channel_name == "Channel 1"):
            self.ani = FuncAnimation(self.fig1, self.update_plot, interval=1000)
        elif (channel_name == "Channel 2"):
            self.ani = FuncAnimation(self.fig2, self.update_plot, interval=1000)

    def update_plot(self, frame):
        voltage = float(self.get_voltage.reading().strip())

        timestamp = time.time() - self.start_time

        self.voltage_data.append(voltage)
        self.time_data.append(timestamp)

        if (channel_name == "Channel 1"):
            self.line1.set_data(self.time_data, self.voltage_data)
            self.ax1.relim()
            self.ax1.autoscale_view()
            return self.line1

        elif(channel_name == "Channel 2"):
            self.line2.set_data(self.time_data, self.voltage_data)
            self.ax2.relim()
            self.ax2.autoscale_view()
            return self.line2

    def get_voltage_reading(self):
        return #reikia grazinti voltage reading

    def lock_fields(self, channel_name, manual_widgets=None):
        """Lock the fields during the test."""
        # Lock the card info fields
        for field in ["WO", "WC", "S/N", "3-Letter Code"]:
            entry = getattr(self, f"{channel_name.lower()}_{field.lower().replace('-', '_')}_entry")
            entry.config(state='disabled')

        # Lock manual input fields if present
        if manual_widgets:
            for widget in manual_widgets:
                widget.config(state='disabled')


    def stop_test(self, channel_name):
        if MessageBox.askyesno("Stop Test", f"Are you sure you want to stop the test on {channel_name}?"):
            # Unlock input fields after testing
            for field in ["WO", "WC", "S/N", "3-Letter Code"]:
                entry = getattr(self, f"{channel_name.lower()}_{field.lower().replace('-', '_')}_entry")
                entry.config(state='normal')

            # Unlock manual input fields if the battery was manual
            selected_battery = getattr(self, f"{channel_name.lower()}_battery_combobox").get()
            if selected_battery == 'Manual':
                manual_frame = getattr(self, f"{channel_name.lower()}_manual_frame", None)
                if manual_frame:
                    widgets = [widget for frame in manual_frame.winfo_children() for widget in frame.winfo_children()]
                    for widget in widgets:
                        widget.config(state='normal')

            # Re-enable Start Test button and Battery Combobox
            start_button = getattr(self, f"{channel_name.lower()}_start_button")
            start_button.config(state=tk.NORMAL)

            battery_combobox = getattr(self, f"{channel_name.lower()}_battery_combobox")
            battery_combobox.config(state='normal')

            print(f"Stopping test on {channel_name}. Disconnecting PSU and load.")

            # Set termination flag for the child process (this will be checked in the child process)
            with open(f"{channel_name.lower()}_termination_flag.txt", "w") as flag_file:
                flag_file.write("TERMINATE")

            # Call the function to turn off the PSU for the respective channel
            if channel_name == "Channel 1":
                from CH_1_test import stop_test
                stop_test()
            elif channel_name == "Channel 2":
                from CH_2_test import stop_test
                stop_test()

            # Disable test running flag
            setattr(self, f"{channel_name.lower()}_test_running", False)

        else:
            print(f"Test on {channel_name} continues.")


root = tk.Tk()
app = BatteryTestApp(root)
root.mainloop()