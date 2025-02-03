import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as MessageBox
from datetime import datetime
from test_sequence import test_sequences
import time

class Channel:
    def __init__(self, root, channel_name, plotting):
        self.root = root
        self.channel_name = channel_name
        self.plotting = plotting
        self.setup_channel()

    def setup_channel(self):
        self.channel_frame = tk.Frame(self.root)
        self.channel_frame.pack(fill=tk.BOTH, pady=20, padx=10, side=tk.LEFT, expand=True)

        tk.Label(self.channel_frame, text=self.channel_name).pack()
        tk.Label(self.channel_frame, text="Select Battery").pack()

        battery_options = ['', 'Manual'] + list(test_sequences.keys())
        self.battery_combobox = ttk.Combobox(self.channel_frame, values=battery_options)
        self.battery_combobox.pack(fill=tk.X)
        self.battery_combobox.bind("<<ComboboxSelected>>", self.update_sequence)

        self.sequence_label = tk.Label(self.channel_frame, text="", justify="left", anchor="w")
        self.sequence_label.pack(fill=tk.X, anchor='w')

        self.input_frame = tk.Frame(self.channel_frame)
        self.input_frame.pack(fill=tk.X)
        for field in ["WO", "WC", "S/N", "3-Letter Code"]:
            self.create_input_field(field)

        self.button_frame = tk.Frame(self.channel_frame)
        self.button_frame.pack(pady=10, fill=tk.X)
        self.start_button = tk.Button(self.button_frame, text=f"Start Test {self.channel_name}", command=self.start_test)
        self.start_button.pack(side=tk.LEFT, padx=5, fill=tk.X)
        self.stop_button = tk.Button(self.button_frame, text=f"Stop Test {self.channel_name}", command=self.stop_test)
        self.stop_button.pack(side=tk.LEFT, padx=5, fill=tk.X)

        self.date_label = tk.Label(self.channel_frame, text="Test Started on: Not Started")
        self.date_label.pack(fill=tk.X)

    def create_input_field(self, field_name):
        field_frame = tk.Frame(self.input_frame)
        field_frame.pack(side=tk.LEFT, padx=5, fill=tk.X)
        tk.Label(field_frame, text=field_name).pack(side=tk.LEFT)
        entry = tk.Entry(field_frame, width=10)
        entry.pack(side=tk.LEFT, fill=tk.X)
        setattr(self, f"{field_name.lower().replace('-', '_')}_entry", entry)

    def update_sequence(self, event):
        selected_battery = self.battery_combobox.get()
        if selected_battery == 'Manual':
            self.sequence_label.config(text="")
            self.show_manual_options()
        else:
            self.hide_manual_options()
            sequence = test_sequences.get(selected_battery, [])
            sequence_text = "\n".join(sequence) if sequence else "No sequence found"
            self.sequence_label.config(text=sequence_text, anchor='w', justify='left')

    def show_manual_options(self):
        self.manual_frame = tk.Frame(self.channel_frame)
        self.manual_frame.pack(fill=tk.X)

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
            field_frame = tk.Frame(self.manual_frame)
            field_frame.pack(fill=tk.X)
            tk.Label(field_frame, text=field, width=25, anchor="w").pack(side=tk.LEFT)
            if input_type == ["CC", "CR"]:
                ttk.Combobox(field_frame, values=input_type, width=15).pack(side=tk.LEFT, fill=tk.X)
            else:
                vcmd = (
                self.root.register(lambda action, value, type=input_type: self.on_validate(action, value, type)), '%d',
                '%P')
                tk.Entry(field_frame, width=15, validate="key", validatecommand=vcmd).pack(side=tk.LEFT, fill=tk.X)

    def hide_manual_options(self):
        if hasattr(self, 'manual_frame'):
            self.manual_frame.destroy()
            delattr(self, 'manual_frame')

    def on_validate(self, action, value, input_type):
        if action == '1':  # insert
            return self.validate_input(value, input_type)
        return True

    def validate_input(self, value, input_type):
        if input_type == 'numeric':
            return value.replace('.', '', 1).isdigit()
        elif input_type == 'cc_cr':
            return value in ['CC', 'CR']
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
            self.plotting.start_plotting()

        elif channel_name == "Channel 2":
            from CH_2_test import start_test
            start_test()
            self.plotting.start_plotting()

        # Print the test sequence for debugging or reference
        print(f"Test Sequence for {channel_name}: {test_sequences.get(selected_battery, [])}")

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