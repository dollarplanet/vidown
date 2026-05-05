import os
import sys
import shutil
import zipfile
import urllib.request
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

FFMPEG_URLS = {
    "linux": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz",
    "win": "https://github.com/GyanD/codexffmpeg/releases/download/8.1.1/ffmpeg-8.1.1-essentials_build.zip",
}


def get_main_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    if sys.argv[0]:
        adir = os.path.dirname(os.path.abspath(sys.argv[0]))
        if adir:
            return adir
    return os.path.dirname(os.path.abspath(__file__))


def get_ffmpeg_path():
    main_dir = get_main_dir()
    ffmpeg_dir = os.path.join(main_dir, 'ffmpeg')
    if sys.platform == 'win32':
        ffmpeg_path = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
    else:
        ffmpeg_path = os.path.join(ffmpeg_dir, 'ffmpeg')
    
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    
    return None


def download_ffmpeg(progress_callback=None):
    main_dir = get_main_dir()
    ffmpeg_dir = os.path.join(main_dir, 'ffmpeg')
    
    if sys.platform == 'win32':
        ffmpeg_path = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
        url = FFMPEG_URLS["win"]
    else:
        ffmpeg_path = os.path.join(ffmpeg_dir, 'ffmpeg')
        url = FFMPEG_URLS["linux"]
    
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    
    if progress_callback:
        progress_callback("Downloading ffmpeg...")
    
    tmpfile = "/tmp/ffmpeg.tar.xz" if sys.platform != 'win32' else "/tmp/ffmpeg.zip"
    if os.path.exists(tmpfile):
        os.remove(tmpfile)
    
    os.makedirs(ffmpeg_dir, exist_ok=True)
    
    try:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, context=ctx) as response:
            total = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            chunk_size = 8192
            with open(tmpfile, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0 and progress_callback:
                        percent = int(downloaded * 100 / total)
                        progress_callback(f"Downloading ffmpeg... {percent}%")
    except Exception as e:
        if progress_callback:
            progress_callback(f"Failed to download ffmpeg: {e}")
        return None
    
    if progress_callback:
        progress_callback("Extracting ffmpeg...")
    
    try:
        if sys.platform == 'win32':
            with zipfile.ZipFile(tmpfile, 'r') as z:
                for name in z.namelist():
                    if 'ffmpeg.exe' in name and not name.endswith('/'):
                        z.extract(name, ffmpeg_dir)
                        src = os.path.join(ffmpeg_dir, name)
                        if os.path.exists(src) and src != ffmpeg_path:
                            os.rename(src, ffmpeg_path)
                        break
        else:
            import tarfile
            with tarfile.open(tmpfile, 'r:xz') as t:
                for member in t.getmembers():
                    if member.name.endswith('/bin/ffmpeg') and member.isfile():
                        t.extract(member, ffmpeg_dir)
                        src = os.path.join(ffmpeg_dir, member.name)
                        if os.path.exists(src):
                            shutil.copy(src, ffmpeg_path)
                            os.remove(src)
                        break
        
        os.chmod(ffmpeg_path, 0o755)
        if os.path.exists(tmpfile):
            os.remove(tmpfile)
    except Exception as e:
        if progress_callback:
            progress_callback(f"Failed to extract ffmpeg: {e}")
        return None
    
    if progress_callback:
        progress_callback("ffmpeg ready")
    
    return ffmpeg_path


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

            ffmpeg_path = get_ffmpeg_path()
            if not ffmpeg_path:
                self.progress_updated.emit("FFmpeg not found, downloading...")
                ffmpeg_path = download_ffmpeg(lambda msg: self.progress_updated.emit(msg))
                if not ffmpeg_path:
                    self.download_finished.emit(False, "Failed to download FFmpeg")
                    return

            opts = self.build_options(ffmpeg_path)
            self.progress_updated.emit(f"Downloading: {self.url}")

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url])

            self.download_finished.emit(True, "Download completed successfully")

        except Exception as e:
            self.download_finished.emit(False, f"Error: {str(e)}")

    def build_options(self, ffmpeg_path=None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_template = os.path.join(self.output_folder, f"%(title)s_{timestamp}.%(ext)s")

        opts = {
            "outtmpl": output_template,
            "format": QUALITY_FORMATS.get(self.quality, "best"),
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [self.progress_hook],
        }

        if not ffmpeg_path:
            ffmpeg_path = get_ffmpeg_path()
        if ffmpeg_path:
            opts["ffmpeg_location"] = ffmpeg_path

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