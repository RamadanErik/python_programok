import tkinter as tk
from tkinter import ttk
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import threading
import scipy.optimize

from forgato import *
from time_controller import *
from fuggvenyek import kontrollerhez_csatlakozas2,kereso_algoritmus_sima2


# time_controller csatlakozás
tc, DEFAULT_ACQUISITION_DURATION, bin_width, DEFAULT_BIN_COUNT, DEFAULT_HISTOGRAMS = time_controller_csatlakozas()
# ------

# forgato csatlakozas
s_no1 = "55290504"
s_no2 = "55290814"
device_1, device_2 = forgato_csatlakozas(s_no1, s_no2)
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
plot_histogram = False

bin_width=adjust_bin_width(tc,bin_width)

class PlotUpdater:
    def __init__(self, window, fig, ax, canvas):
        self.window = window
        self.fig = fig
        self.ax = ax
        self.canvas = canvas
        self.continue_update = False
        self.plot_1_3 = tk.BooleanVar(value=True)
        self.plot_1_4 = tk.BooleanVar(value=True)
        self.plot_2_3 = tk.BooleanVar(value=True)
        self.plot_2_4 = tk.BooleanVar(value=True)
        self.lenormalt = tk.BooleanVar(value = False)
        self.thread = None
        global device_1
        global device_2

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
            if not plot_histogram:
                beutesek = self.adatok()
                self.utolso_beutes(beutesek)
                # Clear the previous plot
                self.ax.clear()
                adat_ki = beutesek
                ylim=12000
                E_ki=0
                if self.lenormalt.get():
                    adat_ki_raw = np.array(beutesek)
                    oszlop_osszeg = np.sum(adat_ki_raw, axis=0)
                    adat_ki1 = np.round(adat_ki_raw / oszlop_osszeg,4)
                    adat_ki1 = np.nan_to_num(adat_ki1, nan=0)
                    adat_ki = adat_ki1.tolist()
                    ylim=1

                    E = (-adat_ki1[1]-adat_ki1[2]+adat_ki1[0]+adat_ki1[3]+1)/2
                    E_ki = E.tolist()

                for i in range(4):
                    if i == 0 and self.plot_1_3.get():
                        self.ax.plot(adat_ki[i], color=colors[i], marker='o', linestyle='', label=legend_labels[i])
                        beutes_label1.config(text=utolso[0])
                    elif i == 1 and self.plot_1_4.get():
                        self.ax.plot(adat_ki[i], color=colors[i], marker='o', linestyle='', label=legend_labels[i])
                        beutes_label2.config(text=utolso[1])
                    elif i == 2 and self.plot_2_3.get():
                        self.ax.plot(adat_ki[i], color=colors[i], marker='o', linestyle='', label=legend_labels[i])
                        beutes_label3.config(text=utolso[2])
                    elif i == 3 and self.plot_2_4.get():
                        self.ax.plot(adat_ki[i], color=colors[i], marker='o', linestyle='', label=legend_labels[i])
                        beutes_label4.config(text=utolso[3])
                if self.lenormalt.get():
                    self.ax.plot(E_ki, color="white", marker='o', linestyle='', label="E")
                    self.ax2 = ax.twinx()
                    self.ax2.set_ylim([-1, 1])
                    self.ax2.set_yticks(np.linspace(-1, 1, 11))

                self.ax.legend(loc='upper left')
                self.ax.set_ylim([0, ylim])
                self.ax.set_yticks(np.linspace(0,ylim,11))
                self.ax.set_title('Koincidencia mérés')
                self.ax.set_xlabel('Adat')
                self.ax.set_ylabel('Beütések')
                self.ax.set_xticks(range(0, 20))
                self.ax.set_facecolor(bg_color)
                self.ax.grid(color=highlight_color)

            else:
                self.ax.clear()
                histograms = self.generate()

                max_bin_count = max(len(histogram) for histogram in histograms.values())

                self.ax.set(xlabel="ps", ylabel="counts")
                self.ax.set_xlim(0, max_bin_count * bin_width)

                colors2 = ['blue', 'green', 'red', 'yellow']
                c = 0
                for hist_title, histogram in histograms.items():

                    if isinstance(hist_title, int):
                        hist_title = f"Histogram {hist_title}"

                    bins = filter_histogram_bins(histogram, bin_width)

                    xp, yp = tuple(bins.keys()), tuple(bins.values())

                    bar_plot = self.ax.bar(xp, yp, align="edge", width=bin_width, alpha=0.1)

                    self.ax.step(xp, yp, color=colors2[c], where="post", label=hist_title, alpha=1)
                    c += 1
                self.ax.legend(legend_labels)
                self.ax.set_xticks(range(0, max_bin_count * bin_width + 1, 200))
                self.ax.set_title('Korrelációs hisztogrammok')

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
ax.set_ylim([0, 4000])
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


