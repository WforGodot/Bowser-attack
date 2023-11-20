import tkinter as tk


def get_window_area():
    def on_drag_start(event):
        canvas.coords("rectangle", event.x, event.y, event.x, event.y)

    def on_drag_motion(event):
        canvas.coords("rectangle", canvas.coords("rectangle")[0], canvas.coords("rectangle")[1], event.x, event.y)

    def on_drag_release(event):
        canvas.coords("rectangle", canvas.coords("rectangle")[0], canvas.coords("rectangle")[1], event.x, event.y)
        print("Rectangle coordinates:", canvas.coords("rectangle"))
        root.destroy()  # Close the window after releasing the mouse
    
    root = tk.Tk()
    root.attributes('-fullscreen', True)  # Fullscreen window
    root.attributes('-topmost', True)  # Always on top
    root.attributes('-alpha', 0.3)  # Transparency (1.0: Opaque, <1.0: Transparent)

    # Remove window decorations
    root.overrideredirect(True)

    canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight(), bg='white')
    canvas.pack()

    # Create a rectangle with a bright red outline
    rect = canvas.create_rectangle(0, 0, 0, 0, outline='#ff0000', width=5, dash=(4, 2), tag="rectangle")

    canvas.bind("<ButtonPress-1>", on_drag_start)
    canvas.bind("<B1-Motion>", on_drag_motion)
    canvas.bind("<ButtonRelease-1>", on_drag_release)

    root.mainloop()
    
