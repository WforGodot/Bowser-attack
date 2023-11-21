import tkinter as tk

def get_window_area():
    coordinates = [None]  # List to hold the coordinates

    def on_drag_start(event):
        canvas.coords("rectangle", event.x, event.y, event.x, event.y)

    def on_drag_motion(event):
        canvas.coords("rectangle", canvas.coords("rectangle")[0], canvas.coords("rectangle")[1], event.x, event.y)

    def on_drag_release(event):
        coords = canvas.coords("rectangle")
        canvas.coords("rectangle", coords[0], coords[1], event.x, event.y)
        coordinates[0] = (coords[0], coords[1], event.x, event.y)  # Store the coordinates
        root.destroy()  # Close the window after releasing the mouse

    def close(event=None):
        root.destroy()  # Function to close the window

    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    root.attributes('-alpha', 0.3)
    root.overrideredirect(True)

    canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight(), bg='white')
    canvas.pack()

    rect = canvas.create_rectangle(0, 0, 0, 0, outline='#ff0000', width=5, dash=(4, 2), tag="rectangle")

    canvas.bind("<ButtonPress-1>", on_drag_start)
    canvas.bind("<B1-Motion>", on_drag_motion)
    canvas.bind("<ButtonRelease-1>", on_drag_release)

    root.bind("<Escape>", close)
    root.after(10000, close)

    root.mainloop()

    return coordinates[0]  # Return the stored coordinates