def plotvaltas():
    global plot_histogram
    if plot_histogram:
        plot_histogram=False
    else:
        plot_histogram=True
    return

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

corr_hist_button = tk.Button(frame2,text="Plot váltás", background=action_color, width=15, height=5, foreground=fg_color,
                             command=lambda: threading.Thread(target=plotvaltas).start(), cursor="hand2")
cb_normalt = tk.Checkbutton(frame2, text='Normált', variable=plot_frame.plot_updater.lenormalt, font=('Times New Roman', 15),
                        onvalue=True, offvalue=False, width=4, cursor="hand2")


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

corr_hist_button.grid(row=3, column=1, sticky="news")
cb_normalt.grid(row=3, column=0, sticky="news")
# --------------------

szog1 = 0
szog2 = 0
forgato_szog1 = tk.StringVar()
forgato_szog2 = tk.StringVar()


def set_forgato1():
    global szog1
    global forgatas1
    global minimalizalas
    global bell

    try:
        if not (forgatas1 or minimalizalas or bell):
            x = re.split(',|\.', forgato_szog1.get())
            if len(x) == 1:
                szog1 = float(x[0])
            else:
                szog1 = int(x[0]) + int(x[1]) / (10 ** len(x[1]))
    except:
        szog1 = 0
    forgato_ertek1.config(text=szog1)
    b_forgato_ertek1.config(text=szog1)

    # beállítja a forgatót

    x = threading.Thread(target=move_forgato, args=[device_1, szog1])
    x.start()
    #move_forgato(device_1,szog1)


def set_forgato2():
    global szog2
    global forgatas2
    global minimalizalas
    global bell


    try:
        if not (forgatas2 or minimalizalas or bell):
            x = re.split(',|\.', forgato_szog2.get())
            if len(x) == 1:
                szog2 = float(x[0])
            else:
                szog2 = int(x[0]) + int(x[1]) / (10 ** len(x[1]))
    except:
        szog2 = 0
    forgato_ertek2.config(text=szog2)
    b_forgato_ertek2.config(text=szog2)
    # beállítja a forgatót

    x = threading.Thread(target=move_forgato, args=[device_2, szog2])
    x.start()
    #move_forgato(device_2,szog2)


forgatas1=False
forgatas2=False

minimalizalas=False
bell=False

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
        time.sleep(2)
        szog1+=5
        if szog1>360:
            szog1=0

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
        time.sleep(2)
        szog2+=5
        if szog2>360:
            szog2=0


minimalizalando_value = tk.IntVar()  # Változó a kiválasztott minimalizálandó érték tárolására


