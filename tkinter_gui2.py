import tkinter as tk
from tkinter import ttk
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import threading

from forgato import *
from time_controller import *


# time_controller csatlakozás
tc, DEFAULT_ACQUISITION_DURATION, bin_width, DEFAULT_BIN_COUNT, DEFAULT_HISTOGRAMS = time_controller_csatlakozas()
# ------

# forgato csatlakozas
s_no1 = "55290504"
s_no2 = "55290814"
device_1 = forgato_csatlakozas(s_no1, s_no2)
device_2 = forgato_csatlakozas(s_no2, s_no1)






# -------------


# Define dark theme colors
bg_color = '#1E1E1E'  # Dark gray
fg_color = '#D4D4D4'  # Light gray
highlight_color = '#2E2E2E'  # Darker gray
primary_color = '#282828'  # Slightly lighter than bg_color
secondary_color = '#333333'  # Slightly darker than bg_color
action_color = '#007ACC'  # Blue
kek = "#0000ff"
zold = "#008000"
piros = "#ff0000"
sarga = "#ffff00"

colors = ['blue', 'green', 'red', 'yellow']
legend_labels = ['1-3 koincidencia', '1-4 koincidencia', '2-3 koincidencia', '2-4 koincidencia']

shape = (4, 20)
beutesek = np.zeros(shape)

utolso = [0, 0, 0, 0]


class PlotUpdater:
    def __init__(self, window, fig, ax, canvas):
        self.window = window
        self.fig = fig
        self.ax = ax
        self.canvas = canvas
        self.continue_update = False
        self.plot_1_3 = tk.BooleanVar()
        self.plot_1_4 = tk.BooleanVar()
        self.plot_2_3 = tk.BooleanVar()
        self.plot_2_4 = tk.BooleanVar()
        self.thread = None
        #global device_1
        #global device_2

    def destroy(self):
        if self.thread is not None:
            if self.thread.is_alive():
                self.continue_update = False
                self.thread.join()

    def generate(self):

        # Ha van tc
        histograms = acquire_histograms(
            tc, DEFAULT_ACQUISITION_DURATION, bin_width, DEFAULT_BIN_COUNT, DEFAULT_HISTOGRAMS
        )
        # ----------

        # Ha nincs tc
        # a1 = np.random.randint(2000, size=10)
        # a2 = np.random.randint(2000, size=10)
        # a3 = np.random.randint(2000, size=10)
        # a4 = np.random.randint(2000, size=10)
        
        # histograms = {
        #     1: a1,
        #     2: a2,
        #     3: a3,
        #     4: a4
        # }
        # -----------
        return histograms

    def adatok(self):
        histograms = self.generate()

        for i, (hist_title, histogram) in enumerate(histograms.items()):
            beutesek[i, 0:19] = beutesek[i, 1:20]
            beutesek[i, 19] = np.sum(histogram)
        return beutesek

    def utolso_beutes(self, beutesek):
        global utolso
        for i in range(4):
            utolso[i] = int(beutesek[i][19])
        return

    def update_plot(self):
        if self.continue_update:
            beutesek = self.adatok()
            self.utolso_beutes(beutesek)
            # Clear the previous plot
            self.ax.clear()

            for i in range(4):
                if i == 0 and self.plot_1_3.get():
                    self.ax.plot(beutesek[i], color=colors[i], marker='o', linestyle='', label=legend_labels[i])
                    beutes_label1.config(text=utolso[0])
                elif i == 1 and self.plot_1_4.get():
                    self.ax.plot(beutesek[i], color=colors[i], marker='o', linestyle='', label=legend_labels[i])
                    beutes_label2.config(text=utolso[1])
                elif i == 2 and self.plot_2_3.get():
                    self.ax.plot(beutesek[i], color=colors[i], marker='o', linestyle='', label=legend_labels[i])
                    beutes_label3.config(text=utolso[2])
                elif i == 3 and self.plot_2_4.get():
                    self.ax.plot(beutesek[i], color=colors[i], marker='o', linestyle='', label=legend_labels[i])
                    beutes_label4.config(text=utolso[3])

            self.ax.legend(loc='upper left')
            self.ax.set_ylim([0, 18000])
            self.ax.set_title('Koincidencia mérés')
            self.ax.set_xlabel('Adat')
            self.ax.set_ylabel('Beütések')
            self.ax.set_xticks(range(0, 20))
            self.ax.set_facecolor(bg_color)
            self.ax.grid(color=highlight_color)
            # Draw the updated plot
            self.canvas.draw()

            self.window.after(100, self.update_plot)

    def update_plot_thread_func(self):
        while self.continue_update:
            self.update_plot()

    def start_plot(self):
        if not self.continue_update:
            beutes_label1.config(text=0)
            beutes_label2.config(text=0)
            beutes_label3.config(text=0)
            beutes_label4.config(text=0)
            self.continue_update = True
            self.thread = threading.Thread(target=self.update_plot_thread_func)
            self.thread.start()

    def stop_plot(self):
        if self.continue_update:
            self.ax.patch.set_facecolor(primary_color)
            self.ax.grid(color=highlight_color)
            self.canvas.draw()
            self.continue_update = False


