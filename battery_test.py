import tkinter as tk
from header import Header
from channel import Channel
from plotting import Plotting

class BatteryTestApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Battery Test GUI")
        self.root.geometry("900x700")
        self.root.minsize(600, 500)
        self.header = Header(self.root)
        self.plot1 = Plotting(self.root, "Channel 1")
        self.plot2 = Plotting(self.root, "Channel 2")
        self.channel1 = Channel(self.root, "Channel 1", self.plot1)
        self.channel2 = Channel(self.root, "Channel 2", self.plot2)

root = tk.Tk()
app = BatteryTestApp(root)
root.mainloop()