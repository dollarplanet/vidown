# Vidown - Video Downloader

A simple video downloader application built with Python and tkinter GUI.

## Supported Platforms

- Windows
- Linux (Ubuntu and other distributions)

## Features

- Download videos from various platforms using yt-dlp
- Select output quality
- Choose between video or audio-only download
- Trim downloads with start/end time
- Progress tracking and logging

---

## Installation

### Windows

1. Download the latest release from the releases page
2. Extract the `vidown-windows.zip` file
3. Run `vidown.exe`

### Linux (Ubuntu/Debian)

#### Option 1: Using Pre-built Package

1. Download `vidown-linux.zip` from the releases page
2. Extract the archive:
   ```bash
   unzip vidown-linux.zip
   ```
3. Navigate to the extracted folder:
   ```bash
   cd vidown-linux
   ```
4. Make the executable runnable:
   ```bash
   chmod +x vidown/vidown
   ```
5. Run the application:
   ```bash
   ./vidown/vidown
   ```

#### Option 2: Add to Application Menu

1. Extract and set up as above
2. Copy the desktop file and icon:
   ```bash
   cp vidown.desktop ~/.local/share/applications/
   cp icon.png ~/.local/share/icons/
   ```
3. Update the desktop database:
   ```bash
   update-desktop-database ~/.local/share/applications/
   ```
4. Search for "Vidown" in your application menu

---

## Usage

### Interface Overview

1. **URL Input**: Enter the video URL
2. **Output Folder**: Select where to save the downloaded file
3. **Mode**: Choose between Video or Audio
4. **Quality**: Select the video quality (best, 1080p, 720p, 480p, etc.)
5. **Start/End Time** (optional): Set trim points in HH:MM:SS format
6. **Download**: Click the download button to start

### Downloading a Video

1. Enter the video URL in the URL field
2. Click "Browse" to select the output folder
3. Select the download mode (Video/Audio)
4. Choose the desired quality
5. Click "Download"
6. Wait for the download to complete

### Downloading Audio Only

1. Select "Audio" mode
2. Choose output folder
3. Click "Download"

### Trimming a Video

1. Enter URL and select output folder
2. Enter start time in HH:MM:SS format (e.g., 00:01:30)
3. Enter end time in HH:MM:SS format (e.g., 00:03:00)
4. Click "Download"

---

## Troubleshooting

### Linux: "Permission Denied" Error

```bash
chmod +x vidown/vidown
```

### Linux: Missing Libraries

If you get library errors, you may need to install additional dependencies:

```bash
sudo apt install libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0
```

### Common Issues

- **Invalid URL**: Make sure the URL is correct and complete
- **Download failed**: Some videos may have restrictions or require authentication
- **No space**: Ensure sufficient disk space in the output folder

---

## Building from Source

### Prerequisites

- Python 3.11+
- yt-dlp

### Install Dependencies

```bash
pip install yt-dlp pyinstaller
```

### Build

```bash
pyinstaller vidown.spec
```

---

## License

MIT License