# Window beállítás
window = tk.Tk()

window.title("Koincidencia mérés")
window.configure(background=primary_color)

window.rowconfigure(0, minsize=600, weight=1)
window.columnconfigure(0, minsize=600, weight=1)
window.columnconfigure(1, minsize=800, weight=1)


class Plot_frame(tk.Frame):
    def __init__(self, root):
        self.plot_updater = None
        super().__init__(master=root, background=primary_color)

    def destroy(self):
        if self.plot_updater is not None:
            self.plot_updater.destroy()
        super().destroy()


# Framek
plot_frame = Plot_frame(window)

# Tabok
notebook = ttk.Notebook(window)

tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)


notebook.add(tab1, text="Plotolás")
notebook.add(tab2, text="Polarizáció kontroller")
notebook.add(tab3, text="Bell-mérés")

notebook.grid(row=0, column=0, sticky="news")

# Plotolás tab-->

# plotolt diagramm beállítás-----------------------------
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_title('Koincidencia mérés')
ax.set_xlabel('Adat')
ax.set_ylabel('Beütések')
ax.set_xticks(range(0, 20))
ax.set_ylim([0, 18000])
ax.set_facecolor(bg_color)
ax.grid(color=highlight_color)

canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
canvas.get_tk_widget().config(background=primary_color)
plot_frame.plot_updater = PlotUpdater(window, fig, ax, canvas)

frame1 = tk.Frame(tab1, relief=tk.GROOVE, bd=2, width=600)
frame2 = tk.Frame(tab1, relief=tk.GROOVE, bd=2, width=600)
frame3 = tk.Frame(tab1, relief=tk.GROOVE, bd=2, width=600)
frame4 = tk.Frame(tab1, relief=tk.GROOVE, bd=2, width=600)


# Start és Stop
label1 = tk.Label(frame1, text="Plot:", width=20, height=5, font=('Times New Roman', 15, 'bold'), foreground="Black")
btn_start = tk.Button(frame1, text="Start", background=action_color, width=15, height=5, foreground=fg_color,
                      command=plot_frame.plot_updater.start_plot, cursor="hand2")
btn_stop = tk.Button(frame1, text="Stop", background=action_color, width=15, height=5, foreground=fg_color,
                     command=plot_frame.plot_updater.stop_plot, cursor="hand2")

label1.grid(row=0, column=0, sticky="news")
btn_start.grid(row=0, column=1, sticky="news", padx=2)
btn_stop.grid(row=0, column=2, sticky="news")

frame1.grid(row=0, column=0, sticky="nws", pady=5)
frame2.grid(row=1, column=0, sticky="nws", pady=5)
frame3.grid(row=2, column=0, sticky="nws", pady=5)
frame4.grid(row=3, column=0, sticky="nws", pady=5)



# Frame2--------
# Checkboxok
cb_1_3 = tk.Checkbutton(frame2, text='1-3', variable=plot_frame.plot_updater.plot_1_3, font=('Times New Roman', 15),
                        onvalue=True, offvalue=False, width=4, cursor="hand2")
cb_1_4 = tk.Checkbutton(frame2, text='1-4', variable=plot_frame.plot_updater.plot_1_4, font=('Times New Roman', 15),
                        onvalue=True, offvalue=False, width=4, cursor="hand2")