def fit_sin(tt, yy):
    tt = np.array(tt)
    yy = np.array(yy)
    ff = np.fft.fftfreq(len(tt), (tt[1]-tt[0]))   # assume uniform spacing
    Fyy = abs(np.fft.fft(yy))
    guess_freq = abs(ff[np.argmax(Fyy[1:])+1])   # excluding the zero frequency "peak", which is related to offset
    guess_amp = np.std(yy) * 2.**0.5
    guess_offset = np.mean(yy)
    guess = np.array([guess_amp, 2.*np.pi*guess_freq, 0., guess_offset])
    def sinfunc(t, A, w, p, c):  return A * np.sin(w*t + p) + c
    popt, pcov = scipy.optimize.curve_fit(sinfunc, tt, yy, p0=guess)
    A, w, p, c = popt
    f = w/(2.*np.pi)
    fitfunc = lambda t: A * np.sin(w*t + p) + c
    return {"amp": A, "omega": w, "phase": p, "offset": c, "freq": f, "period": 1./f, "fitfunc": fitfunc, "maxcov": np.max(pcov), "rawres": (guess,popt,pcov)}

    
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

    szogek=[]
    beutesek=[]

    forgato_minimalizalasa1.config(text="...")
    fokonkent=5
    k=int(90/fokonkent)
    for i in range(k):
        szog1+=fokonkent
        szogek.append(szog1)
        set_forgato1()
        time.sleep(3)

        beutes = utolso[min_val-1]
        beutesek.append(beutes)
        if( beutes < minbeut ):
            minszog=szog1
            minbeut=beutes

    # szin = fit_sin(szogek,beutes)
    # minszog = 90 * 3/4 - szin["phase"]/szin["omega"]

    szog1 = minszog
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
    k=int(90/fokonkent)
    for i in range(k):
        szog2+=fokonkent
        set_forgato2()
        time.sleep(3)
        beutes = utolso[min_val-1]
        if( beutes < minbeut ):
            minszog=szog2
            minbeut=beutes
    
    szog2 = minszog
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

rb_label1_dot = tk.Label(frame4, text="●", width=5, font=('Times New Roman', 15), foreground=kek)
rb_label2_dot = tk.Label(frame4, text="●", width=5, font=('Times New Roman', 15), foreground=zold)
rb_label3_dot = tk.Label(frame4, text="●", width=5, font=('Times New Roman', 15), foreground=piros)
rb_label4_dot = tk.Label(frame4, text="●", width=5, font=('Times New Roman', 15), foreground=sarga)



label4 = tk.Label(frame4, text="Minimumba beállítás:", width=20, font=('Times New Roman', 15, 'bold'), foreground="Black")

forgato_minimalizalasa1 = tk.Button(frame4, width=5, text="Beállítás 1.", background=action_color, foreground=fg_color,command=lambda: threading.Thread(target=minimum_kereses_forgato1).start(),
                              cursor="hand2")
forgato_minimalizalasa2 = tk.Button(frame4, width=5, text="Beállítás 2.", background=action_color, foreground=fg_color,command=lambda: threading.Thread(target=minimum_kereses_forgato2).start(),
                              cursor="hand2")



label4.grid(rowspan=4, column=0, sticky="news")
# Rádiógombok elhelyezése a frame-en
rb_1.grid(row=0, column=1)
rb_2.grid(row=0, column=2)
rb_3.grid(row=0, column=3)
rb_4.grid(row=0, column=4)

rb_label1_dot.grid(row=1, column=1)
rb_label2_dot.grid(row=1, column=2)
rb_label3_dot.grid(row=1, column=3)
rb_label4_dot.grid(row=1, column=4)



forgato_minimalizalasa1.grid(row=2, column=1, columnspan=2, sticky="news")
forgato_minimalizalasa2.grid(row=2, column=3, columnspan=2, sticky="news")




# Alapértelmezett érték beállítása
minimalizalando_value.set(1)  # Alapértelmezettként a 1-es minimalizálandó van kiválasztva




#------------------------------------------
p_gomb_szoveg=["Beállít","Beállít","Beállít","Beállít"]
p_csatlakozva=[False,False,False,False]
pol_devices = [0,0,0,0]

# Polarizáció kontroller tab -->

#Csatlakozás
serial_no = [38290024,38405444,38432514,38442764]
for i in range(4):
    try:
        pol_devices[i], paddle11, paddle22, paddle33 = kontrollerhez_csatlakozas2(serial_no[i])
        p_csatlakozva[i] = True
    except:
        p_gomb_szoveg[i] = "Nem sikerült csatlakozni"
        print(f"Nem sikerült csatlakozni a(z) {i}. polarizáció konrtollerhez")
    pol_kontr=[[0,0,0],[0,0,0],[0,0,0],[0,0,0]]




