import os
from datetime import datetime
from PySide6.QtCore import QThread, Signal
import yt_dlp
import tempfile


QUALITY_FORMATS = {
    "Best (HD)": "best",
    "1080p": "bv[height<=1080]+ba/b",
    "720p": "bv[height<=720]+ba/b",
    "480p": "bv[height<=480]+ba/b",
    "360p": "bv[height<=360]+ba/b",
}


def get_temp_config():
    node_path = os.path.expanduser("~/.nvm/versions/node/v22.21.1/bin/node")
    if os.path.exists(node_path):
        config = f"--js-runtimes=node:{node_path}"
    else:
        config = ""
    
    config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False)
    config_file.write(config)
    config_file.close()
    return config_file.name


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

            opts = self.build_options()
            self.progress_updated.emit(f"Downloading: {self.url}")

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url])

            self.download_finished.emit(True, "Download completed successfully")

        except Exception as e:
            self.download_finished.emit(False, f"Error: {str(e)}")

    def build_options(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_template = os.path.join(self.output_folder, f"%(title)s_{timestamp}.%(ext)s")

        opts = {
            "outtmpl": output_template,
            "format": QUALITY_FORMATS.get(self.quality, "best"),
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [self.progress_hook],
        }

        config_file = get_temp_config()
        opts["config_location"] = config_file

        if self.mode == "audio":
            opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }]
        else:
            opts["merge_output_format"] = "mp4"

        if self.start_time or self.end_time:
            start_seconds = self.parse_time(self.start_time)
            end_seconds = self.parse_time(self.end_time)
            opts["download_ranges"] = self._make_ranges(start_seconds, end_seconds)

        return opts

    def parse_time(self, time_str):
        if not time_str:
            return None
        parts = time_str.split(":")
        if len(parts) == 3:
            h, m, s = map(int, parts)
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:
            m, s = map(int, parts)
            return m * 60 + s
        return 0

    def _make_ranges(self, start, end):
        def get_ranges(info, ydl):
            ranges = []
            if start is not None:
                range_dict = {"start_time": start}
                if end is not None:
                    range_dict["end_time"] = end
                ranges.append(range_dict)
            return tuple(ranges)
        return get_ranges

    def progress_hook(self, d):
        if self._cancelled:
            raise Exception("Download cancelled")

        if d["status"] == "downloading":
            percent = d.get("_percent_str", "")
            if percent:
                self.progress_updated.emit(f"Downloading: {percent}")
        elif d["status"] == "finished":
            self.progress_updated.emit("Downloaded: " + d.get("filename", ""))