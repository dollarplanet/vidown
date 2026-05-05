from PySide6.QtWidgets import QApplication
import sys
from ui import MainWindow
from downloader import DownloaderWorker


class VidownApp(MainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None

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

        self.log_output.clear()
        self.set_downloading(True)

        self.worker = DownloaderWorker(
            url=url,
            output_folder=output_folder,
            mode=mode,
            quality=quality,
            start_time=start_time,
            end_time=end_time
        )
        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.download_finished.connect(self.on_download_finished)
        self.worker.start()

    def on_progress_updated(self, line):
        self.log_output.append(line)
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_download_finished(self, success, message):
        self.set_downloading(False)
        if success:
            self.show_info(message)
        else:
            self.show_error(message)


def main():
    app = QApplication(sys.argv)
    window = VidownApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()