def polarizacio_kontroller_beallitas(i):
    global p_csatlakozva
    if p_csatlakozva[i]:
        global pol_devices
        global pol_kontr
        global  pol_labels
        fokok, adatok3, optimum = kereso_algoritmus_sima2(pol_devices[i], tc, 3, 10,i)
        pol_kontr[i]=optimum
        pol_labels[i][0].config(text=round(pol_kontr[i][0],2))
        pol_labels[i][1].config(text=round(pol_kontr[i][1],2))
        pol_labels[i][2].config(text=round(pol_kontr[i][2],2))
    return




p_frame1 = tk.Frame(tab2, relief=tk.GROOVE, bd=2, width=600)

p_frame1.grid(row=0, column=0, sticky="nws", pady=5)

p_label1 = tk.Label(p_frame1, text="Polarizáció kontroller", width=20, height=5, font=('Times New Roman', 15, 'bold'), foreground="Black")

#1
p_pol_label1 = tk.Label(p_frame1, text=round(pol_kontr[0][0],2), width=5, font=('Times New Roman', 15), foreground="Black")
p_pol_label2 = tk.Label(p_frame1, text=round(pol_kontr[0][1],2), width=5, font=('Times New Roman', 15), foreground="Black")
p_pol_label3 = tk.Label(p_frame1, text=round(pol_kontr[0][2],2), width=5, font=('Times New Roman', 15), foreground="Black")
#2
p_pol2_label1 = tk.Label(p_frame1, text=round(pol_kontr[1][0],2), width=5, font=('Times New Roman', 15), foreground="Black")
p_pol2_label2 = tk.Label(p_frame1, text=round(pol_kontr[1][1],2), width=5, font=('Times New Roman', 15), foreground="Black")
p_pol2_label3 = tk.Label(p_frame1, text=round(pol_kontr[1][2],2), width=5, font=('Times New Roman', 15), foreground="Black")
#3
p_pol3_label1 = tk.Label(p_frame1, text=round(pol_kontr[2][0],2), width=5, font=('Times New Roman', 15), foreground="Black")
p_pol3_label2 = tk.Label(p_frame1, text=round(pol_kontr[2][1],2), width=5, font=('Times New Roman', 15), foreground="Black")
p_pol3_label3 = tk.Label(p_frame1, text=round(pol_kontr[2][2],2), width=5, font=('Times New Roman', 15), foreground="Black")
#4
p_pol4_label1 = tk.Label(p_frame1, text=round(pol_kontr[3][0],2), width=5, font=('Times New Roman', 15), foreground="Black")
p_pol4_label2 = tk.Label(p_frame1, text=round(pol_kontr[3][1],2), width=5, font=('Times New Roman', 15), foreground="Black")
p_pol4_label3 = tk.Label(p_frame1, text=round(pol_kontr[3][2],2), width=5, font=('Times New Roman', 15), foreground="Black")

pol_labels = [[p_pol_label1,p_pol_label2,p_pol_label3], [p_pol2_label1,p_pol2_label2,p_pol2_label3] , [p_pol3_label1,p_pol3_label2,p_pol3_label3], [p_pol4_label1,p_pol4_label2,p_pol4_label3]]


polarizacio_but1 = tk.Button(p_frame1, width=20, height=3, text=p_gomb_szoveg[0], background=action_color, foreground=fg_color, command=lambda: threading.Thread(target=lambda: polarizacio_kontroller_beallitas(0)).start(), cursor="hand2")
polarizacio_but2 = tk.Button(p_frame1, width=20, height=3, text=p_gomb_szoveg[1], background=action_color, foreground=fg_color, command=lambda: threading.Thread(target=lambda: polarizacio_kontroller_beallitas(1)).start(), cursor="hand2")
polarizacio_but3 = tk.Button(p_frame1, width=20, height=3, text=p_gomb_szoveg[2], background=action_color, foreground=fg_color, command=lambda: threading.Thread(target=lambda: polarizacio_kontroller_beallitas(2)).start(), cursor="hand2")
polarizacio_but4 = tk.Button(p_frame1, width=20, height=3, text=p_gomb_szoveg[3], background=action_color, foreground=fg_color, command=lambda: threading.Thread(target=lambda: polarizacio_kontroller_beallitas(3)).start(), cursor="hand2")


