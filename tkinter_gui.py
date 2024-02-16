import tkinter as tk
import numpy as np
from time_controller import *
from datetime import datetime

# Time controller csatlakozás
tc, duration, bin_width, bin_count, DEFAULT_HISTOGRAM = time_controller_csatlakozas()

colors = ['blue', 'green', 'red', 'yellow']
legend_labels = ['1-3 koincidencia', '1-4 koincidencia', '2-3 koincidencia', '2-4 koincidencia']

shape = (4, 20)
beutesek = np.zeros(shape)

elso = True

def adatok(beutesek):
    global elso
    a = time.time()

    histograms = acquire_histograms(tc, duration, bin_width, bin_count, DEFAULT_HISTOGRAM)

    b = time.time()
    print(b-a)
    for i, (hist_title, histogram) in enumerate(histograms.items()):
        beutesek[i, 0:19] = beutesek[i, 1:20]
        beutesek[i, 19] = np.sum(histogram)
    return beutesek

def update_plot(beutesek):
    beutesek = adatok(beutesek)

    canvas.delete("all")  # Töröljük a korábbi elemeket

    max_value = 16000  # Maximum érték
    scale_factor = 600 / max_value  # Skálafaktor

    for i, beutessor in enumerate(beutesek):
        for j, value in enumerate(beutessor):
            x = j * 30  # X koordináta (30 a távolság a pontok között)
            y = 600 - value * scale_factor  # Y koordináta
            canvas.create_oval(x, y, x + 5, y + 5, fill=colors[i])  # Kirajzoljuk a pontokat

    root.after(100, lambda: update_plot(beutesek))
    root.update_idletasks()

# Inicializáljuk a Tkinter ablakot
root = tk.Tk()
root.title("Koincidencia mérés")

# Készítünk egy Tkinter Canvas objektumot és ágyazzuk be a Tkinter ablakba
canvas = tk.Canvas(root, width=600, height=600,bg="black")
canvas.pack()

# Futtatjuk a Tkinter event loop-ot
root.after(100, lambda: update_plot(beutesek))
root.mainloop()
