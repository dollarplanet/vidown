import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os


SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "value.json")


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.wm_class = "Vidown"
        self.root.title("Vidown - YouTube Downloader")
        self.root.resizable(False, False)
        self._start_enabled = False
        self._end_enabled = False
        self.setup_ui()
        self.load_settings()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="12")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Video URL").pack(anchor=tk.W)
        self.url_input = ttk.Entry(main_frame, width=60)
        self.url_input.pack(fill=tk.X, pady=(0, 12))

        time_frame = ttk.LabelFrame(main_frame, text="Start / End Time (HH:MM:SS)", padding="8")
        time_frame.pack(fill=tk.X, pady=(0, 12))

        self.start_var = tk.BooleanVar(value=False)
        self.start_checkbox = ttk.Checkbutton(time_frame, text="Start:", variable=self.start_var, command=self.toggle_start_time)
        self.start_checkbox.pack(anchor=tk.W)
        self.start_time_input = ttk.Entry(time_frame, width=15, state=tk.DISABLED)
        self.start_time_input.pack(anchor=tk.W, padx=(80, 0), pady=(0, 8))

        self.end_var = tk.BooleanVar(value=False)
        self.end_checkbox = ttk.Checkbutton(time_frame, text="End:", variable=self.end_var, command=self.toggle_end_time)
        self.end_checkbox.pack(anchor=tk.W)
        self.end_time_input = ttk.Entry(time_frame, width=15, state=tk.DISABLED)
        self.end_time_input.pack(anchor=tk.W, padx=(80, 0), pady=(0, 8))

        mode_frame = ttk.LabelFrame(main_frame, text="Mode", padding="8")
        mode_frame.pack(fill=tk.X, pady=(0, 12))

        self.mode_var = tk.StringVar(value="video")
        self.video_radio = ttk.Radiobutton(mode_frame, text="Video", value="video", variable=self.mode_var)
        self.video_radio.pack(side=tk.LEFT)
        self.audio_radio = ttk.Radiobutton(mode_frame, text="Audio", value="audio", variable=self.mode_var)
        self.audio_radio.pack(side=tk.LEFT, padx=(12, 0))

        ttk.Label(main_frame, text="Quality").pack(anchor=tk.W)
        self.quality_combo = ttk.Combobox(main_frame, values=["Best (HD)", "1080p", "720p", "480p", "360p"], state="readonly")
        self.quality_combo.set("Best (HD)")
        self.quality_combo.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(main_frame, text="Output Folder").pack(anchor=tk.W)
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 12))
        self.output_folder_input = ttk.Entry(folder_frame)
        self.output_folder_input.insert(0, os.path.expanduser("~/Downloads"))
        self.output_folder_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.LEFT, padx=(8, 0))

        self.download_button = ttk.Button(main_frame, text="Download", command=self.start_download)
        self.download_button.pack(fill=tk.X, pady=(0, 12))

        self.progress_bar = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(main_frame, text="Log").pack(anchor=tk.W)
        self.log_output = tk.Text(main_frame, height=8, state=tk.DISABLED, wrap=tk.WORD)
        self.log_output.pack(fill=tk.BOTH, expand=True)

    def toggle_start_time(self):
        self._start_enabled = self.start_var.get()
        self.start_time_input.config(state=tk.NORMAL if self._start_enabled else tk.DISABLED)

    def toggle_end_time(self):
        self._end_enabled = self.end_var.get()
        self.end_time_input.config(state=tk.NORMAL if self._end_enabled else tk.DISABLED)

    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            return
        try:
            with open(SETTINGS_FILE, "r") as f:
                s = json.load(f)
        except (json.JSONDecodeError, IOError):
            return
        
        self.url_input.delete(0, tk.END)
        self.url_input.insert(0, s.get("url", ""))
        
        start_enabled = s.get("start_enabled", False)
        self.start_var.set(start_enabled)
        self.toggle_start_time()
        
        end_enabled = s.get("end_enabled", False)
        self.end_var.set(end_enabled)
        self.toggle_end_time()
        
        self.start_time_input.delete(0, tk.END)
        self.start_time_input.insert(0, s.get("start_time", ""))
        self.end_time_input.delete(0, tk.END)
        self.end_time_input.insert(0, s.get("end_time", ""))
        
        mode = s.get("mode", "video")
        self.mode_var.set(mode)
        
        quality = s.get("quality", "Best (HD)")
        self.quality_combo.set(quality)
        
        self.output_folder_input.delete(0, tk.END)
        self.output_folder_input.insert(0, s.get("output_folder", os.path.expanduser("~/Downloads")))

    def save_settings(self):
        s = {
            "url": self.get_url(),
            "start_enabled": self.start_var.get(),
            "start_time": self.get_start_time_str(),
            "end_enabled": self.end_var.get(),
            "end_time": self.get_end_time_str(),
            "mode": self.get_mode(),
            "quality": self.get_quality(),
            "output_folder": self.get_output_folder(),
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(s, f)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder_input.delete(0, tk.END)
            self.output_folder_input.insert(0, folder)

    def get_start_time_str(self):
        if not self.start_var.get():
            return ""
        return self.start_time_input.get().strip()

    def get_end_time_str(self):
        if not self.end_var.get():
            return ""
        return self.end_time_input.get().strip()

    def get_mode(self):
        return self.mode_var.get()

    def get_quality(self):
        return self.quality_combo.get()

    def get_output_folder(self):
        return self.output_folder_input.get().strip()

    def get_url(self):
        return self.url_input.get().strip()

    def set_downloading(self, is_downloading):
        state = tk.DISABLED if is_downloading else tk.NORMAL
        self.download_button.config(state=state)
        self.url_input.config(state=state)
        self.start_checkbox.config(state=state)
        self.start_time_input.config(state=state if self._start_enabled else tk.DISABLED)
        self.end_checkbox.config(state=state)
        self.end_time_input.config(state=state if self._end_enabled else tk.DISABLED)
        self.video_radio.config(state=state)
        self.audio_radio.config(state=state)
        self.quality_combo.config(state=state)
        self.output_folder_input.config(state=state)
        
        if is_downloading:
            self.progress_bar.start(10)
        else:
            self.progress_bar.stop()

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def show_info(self, message):
        messagebox.showinfo("Info", message)

    def append_log(self, message):
        self.log_output.config(state=tk.NORMAL)
        self.log_output.insert(tk.END, message + "\n")
        self.log_output.see(tk.END)
        self.log_output.config(state=tk.DISABLED)

    def on_close(self):
        self.save_settings()
        self.root.destroy()

    def run(self):
        self.root.mainloop()