p_label1.grid(row=0, column=0, columnspan=4, sticky="news")

# 1. csoport
p_pol_label1.grid(row=1, column=0, sticky="news", padx=40)
p_pol_label2.grid(row=1, column=1, sticky="news", padx=40)
p_pol_label3.grid(row=1, column=2, sticky="news", padx=40)

# 2. csoport
p_pol2_label1.grid(row=2, column=0, sticky="news", padx=40)
p_pol2_label2.grid(row=2, column=1, sticky="news", padx=40)
p_pol2_label3.grid(row=2, column=2, sticky="news", padx=40)

# 3. csoport
p_pol3_label1.grid(row=3, column=0, sticky="news", padx=40)
p_pol3_label2.grid(row=3, column=1, sticky="news", padx=40)
p_pol3_label3.grid(row=3, column=2, sticky="news", padx=40)

# 4. csoport
p_pol4_label1.grid(row=4, column=0, sticky="news", padx=40)
p_pol4_label2.grid(row=4, column=1, sticky="news", padx=40)
p_pol4_label3.grid(row=4, column=2, sticky="news", padx=40)


polarizacio_but1.grid(row=1, column=3, sticky="news")
polarizacio_but2.grid(row=2, column=3, sticky="news")
polarizacio_but3.grid(row=3, column=3, sticky="news")
polarizacio_but4.grid(row=4, column=3, sticky="news")




#----------------------------------------
#Bell mérés tab
def kompatibilis_szogekke(a):
    for i in range(len(a)):
        if a[i]>360:
            a[i]-=360
    return a

N = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
eredmenyek = [0,0,0,0]
bazis = [0.0, 0.0]

def beutes_label_beallit():
    global N

    bl11.config(text=N[0][0])
    bl12.config(text=N[0][1])
    bl13.config(text=N[0][2])
    bl14.config(text=N[0][3])

    bl21.config(text=N[1][0])
    bl22.config(text=N[1][1])
    bl23.config(text=N[1][2])
    bl24.config(text=N[1][3])

    bl31.config(text=N[2][0])
    bl32.config(text=N[2][1])
    bl33.config(text=N[2][2])
    bl34.config(text=N[2][3])

    bl41.config(text=N[3][0])
    bl42.config(text=N[3][1])
    bl43.config(text=N[3][2])
    bl44.config(text=N[3][3])

def eredmeny_label_beallit():
    global eredmenyek

    el1.config(text=eredmenyek[0])
    el2.config(text=eredmenyek[1])
    el3.config(text=eredmenyek[2])
    el4.config(text=eredmenyek[3])

def bazis_beallit():
    global bazis

    bazis_label.config(text=f"Bázis:  ({bazis[0]} - {bazis[1]}):")

def E_szamolas(i):
    global utolso
    global N
    N1,N2,N3,N4 = utolso
    N[i] = [N1,N2,N3,N4]
    beutes_label_beallit()

    E = (N1-N2-N3+N4) / (N1+N2+N3+N4)
    return round(E,4)


def bell_test():
    global szog1,szog2
    global eredmenyek
    global bell
    global N
    global bazis

    bell=True
    N = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    beutes_label_beallit()
    eredmenyek = [0, 0, 0, 0]
    eredmeny_label_beallit()

    #minimum_kereses_forgato1()

    #Bázis meghatározása
    bazis=[szog1,szog2]
    bazis_beallit()


    #Mérés szögei
    a = bazis[0]
    a2 = bazis[0]+22.5
    b = bazis[1]+11.25
    b2 = bazis[1]+33.75
    a, a2, b, b2 = kompatibilis_szogekke([a, a2, b, b2])

    meresek=[[a, b], [a, b2], [a2, b2], [a2, b]]



    for i,x in enumerate(meresek):
        szog1 = x[0]
        szog2 = x[1]
        print(f"Egyes beállítása {szog1}")
        print(f"Kettes beállítása {szog2}")
        set_forgato1()
        set_forgato2()
        time.sleep(8)
        eredmenyek[i] = E_szamolas(i)
        eredmeny_label_beallit()



    E_ab, E_ab2, E_a2b2, E_a2b = eredmenyek
    print(f"E_ab = {E_ab} \n E_ab' = {E_ab2} \n E_a'b' = {E_a2b2} \n E_a'b = {E_a2b} \n")
    S = round(E_ab - E_ab2 + E_a2b2 + E_a2b,4)
    S_label.config(text=S)
    print(f"Bell mérés vége: S = {S}")
    bell=False




