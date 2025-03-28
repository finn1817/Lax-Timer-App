import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class LacrosseTimerApp:

    def main():
    print("App is starting...")
    root = tk.Tk()
    app = LacrosseTimerApp(root)
    root.mainloop()

    
    def __init__(self, root):
        self.root = root
        self.root.title("Lacrosse Timer App - © Dan Finn")
        self.root.configure(bg="#e6f2ff")  # changed to a nicer light blue background
        # start the app in fullscreen mode
        self.root.attributes('-fullscreen', True)

        # add exit button for fullscreen
        self.exit_btn = tk.Button(
            self.root,
            text="Exit Fullscreen",
            command=self.exit_fullscreen,
            font=("Arial", 12),
            bg="red",
            fg="white",
            bd=0
        )
        self.exit_btn.place(relx=0.99, rely=0.01, anchor="ne")

        # variables to track timers
        self.intervals = {}  # store timer objects
        self.paused_times = {}  # store paused times in seconds
        self.timer_frames = {}  # store timer frames
        self.timer_count = 2  # start with 2 timers by default

        # create main frame with scrollbar
        self.main_frame = tk.Frame(root, bg="#e6f2ff")  # match the new background color
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=70)

        # create canvas with scrollbar
        self.canvas = tk.Canvas(self.main_frame, bg="#e6f2ff")  # match the new background color
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # create a frame inside the canvas for the timers
        self.timer_container = tk.Frame(self.canvas, bg="#e6f2ff")  # match the new background color
        self.canvas.create_window((0, 0), window=self.timer_container, anchor="nw")

        # header
        self.header = tk.Frame(root, bg="#007BFF", height=50)
        self.header.pack(fill=tk.X, side=tk.TOP)
        self.header.pack_propagate(False)

        self.title_label = tk.Label(
            self.header,
            text="This is a Lacrosse Timer Website - © Dan Finn",
            font=("Arial", 18),
            bg="#007BFF",
            fg="white"
        )
        self.title_label.pack(pady=10)

        # footer with control buttons
        self.footer = tk.Frame(root, bg="#007BFF", height=50)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM)
        self.footer.pack_propagate(False)

        # footer Control Buttons
        self.start_all_btn = tk.Button(
            self.footer,
            text="Start All",
            command=self.start_all_timers,
            font=("Arial", 12),
            bg="#007BFF",
            fg="white",
            bd=0
        )
        self.start_all_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=10)

        self.stop_all_btn = tk.Button(
            self.footer,
            text="Stop All",
            command=self.stop_all_timers,
            font=("Arial", 12),
            bg="#007BFF",
            fg="white",
            bd=0
        )
        self.stop_all_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=10)

        self.resume_all_btn = tk.Button(
            self.footer,
            text="Resume All",
            command=self.resume_all_timers,
            font=("Arial", 12),
            bg="#007BFF",
            fg="white",
            bd=0
        )
        self.resume_all_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=10)

        # add and remove timer buttons
        self.add_timer_btn = tk.Button(
            self.footer,
            text="Add Timer",
            command=self.add_timer,
            font=("Arial", 12),
            bg="#007BFF",
            fg="white",
            bd=0
        )
        self.add_timer_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=10)

        self.remove_timer_btn = tk.Button(
            self.footer,
            text="Remove Timer",
            command=self.remove_timer,
            font=("Arial", 12),
            bg="#007BFF",
            fg="white",
            bd=0
        )
        self.remove_timer_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=10)

        # save Button
        self.save_btn = tk.Button(
            self.footer,
            text="Save",
            command=self.save_data,
            font=("Arial", 12),
            bg="#007BFF",
            fg="white",
            bd=0
        )
        self.save_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=10)

        # initialize timers
        self.initialize_timers()

        # load saved data if exists
        self.load_data()

        # configure canvas scrolling
        self.timer_container.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # bind mousewheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """When canvas is resized, resize the inner frame to match"""
        width = event.width
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=width)

    def on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def initialize_timers(self):
        """Create initial timers"""
        for i in range(1, self.timer_count+1):
            self.create_timer(i)

    def create_timer(self, index):
        """Create smaller timer frames"""
        timer_frame = tk.Frame(self.timer_container, bg="white", bd=1, relief=tk.SOLID, padx=5, pady=5)
        timer_frame.pack(fill=tk.X, padx=5, pady=5)

        # adjust timer layout
        player_label = tk.Label(timer_frame, text="Player:", bg="white")
        player_label.grid(row=0, column=0, sticky="w", padx=3, pady=3)
        player_entry = tk.Entry(timer_frame, width=10)
        player_entry.grid(row=0, column=1, sticky="w", padx=3, pady=3)

        team_label = tk.Label(timer_frame, text="Team:", bg="white")
        team_label.grid(row=0, column=2, sticky="w", padx=3, pady=3)
        team_entry = tk.Entry(timer_frame, width=12)
        team_entry.grid(row=0, column=3, sticky="w", padx=3, pady=3)

        time_display = tk.Label(timer_frame, text="00:00:00", font=("Arial", 14), bg="white")
        time_display.grid(row=1, column=0, columnspan=2, pady=5)

        start_btn = tk.Button(timer_frame, text="Start", command=lambda idx=index: self.start_timer(idx), bg="#007BFF", fg="white")
        start_btn.grid(row=2, column=0, padx=5, pady=5)

        stop_btn = tk.Button(timer_frame, text="Stop", command=lambda idx=index: self.stop_timer(idx), bg="#007BFF", fg="white")
        stop_btn.grid(row=2, column=1, padx=5, pady=5)

        released_btn = tk.Button(timer_frame, text="Clear", command=lambda idx=index: self.clear_timer(idx), bg="#007BFF", fg="white")
        released_btn.grid(row=2, column=2, padx=5, pady=5)

        self.timer_frames[index] = {
            "frame": timer_frame,
            "player_entry": player_entry,
            "team_entry": team_entry,
            "time_display": time_display
        }
        self.paused_times[index] = 0

    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        self.root.attributes('-fullscreen', False)
