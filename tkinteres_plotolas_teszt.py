import tkinter as tk

def plot():
    # Get the coordinates from the entry widget
    x_values = [int(x) for x in entry_x.get().split(',')]
    y_values = [int(y) for y in entry_y.get().split(',')]

    # Clear previous drawings
    canvas.delete("all")

    # Plot the points
    for i in range(len(x_values)):
        canvas.create_oval(x_values[i] - 3, y_values[i] - 3, x_values[i] + 3, y_values[i] + 3, fill="blue")

# Create the main window
root = tk.Tk()
root.title("Simple Plot in Tkinter")

# Create Entry widgets for x and y coordinates
label_x = tk.Label(root, text="X coordinates:")
label_x.pack()
entry_x = tk.Entry(root)
entry_x.pack()

label_y = tk.Label(root, text="Y coordinates:")
label_y.pack()
entry_y = tk.Entry(root)
entry_y.pack()

# Create a button to trigger the plot
plot_button = tk.Button(root, text="Plot", command=plot)
plot_button.pack()

# Create a Canvas widget for drawing
canvas = tk.Canvas(root, width=400, height=300, bg="black")
canvas.pack()

# Run the Tkinter event loop
root.mainloop()