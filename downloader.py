import subprocess
import os
import re
from PySide6.QtCore import QObject, Signal, QThread


QUALITY_FORMATS = {
    "Best (HD)": "best",
    "1080p": "bv[height<=1080]+ba/b",
    "720p": "bv[height<=720]+ba/b",
    "480p": "bv[height<=480]+ba/b",
    "360p": "bv[height<=360]+ba/b",
}


class DownloaderWorker(QThread):
    progress_updated = Signal(str)
    download_finished = Signal(bool, str)

    def __init__(self, url, output_folder, mode, quality, start_time, end_time):
        super().__init__()
        self.url = url
        self.output_folder = output_folder
        self.mode = mode
        self.quality = quality
        self.start_time = start_time
        self.end_time = end_time
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            if not self.url.strip():
                self.download_finished.emit(False, "URL cannot be empty")
                return

            if not os.path.isdir(self.output_folder):
                self.download_finished.emit(False, f"Output folder does not exist: {self.output_folder}")
                return

            cmd = self.build_command()

            self.progress_updated.emit(f"Running: {' '.join(cmd)}\n")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in process.stdout:
                if self._cancelled:
                    process.terminate()
                    self.download_finished.emit(False, "Download cancelled")
                    return
                self.progress_updated.emit(line.strip())

            process.wait()

            if process.returncode == 0:
                self.download_finished.emit(True, "Download completed successfully")
            else:
                self.download_finished.emit(False, f"Download failed with exit code {process.returncode}")

        except Exception as e:
            self.download_finished.emit(False, f"Error: {str(e)}")

    def build_command(self):
        cmd = ["yt-dlp"]

        format_spec = QUALITY_FORMATS.get(self.quality, "best")

        if self.mode == "audio":
            cmd.extend(["-x", "--audio-format", "mp3"])
        else:
            cmd.extend(["--merge-output-format", "mp4"])

        cmd.extend(["-f", format_spec])

        if self.start_time or self.end_time:
            section = ""
            if self.start_time:
                section = f"*{self.start_time}-"
            if self.end_time and section:
                section += f"{self.end_time}"
            cmd.extend(["--download-sections", section])

        output_template = os.path.join(self.output_folder, "%(title)s.%(ext)s")
        cmd.extend(["-o", output_template])

        cmd.append(self.url)

        return cmd