b_frame1 = tk.Frame(tab3, relief=tk.GROOVE, bd=2, width=600)
b_frame2 = tk.Frame(tab3, relief=tk.GROOVE, bd=2, width=600)
b_frame1.grid(row=0, column=0, sticky="nws", pady=5)
b_frame2.grid(row=1, column=0, sticky="nws", pady=5)



# Utolsó beütés
bazis_label = tk.Label(b_frame1, text=f"Bázis:  ({bazis[0]} - {bazis[1]}):", width=20, font=('Times New Roman', 15), foreground="Black")
meres_label_1 = tk.Label(b_frame1, text="1. mérés  (0 - 22,5):", width=20, font=('Times New Roman', 15), foreground="Black")
meres_label_2 = tk.Label(b_frame1, text="2. mérés  (0 - 67,5):", width=20, font=('Times New Roman', 15), foreground="Black")
meres_label_3 = tk.Label(b_frame1, text="3. mérés  (45 - 67,5):", width=20, font=('Times New Roman', 15), foreground="Black")
meres_label_4 = tk.Label(b_frame1, text="4. mérés  (45 - 22,5):", width=20, font=('Times New Roman', 15), foreground="Black")


bl11 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
bl12 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
bl13 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
bl14 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")

bl21 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
bl22 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
bl23 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
bl24 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")

bl31 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
bl32 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
bl33 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
bl34 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")

bl41 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
bl42 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
bl43 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
bl44 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")

el1 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
el2 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
el3 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")
el4 = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")

S_label_szoveg = tk.Label(b_frame1, text="S =", width=5, font=('Times New Roman', 15), foreground="Black")
S_label = tk.Label(b_frame1, text=0, width=5, font=('Times New Roman', 15), foreground="Black")

beutes_label1_dot_b = tk.Label(b_frame1, text="●", width=5, font=('Times New Roman', 15), foreground=kek)
beutes_label2_dot_b = tk.Label(b_frame1, text="●", width=5, font=('Times New Roman', 15), foreground=zold)
beutes_label3_dot_b = tk.Label(b_frame1, text="●", width=5, font=('Times New Roman', 15), foreground=piros)
beutes_label4_dot_b = tk.Label(b_frame1, text="●", width=5, font=('Times New Roman', 15), foreground=sarga)
E_label_szoveg = tk.Label(b_frame1, text="E", width=5, font=('Times New Roman', 15), foreground="Black")

bell_test_button = tk.Button(b_frame1, width=5, text="Bell mérés", background=action_color, foreground=fg_color,command=lambda: threading.Thread(target=bell_test).start(),
                              cursor="hand2")



bazis_label.grid(row=0, column=0, sticky="news")
meres_label_1.grid(row=1, column=0, sticky="news")
meres_label_2.grid(row=2, column=0, sticky="news")
meres_label_3.grid(row=3, column=0, sticky="news")
meres_label_4.grid(row=4, column=0, sticky="news")


bl11.grid(row=1, column=1, sticky="news")
bl12.grid(row=1, column=2, sticky="news")
bl13.grid(row=1, column=3, sticky="news")
bl14.grid(row=1, column=4, sticky="news")

bl21.grid(row=2, column=1, sticky="news")
bl22.grid(row=2, column=2, sticky="news")
bl23.grid(row=2, column=3, sticky="news")
bl24.grid(row=2, column=4, sticky="news")