cb_2_3 = tk.Checkbutton(frame2, text='2-3', variable=plot_frame.plot_updater.plot_2_3, font=('Times New Roman', 15),
                        onvalue=True, offvalue=False, width=4, cursor="hand2")
cb_2_4 = tk.Checkbutton(frame2, text='2-4', variable=plot_frame.plot_updater.plot_2_4, font=('Times New Roman', 15),
                        onvalue=True, offvalue=False, width=4, cursor="hand2")

label2 = tk.Label(frame2, text="Koincidenciák:", width=20, font=('Times New Roman', 15, 'bold'), foreground="Black")

# Utolsó beütés
beutes_label1 = tk.Label(frame2, text=utolso[0], width=5, font=('Times New Roman', 15), foreground="Black")
beutes_label2 = tk.Label(frame2, text=utolso[1], width=5, font=('Times New Roman', 15), foreground="Black")
beutes_label3 = tk.Label(frame2, text=utolso[2], width=5, font=('Times New Roman', 15), foreground="Black")
beutes_label4 = tk.Label(frame2, text=utolso[3], width=5, font=('Times New Roman', 15), foreground="Black")

beutes_label1_dot = tk.Label(frame2, text="●", width=5, font=('Times New Roman', 15), foreground=kek)
beutes_label2_dot = tk.Label(frame2, text="●", width=5, font=('Times New Roman', 15), foreground=zold)
beutes_label3_dot = tk.Label(frame2, text="●", width=5, font=('Times New Roman', 15), foreground=piros)
beutes_label4_dot = tk.Label(frame2, text="●", width=5, font=('Times New Roman', 15), foreground=sarga)

label2.grid(rowspan=3, column=0, sticky="news")
cb_1_3.grid(row=0, column=1, sticky="news", padx=5)
cb_1_4.grid(row=0, column=2, sticky="news", padx=5)
cb_2_3.grid(row=0, column=3, sticky="news", padx=5)
cb_2_4.grid(row=0, column=4, sticky="news", padx=5)

beutes_label1.grid(row=1, column=1, sticky="news")
beutes_label2.grid(row=1, column=2, sticky="news")
beutes_label3.grid(row=1, column=3, sticky="news")
beutes_label4.grid(row=1, column=4, sticky="news")

beutes_label1_dot.grid(row=2, column=1, sticky="news")
beutes_label2_dot.grid(row=2, column=2, sticky="news")
beutes_label3_dot.grid(row=2, column=3, sticky="news")
beutes_label4_dot.grid(row=2, column=4, sticky="news")

# --------------------
szog1 = 0
szog2 = 0
forgato_szog1 = tk.StringVar()
forgato_szog2 = tk.StringVar()


def set_forgato1():
    global szog1
    global forgatas1
    global minimalizalas

    try:
        if not (forgatas1 or minimalizalas):
            x = re.split(',|\.', forgato_szog1.get())
            if len(x) == 1:
                szog1 = float(x[0])
            else:
                szog1 = int(x[0]) + int(x[1]) / (10 ** len(x[1]))
    except:
        szog1 = 0
    forgato_ertek1.config(text=szog1)
    # beállítja a forgatót

    x = threading.Thread(target=move_forgato, args=[device_1, szog1])
    x.start()
    #move_forgato(device_1,szog1)


def set_forgato2():
    global szog2
    global forgatas2
    global minimalizalas


    try:
        if not (forgatas2 or minimalizalas):
            x = re.split(',|\.', forgato_szog2.get())
            if len(x) == 1:
                szog2 = float(x[0])
            else:
                szog2 = int(x[0]) + int(x[1]) / (10 ** len(x[1]))
    except:
        szog2 = 0
    forgato_ertek2.config(text=szog2)
    # beállítja a forgatót

    x = threading.Thread(target=move_forgato, args=[device_2, szog2])
    x.start()
    #move_forgato(device_2,szog2)


forgatas1=False
forgatas2=False

minimalizalas=False

def set_korbe_forgatas1():
    global szog1
    global forgatas1
    forgatas1 = not forgatas1
    if forgatas1:
        forgato_forgatas1.config(text="Megállítás")
    else:
        forgato_forgatas1.config(text="Forgatás")
    while forgatas1:
        set_forgato1()
        time.sleep(1)
        szog1+=10

