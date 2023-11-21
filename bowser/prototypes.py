   def create_ui(self):
        root = tk.Tk()
        root.title("Glossary and Summary")
        # root.overrideredirect(True)
        root.attributes('-topmost', True)  # Keeps the window always on top

        # Set the geometry of the window
        window_width = 400
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_coordinate = screen_width - window_width
        y_coordinate = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        def combined_command(action):
            root.iconify()
            time.sleep(5)
            action()
            root.deiconify()
        
        def create_buttons():
            button_specs = [
                ("F8: Screenshot & DOM", self.on_f8),
                ("F9: Screenshot Canvas", self.on_f9),
                ("F10: Start Recording", self.on_f10),
                ("F11: Start Inference", self.on_f11),
                ("F12: Pause", self.on_f12)
            ]

            for text, action in button_specs:
                tk.Button(root, text=text, command=lambda act=action: combined_command(act)).pack(fill=tk.X)

        create_buttons()

        root.mainloop()

        def combined_command(self, action):
        self.root.iconify()
        action()

        # Button creation
        btn_f8 = tk.Button(root, text="F8: Screenshot & DOM", command=self.on_f8)
        btn_f9 = tk.Button(root, text="F9: Screenshot Canvas", command=self.on_f9)
        btn_f10 = tk.Button(root, text="F10: Start Recording", command=self.on_f10)
        btn_f11 = tk.Button(root, text="F11: Start Inference", command=self.on_f11)
        btn_f12 = tk.Button(root, text="F12: Pause", command=self.on_f12)

        # Pack buttons
        btn_f8.pack(fill=tk.X)
        btn_f9.pack(fill=tk.X)
        btn_f10.pack(fill=tk.X)
        btn_f11.pack(fill=tk.X)
        btn_f12.pack(fill=tk.X)

        root.mainloop()
