import sys
import tkinter as tk
from ui import MainWindow
from downloader import DownloaderWorker


class VidownApp(MainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.root.after(100, self._check_worker)

    def _check_worker(self):
        if self.worker and self.worker.is_alive():
            self.root.after(100, self._check_worker)

    def start_download(self):
        url = self.get_url()
        if not url:
            self.show_error("Please enter a video URL")
            return

        output_folder = self.get_output_folder()
        if not output_folder:
            self.show_error("Please select an output folder")
            return

        mode = self.get_mode()
        quality = self.get_quality()
        start_time = self.get_start_time_str()
        end_time = self.get_end_time_str()

        self.log_output.config(state=tk.NORMAL)
        self.log_output.delete("1.0", tk.END)
        self.log_output.config(state=tk.DISABLED)
        self.set_downloading(True)

        self.worker = DownloaderWorker(
            url=url,
            output_folder=output_folder,
            mode=mode,
            quality=quality,
            start_time=start_time,
            end_time=end_time,
            progress_callback=self.append_log,
            finished_callback=self._on_download_finished
        )
        self.worker.start()

    def _on_download_finished(self, success, message):
        self.set_downloading(False)
        if success:
            self.show_info(message)
        else:
            self.show_error(message)


def main():
    window = VidownApp()
    window.run()


if __name__ == "__main__":
    main()