def set_korbe_forgatas2():
    global szog2
    global forgatas2
    forgatas2 = not forgatas2
    if forgatas2:
        forgato_forgatas2.config(text="Megállítás")
    else:
        forgato_forgatas2.config(text="Forgatás")
    while forgatas2:
        set_forgato2()
        time.sleep(1)
        szog2+=10


minimalizalando_value = tk.IntVar()  # Változó a kiválasztott minimalizálandó érték tárolására

    
def minimum_kereses_forgato1():
    global szog1
    global forgatas1
    global utolso
    global minimalizalando_value
    global minimalizalas



    min_val=minimalizalando_value.get()
    minimalizalas = True
    minszog=szog1
    minbeut=utolso[min_val-1]

    forgato_minimalizalasa1.config(text="...")
    fokonkent=5
    k=int(180/fokonkent)    
    for i in range(k):
        szog1+=fokonkent
        set_forgato1()
        time.sleep(1)
        beutes = utolso[min_val-1]
        if( beutes < minbeut ):
            minszog=szog1
            minbeut=beutes
    
    szog1=minszog
    set_forgato1()
    time.sleep(1)
    forgato_minimalizalasa1.config(text="Beállítás 1.")
    minimalizalas = False

    

def minimum_kereses_forgato2():
    global szog2
    global forgatas2
    global utolso
    global minimalizalando_value
    global minimalizalas

    min_val=minimalizalando_value.get()
    minimalizalas = True
    minszog=szog2
    minbeut=utolso[min_val-1]

    forgato_minimalizalasa2.config(text="...")
    fokonkent=5
    k=int(180/fokonkent)    
    for i in range(k):
        szog2+=fokonkent
        set_forgato2()
        time.sleep(1)
        beutes = utolso[min_val-1]
        if( beutes < minbeut ):
            minszog=szog2
            minbeut=beutes
    
    szog2=minszog
    set_forgato2()
    time.sleep(1)
    forgato_minimalizalasa2.config(text="Beállítás 2.")
    minimalizalas = False




# Frame3
label3 = tk.Label(frame3, text="Forgató beállítás:", width=20, font=('Times New Roman', 15, 'bold'), foreground="Black")

forgato_cim1 = tk.Label(frame3, text="1.", width=10, font=('Times New Roman', 15), foreground="Black")
forgato_box1 = tk.Entry(frame3, width=5, textvariable=forgato_szog1, font=('Times New Roman', 15), foreground="Black",
                        justify='center')
forgato_set1 = tk.Button(frame3, width=5, text="Set", background=action_color, foreground=fg_color,
                         command=set_forgato1, cursor="hand2")
forgato_ertek1 = tk.Label(frame3, width=10, text=szog1, font=('Times New Roman', 15), foreground="Black")
forgato_forgatas1 = tk.Button(frame3, width=5, text="Forgatás", background=action_color, foreground=fg_color,command=lambda: threading.Thread(target=set_korbe_forgatas1).start(),
                              cursor="hand2")

forgato_cim2 = tk.Label(frame3, text="2.", width=10, font=('Times New Roman', 15), foreground="Black")
forgato_box2 = tk.Entry(frame3, width=5, textvariable=forgato_szog2, font=('Times New Roman', 15), foreground="Black",
                        justify='center')
forgato_set2 = tk.Button(frame3, width=5, text="Set", background=action_color, foreground=fg_color,
                         command=set_forgato2, cursor="hand2")
forgato_ertek2 = tk.Label(frame3, width=10, text=szog1, font=('Times New Roman', 15), foreground="Black")
forgato_forgatas2 = tk.Button(frame3, width=5, text="Forgatás", background=action_color, foreground=fg_color,command=lambda: threading.Thread(target=set_korbe_forgatas2).start(),
                              cursor="hand2")

label3.grid(rowspan=4, column=0, sticky="news")

forgato_cim1.grid(row=0, column=1, columnspan=2, sticky="news")
forgato_box1.grid(row=1, column=1, sticky="news")
forgato_set1.grid(row=1, column=2, sticky="news")
forgato_ertek1.grid(row=2, column=1, columnspan=2, sticky="news")
forgato_forgatas1.grid(row=3, column=1, columnspan=2, sticky="news")