bl31.grid(row=3, column=1, sticky="news")
bl32.grid(row=3, column=2, sticky="news")
bl33.grid(row=3, column=3, sticky="news")
bl34.grid(row=3, column=4, sticky="news")

bl41.grid(row=4, column=1, sticky="news")
bl42.grid(row=4, column=2, sticky="news")
bl43.grid(row=4, column=3, sticky="news")
bl44.grid(row=4, column=4, sticky="news")

el1.grid(row=1, column=5, sticky="news")
el2.grid(row=2, column=5, sticky="news")
el3.grid(row=3, column=5, sticky="news")
el4.grid(row=4, column=5, sticky="news")

beutes_label1_dot_b.grid(row=0, column=1, sticky="news")
beutes_label2_dot_b.grid(row=0, column=2, sticky="news")
beutes_label3_dot_b.grid(row=0, column=3, sticky="news")
beutes_label4_dot_b.grid(row=0, column=4, sticky="news")
E_label_szoveg.grid(row=0, column=5, sticky="news")

S_label_szoveg.grid(row=5, column=4, sticky="news")
S_label.grid(row=5,column=5, sticky="news")

bell_test_button.grid(row=5, column=1, columnspan=3, sticky="news")


#Frame 2

b_label2 = tk.Label(b_frame2, text="Forgató beállítás:", width=20, font=('Times New Roman', 15, 'bold'), foreground="Black")

b_forgato_cim1 = tk.Label(b_frame2, text="1.", width=10, font=('Times New Roman', 15), foreground="Black")
b_forgato_box1 = tk.Entry(b_frame2, width=5, textvariable=forgato_szog1, font=('Times New Roman', 15), foreground="Black",
                        justify='center')
b_forgato_set1 = tk.Button(b_frame2, width=5, text="Set", background=action_color, foreground=fg_color,
                         command=set_forgato1, cursor="hand2")
b_forgato_ertek1 = tk.Label(b_frame2, width=10, text=szog1, font=('Times New Roman', 15), foreground="Black")
b_forgato_forgatas1 = tk.Button(b_frame2, width=5, text="Forgatás", background=action_color, foreground=fg_color,command=lambda: threading.Thread(target=set_korbe_forgatas1).start(),
                              cursor="hand2")

b_forgato_cim2 = tk.Label(b_frame2, text="2.", width=10, font=('Times New Roman', 15), foreground="Black")
b_forgato_box2 = tk.Entry(b_frame2, width=5, textvariable=forgato_szog2, font=('Times New Roman', 15), foreground="Black",
                        justify='center')
b_forgato_set2 = tk.Button(b_frame2, width=5, text="Set", background=action_color, foreground=fg_color,
                         command=set_forgato2, cursor="hand2")
b_forgato_ertek2 = tk.Label(b_frame2, width=10, text=szog1, font=('Times New Roman', 15), foreground="Black")
b_forgato_forgatas2 = tk.Button(b_frame2, width=5, text="Forgatás", background=action_color, foreground=fg_color,command=lambda: threading.Thread(target=set_korbe_forgatas2).start(),
                              cursor="hand2")

b_label2.grid(rowspan=4, column=0, sticky="news")

b_forgato_cim1.grid(row=0, column=1, columnspan=2, sticky="news")
b_forgato_box1.grid(row=1, column=1, sticky="news")
b_forgato_set1.grid(row=1, column=2, sticky="news")
b_forgato_ertek1.grid(row=2, column=1, columnspan=2, sticky="news")
b_forgato_forgatas1.grid(row=3, column=1, columnspan=2, sticky="news")

b_forgato_cim2.grid(row=0, column=3, columnspan=2, sticky="news")
b_forgato_box2.grid(row=1, column=3, sticky="news")
b_forgato_set2.grid(row=1, column=4, sticky="news")
b_forgato_ertek2.grid(row=2, column=3, columnspan=2, sticky="news")
b_forgato_forgatas2.grid(row=3, column=3, columnspan=2, sticky="news")


#----------------------------------------



notebook.grid(row=0, column=0, sticky="news")
plot_frame.grid(row=0, column=1, sticky="news")

window.mainloop()
