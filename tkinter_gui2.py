import tkinter as tk
from ttkbootstrap.constants import *
import ttkbootstrap as tb
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

colors = ['blue', 'green', 'red', 'yellow']
legend_labels = ['1-3 koincidencia', '1-4 koincidencia', '2-3 koincidencia', '2-4 koincidencia']

shape = (4, 20)
beutesek = np.zeros(shape)

class PlotUpdater:
    def __init__(self, root, fig, ax, canvas):
        self.root = root
        self.fig = fig
        self.ax = ax
        self.canvas = canvas
        self.continue_update = False

    def generate(self):
        a1 =np.random.randint(2000,size=10)
        a2 =np.random.randint(2000,size=10)
        a3 =np.random.randint(2000,size=10)
        a4 =np.random.randint(2000,size=10)

        histograms ={
            1:a1,
            2:a2,
            3:a3,
            4:a4
        }
        return histograms

    def adatok(self):
        histograms=self.generate()

        for i, (hist_title, histogram) in enumerate(histograms.items()):
            beutesek[i, 0:19] = beutesek[i, 1:20]
            beutesek[i, 19] = np.sum(histogram)
        return beutesek

    def update_plot(self):
        if self.continue_update:
            beutesek = self.adatok()

            # Clear the previous plot
            self.ax.clear()

            for i in range(4):
                self.ax.plot(beutesek[i], color=colors[i], marker='o', linestyle='',label=legend_labels[i])

            self.ax.legend(loc='upper left')
            self.ax.set_ylim([0, 18000])
            self.ax.set_title('Koincidencia mérés')
            self.ax.set_xlabel('Adat')
            self.ax.set_ylabel('Beütések')
            self.ax.set_xticks(range(0, 20))
            self.ax.set_facecolor('dimgray')
            # Draw the updated plot
            self.canvas.draw()

            self.root.after(100, self.update_plot)

    def start_plot(self):
        self.continue_update = True
        self.update_plot()

    def stop_plot(self):
        self.ax.patch.set_facecolor('silver')
        self.canvas.draw()
        self.continue_update = False

# Window beállítás
root = tb.Window(themename="darkly")
root.title("Koincidencia mérés")
#getting screen width and height of display
width= root.winfo_screenwidth() 
height= root.winfo_screenheight()
#setting tkinter window sizea
root.geometry("%dx%d" % (width, height))

frame1=tb.Frame(root,bootstyle="light",height=600,width=50)
frame1.pack(side=LEFT,pady=20,anchor=NW)
frame1['relief'] = 'groove'

#plotolt diagramm beállítás
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_title('Koincidencia mérés')
ax.set_xlabel('Adat')
ax.set_ylabel('Beütések')
ax.set_xticks(range(0, 20))
ax.set_ylim([0, 18000])
ax.set_facecolor("silver")

canvas = FigureCanvasTkAgg(fig, master=root)
#canvas.get_tk_widget().grid(row=0, column=1, rowspan=2, padx=10, pady=10) # Adjust the row and column span as needed
canvas.get_tk_widget().pack(side='top', anchor=NE)
canvas.get_tk_widget().config(background='gray')

plot_updater = PlotUpdater(root, fig, ax, canvas)

label1=tb.Label(frame1,text="Plot",width=20,font=("Arial", 25) )

# Start and Stop buttons
btn_start = tb.Button(frame1, text="Start",bootstyle="success", command=plot_updater.start_plot)
btn_stop = tb.Button(frame1, text="Stop",bootstyle="danger", command=plot_updater.stop_plot)

label1.pack(padx=20, pady=20)
btn_start.pack(padx=20, pady=20)
btn_stop.pack(padx=20, pady=20)

# Futtatjuk a Tkinter event loop-ot
root.mainloop()