forgato_cim2.grid(row=0, column=3, columnspan=2, sticky="news")
forgato_box2.grid(row=1, column=3, sticky="news")
forgato_set2.grid(row=1, column=4, sticky="news")
forgato_ertek2.grid(row=2, column=3, columnspan=2, sticky="news")
forgato_forgatas2.grid(row=3, column=3, columnspan=2, sticky="news")

# -----------------------




# Frame 4


# Rádiógombok létrehozása
rb_1 = tk.Radiobutton(frame4, text='1', variable=minimalizalando_value, value=1, font=('Times New Roman', 15), cursor="hand2")
rb_2 = tk.Radiobutton(frame4, text='2', variable=minimalizalando_value, value=2, font=('Times New Roman', 15), cursor="hand2")
rb_3 = tk.Radiobutton(frame4, text='3', variable=minimalizalando_value, value=3, font=('Times New Roman', 15), cursor="hand2")
rb_4 = tk.Radiobutton(frame4, text='4', variable=minimalizalando_value, value=4, font=('Times New Roman', 15), cursor="hand2")

label4 = tk.Label(frame4, text="Minimumba beállítás:", width=20, font=('Times New Roman', 15, 'bold'), foreground="Black")

forgato_minimalizalasa1 = tk.Button(frame4, width=5, text="Beállítás 1.", background=action_color, foreground=fg_color,command=lambda: threading.Thread(target=minimum_kereses_forgato1).start(),
                              cursor="hand2")
forgato_minimalizalasa2 = tk.Button(frame4, width=5, text="Beállítás 2.", background=action_color, foreground=fg_color,command=lambda: threading.Thread(target=minimum_kereses_forgato2).start(),
                              cursor="hand2")


label4.grid(rowspan=2, column=0, sticky="news")
# Rádiógombok elhelyezése a frame-en
rb_1.grid(row=0, column=1)
rb_2.grid(row=0, column=2)
rb_3.grid(row=0, column=3)
rb_4.grid(row=0, column=4)

forgato_minimalizalasa1.grid(row=2, column=1, columnspan=2, sticky="news")
forgato_minimalizalasa2.grid(row=2, column=3, columnspan=2, sticky="news")


# Alapértelmezett érték beállítása
minimalizalando_value.set(1)  # Alapértelmezettként a 1-es minimalizálandó van kiválasztva




#------------------------------------------

# Polarizáció kontroller tab -->

def polarizacio_kontroller_beallitas():
    return


pol_kontr=[0,0,0]

p_frame1 = tk.Frame(tab2, relief=tk.GROOVE, bd=2, width=600)

p_frame1.grid(row=0, column=0, sticky="nws", pady=5)

p_label1 = tk.Label(p_frame1, text="Polarizáció kontroller", width=20, height=5, font=('Times New Roman', 15, 'bold'), foreground="Black")
p_pol_label1 = tk.Label(p_frame1, text=pol_kontr[0], width=5, font=('Times New Roman', 15), foreground="Black")
p_pol_label2 = tk.Label(p_frame1, text=pol_kontr[1], width=5, font=('Times New Roman', 15), foreground="Black")
p_pol_label3 = tk.Label(p_frame1, text=pol_kontr[2], width=5, font=('Times New Roman', 15), foreground="Black")

polarizacio_but1 = tk.Button(p_frame1, width=5, text="Beállít", background=action_color, foreground=fg_color,command=lambda: threading.Thread(target=polarizacio_kontroller_beallitas).start(),
                              cursor="hand2")

p_label1.grid(row=0, column=0, columnspan=3, sticky="news")
p_pol_label1.grid(row=1,column=0,sticky="news", padx=100)
p_pol_label2.grid(row=1,column=1,sticky="news", padx=100)
p_pol_label3.grid(row=1,column=2,sticky="news", padx=100)

polarizacio_but1.grid(row=2,column=0,columnspan=3,sticky="news")

#----------------------------------------



notebook.grid(row=0, column=0, sticky="news")
plot_frame.grid(row=0, column=1, sticky="news")

window.mainloop()
