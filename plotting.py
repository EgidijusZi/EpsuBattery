import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import tkinter as tk
import collections

class Plotting:
    def __init__(self, root, channel_name):
        self.root = root
        self.channel_name = channel_name
        self.voltage_data = collections.deque(maxlen=1000)
        self.time_data = collections.deque(maxlen=1000)
        self.ani = None
        self.setup_plot()

    def setup_plot(self):
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, pady=20, padx=10, side=tk.LEFT, expand=True)

        self.fig = plt.figure(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"Voltage Profile - {self.channel_name}" )
        self.ax.set_ylabel("Voltage (V)")
        self.ax.set_xlabel("Time (s)")

        self.line, = self.ax.plot([], [])
        self.ax.legend()

    def start_plotting(self):
        if self.ani is None:
            self.ani = FuncAnimation(self.fig, self.update_plot, interval=1000, blit=True)

    def update_plot(self, voltage_data, time_data):
        self.line.set_data(time_data, voltage_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()