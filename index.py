import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class LacrosseTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lacrosse Timer App - © Dan Finn")
        self.root.configure(bg="#e6f2ff")  # Changed to a nicer light blue background
        self.root.geometry("1200x800")
        
        # Variables to track timers
        self.intervals = {}  # Store timer objects
        self.paused_times = {}  # Store paused times in seconds
        self.timer_frames = {}  # Store timer frames
        self.timer_count = 2  # Start with 2 timers by default
        
        # Create main frame with scrollbar
        self.main_frame = tk.Frame(root, bg="#e6f2ff")  # Match the new background color
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=70)
        
        # Create canvas with scrollbar
        self.canvas = tk.Canvas(self.main_frame, bg="#e6f2ff")  # Match the new background color
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas for the timers
        self.timer_container = tk.Frame(self.canvas, bg="#e6f2ff")  # Match the new background color
        self.canvas.create_window((0, 0), window=self.timer_container, anchor="nw")
        
        # Header
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
        
        # Footer with control buttons
        self.footer = tk.Frame(root, bg="#007BFF", height=50)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM)
        self.footer.pack_propagate(False)
        
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
        
        # Add/Remove timer buttons
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
        
        # Save button
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
        
        # Initialize timers
        self.initialize_timers()
        
        # Load saved data if exists
        self.load_data()
        
        # Configure canvas scrolling
        self.timer_container.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind mousewheel for scrolling
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
        for i in range(1, self.timer_count + 1):
            self.create_timer(i)
    
    def create_timer(self, index):
        """Create a new timer with the given index"""
        # Create a frame for the timer
        timer_frame = tk.Frame(self.timer_container, bg="white", bd=1, relief=tk.SOLID, padx=10, pady=10)
        timer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add close button (X) to remove this specific timer
        close_btn = tk.Button(
            timer_frame,
            text="✕",
            command=lambda idx=index: self.remove_specific_timer(idx),
            bg="white",
            fg="red",
            font=("Arial", 10, "bold"),
            bd=0,
            padx=5,
            pady=0
        )
        close_btn.grid(row=0, column=2, sticky="ne")
        
        # Player number input
        player_label = tk.Label(timer_frame, text="Player Number:", bg="white")
        player_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        player_entry = tk.Entry(timer_frame, width=20)
        player_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Team name input
        team_label = tk.Label(timer_frame, text="Team Name:", bg="white")
        team_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        team_entry = tk.Entry(timer_frame, width=20)
        team_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Time selection
        time_label = tk.Label(timer_frame, text="Penalty Time:", bg="white")
        time_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        time_options = [
            "Not in use",
            "00:00:30",
            "00:01:00",
            "00:01:30",
            "00:02:00",
            "00:02:30",
            "00:03:00",
            "00:03:30",
            "00:04:00",
            "00:04:30",
            "00:05:00"
        ]
        
        time_var = tk.StringVar(value=time_options[0])
        time_dropdown = ttk.Combobox(timer_frame, textvariable=time_var, values=time_options, state="readonly", width=18)
        time_dropdown.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        time_dropdown.bind("<<ComboboxSelected>>", lambda e, idx=index: self.setup_timer(idx))
        
        # Timer display
        time_display = tk.Label(timer_frame, text="00:00:00", font=("Arial", 16, "bold"), bg="white")
        time_display.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Control buttons
        button_frame = tk.Frame(timer_frame, bg="white")
        button_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        start_btn = tk.Button(
            button_frame, 
            text="Start", 
            command=lambda idx=index: self.start_timer(idx),
            bg="#007BFF",
            fg="white"
        )
        start_btn.pack(side=tk.LEFT, padx=5)
        
        stop_btn = tk.Button(
            button_frame, 
            text="Stop", 
            command=lambda idx=index: self.stop_timer(idx),
            bg="#007BFF",
            fg="white"
        )
        stop_btn.pack(side=tk.LEFT, padx=5)
        
        released_btn = tk.Button(
            button_frame, 
            text="Released", 
            command=lambda idx=index: self.clear_timer(idx),
            bg="#007BFF",
            fg="white"
        )
        released_btn.pack(side=tk.LEFT, padx=5)
        
        # Penalty type selection
        penalty_label = tk.Label(timer_frame, text="Penalty Type:", bg="white")
        penalty_label.grid(row=5, column=0, sticky="w", padx=5, pady=5)
        
        penalty_options = [
            "Select Penalty Type",
            "Foul",
            "Slash",
            "Push",
            "Crease",
            "Crosscheck",
            "IllegalProcedure",
            "Screen",
            "Interference",
            "Misconduct"
        ]
        
        penalty_var = tk.StringVar(value=penalty_options[0])
        penalty_dropdown = ttk.Combobox(timer_frame, textvariable=penalty_var, values=penalty_options, state="readonly", width=18)
        penalty_dropdown.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        
        # Penalty time input
        penalty_time_label = tk.Label(timer_frame, text="Time of Penalty:", bg="white")
        penalty_time_label.grid(row=6, column=0, sticky="w", padx=5, pady=5)
        penalty_time_entry = tk.Entry(timer_frame, width=20)
        penalty_time_entry.grid(row=6, column=1, sticky="w", padx=5, pady=5)
        
        # Store references to widgets
        self.timer_frames[index] = {
            "frame": timer_frame,
            "player_entry": player_entry,
            "team_entry": team_entry,
            "time_var": time_var,
            "time_display": time_display,
            "penalty_var": penalty_var,
            "penalty_time_entry": penalty_time_entry,
            "close_btn": close_btn  # Store reference to close button
        }
        
        # Initialize timer values
        self.paused_times[index] = 0
    
    def remove_specific_timer(self, index):
        """Remove a specific timer by its index"""
        if len(self.timer_frames) <= 1:
            messagebox.showinfo("Cannot Remove", "You must have at least one timer.")
            return
            
        # Stop the timer if running
        self.stop_timer(index)
        
        # Remove the timer frame
        if index in self.timer_frames:
            self.timer_frames[index]["frame"].destroy()
            del self.timer_frames[index]
            
            # Remove from paused_times
            if index in self.paused_times:
                del self.paused_times[index]
            
            # Update scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def setup_timer(self, index):
        """Set up the timer based on the selected time"""
        if index not in self.timer_frames:
            return
        
        time_str = self.timer_frames[index]["time_var"].get()
        if time_str == "Not in use":
            self.paused_times[index] = 0
            self.timer_frames[index]["time_display"].config(text="00:00:00")
            return
        
        # Convert time string to seconds
        self.paused_times[index] = self.hms_to_seconds(time_str)
        self.timer_frames[index]["time_display"].config(text=self.seconds_to_hms(self.paused_times[index]))
    
    def start_timer(self, index):
        """Start the timer with the given index"""
        if index not in self.timer_frames:
            return
        
        # Stop existing timer if running
        self.stop_timer(index)
        
        # Start a new timer
        if self.paused_times[index] > 0:
            self.intervals[index] = self.root.after(1000, lambda: self.update_timer(index))
    
    def update_timer(self, index):
        """Update the timer display and decrement the time"""
        if index not in self.timer_frames or index not in self.paused_times:
            return
        
        if self.paused_times[index] > 0:
            self.paused_times[index] -= 1
            self.timer_frames[index]["time_display"].config(text=self.seconds_to_hms(self.paused_times[index]))
            self.intervals[index] = self.root.after(1000, lambda: self.update_timer(index))
        else:
            # Timer reached zero
            if index in self.intervals:
                self.root.after_cancel(self.intervals[index])
                del self.intervals[index]
    
    def stop_timer(self, index):
        """Stop the timer with the given index"""
        if index in self.intervals:
            self.root.after_cancel(self.intervals[index])
            del self.intervals[index]
    
    def clear_timer(self, index):
        """Clear the timer with the given index"""
        if index not in self.timer_frames:
            return
        
        # Stop the timer if running
        self.stop_timer(index)
        
        # Reset the time
        self.paused_times[index] = 0
        self.timer_frames[index]["time_display"].config(text="00:00:00")
    
    def start_all_timers(self):
        """Start all timers"""
        for index in self.timer_frames:
            self.start_timer(index)
    
    def stop_all_timers(self):
        """Stop all timers"""
        for index in list(self.intervals.keys()):
            self.stop_timer(index)
    
    def resume_all_timers(self):
        """Resume all timers"""
        for index in self.timer_frames:
            if self.paused_times[index] > 0:
                self.start_timer(index)
    
    def add_timer(self):
        """Add a new timer"""
        self.timer_count += 1
        self.create_timer(self.timer_count)
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def remove_timer(self):
        """Remove the last timer"""
        if self.timer_count > 1:
            # Find the highest index timer
            highest_index = max(self.timer_frames.keys())
            
            # Stop the timer if running
            self.stop_timer(highest_index)
            
            # Remove the timer frame
            if highest_index in self.timer_frames:
                self.timer_frames[highest_index]["frame"].destroy()
                del self.timer_frames[highest_index]
                
                # Remove from paused_times
                if highest_index in self.paused_times:
                    del self.paused_times[highest_index]
                
                self.timer_count -= 1
                
                # Update scroll region
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def save_data(self):
        """Save the current state of all timers to a JSON file"""
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timer_count": self.timer_count,
            "timers": {}
        }
        
        for index, timer_data in self.timer_frames.items():
            data["timers"][str(index)] = {
                "player_number": timer_data["player_entry"].get(),
                "team_name": timer_data["team_entry"].get(),
                "time_selection": timer_data["time_var"].get(),
                "remaining_time": self.paused_times.get(index, 0),
                "penalty_type": timer_data["penalty_var"].get(),
                "penalty_time": timer_data["penalty_time_entry"].get()
            }
        
        try:
            with open("lacrosse_timer_data.json", "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Save Successful", "Timer data has been saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save data: {str(e)}")
    
    def load_data(self):
        """Load timer data from JSON file if it exists"""
        if not os.path.exists("lacrosse_timer_data.json"):
            return
        
        try:
            with open("lacrosse_timer_data.json", "r") as f:
                data = json.load(f)
            
            # Clear existing timers
            for index in list(self.timer_frames.keys()):
                if index in self.intervals:
                    self.root.after_cancel(self.intervals[index])
                self.timer_frames[index]["frame"].destroy()
            
            self.timer_frames = {}
            self.intervals = {}
            self.paused_times = {}
            
            # Set timer count
            self.timer_count = data.get("timer_count", 2)
            
            # Create new timers based on saved data
            for index_str, timer_data in data.get("timers", {}).items():
                index = int(index_str)
                self.create_timer(index)
                
                # Set values
                if index in self.timer_frames:
                    self.timer_frames[index]["player_entry"].insert(0, timer_data.get("player_number", ""))
                    self.timer_frames[index]["team_entry"].insert(0, timer_data.get("team_name", ""))
                    self.timer_frames[index]["time_var"].set(timer_data.get("time_selection", "Not in use"))
                    self.timer_frames[index]["penalty_var"].set(timer_data.get("penalty_type", "Select Penalty Type"))
                    self.timer_frames[index]["penalty_time_entry"].insert(0, timer_data.get("penalty_time", ""))
                    
                    # Set remaining time
                    self.paused_times[index] = timer_data.get("remaining_time", 0)
                    self.timer_frames[index]["time_display"].config(text=self.seconds_to_hms(self.paused_times[index]))
            
            messagebox.showinfo("Load Successful", "Timer data has been loaded successfully!")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load data: {str(e)}")
    
    def seconds_to_hms(self, seconds):
        """Convert seconds to HH:MM:SS format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def hms_to_seconds(self, hms_str):
        """Convert HH:MM:SS string to seconds"""
        if hms_str == "Not in use":
            return 0
        
        parts = hms_str.split(":")
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        return 0

def main():
    root = tk.Tk()
    app = LacrosseTimerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
