from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QRadioButton, QTimeEdit, QFileDialog, QTextEdit,
    QProgressBar, QGroupBox, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt, QTime
import json
import os


SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "value.json")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vidown - YouTube Downloader")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        url_layout = QVBoxLayout()
        url_layout.addWidget(QLabel("Video URL"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        url_layout.addWidget(self.url_input)
        main_layout.addLayout(url_layout)

        time_group = QGroupBox("Start / End Time (HH:MM:SS)")
        time_layout = QVBoxLayout()

        start_layout = QHBoxLayout()
        self.start_checkbox = QCheckBox("Start:")
        self.start_time_input = QLineEdit()
        self.start_time_input.setPlaceholderText("00:00:00")
        start_layout.addWidget(self.start_checkbox)
        start_layout.addWidget(self.start_time_input)
        time_layout.addLayout(start_layout)

        end_layout = QHBoxLayout()
        self.end_checkbox = QCheckBox("End:")
        self.end_time_input = QLineEdit()
        self.end_time_input.setPlaceholderText("00:00:00")
        end_layout.addWidget(self.end_checkbox)
        end_layout.addWidget(self.end_time_input)
        time_layout.addLayout(end_layout)

        time_group.setLayout(time_layout)
        main_layout.addWidget(time_group)

        mode_group = QGroupBox("Mode")
        mode_layout = QHBoxLayout()
        self.video_radio = QRadioButton("Video")
        self.video_radio.setChecked(True)
        self.audio_radio = QRadioButton("Audio")
        mode_layout.addWidget(self.video_radio)
        mode_layout.addWidget(self.audio_radio)
        mode_layout.addStretch()
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)

        quality_layout = QVBoxLayout()
        quality_layout.addWidget(QLabel("Quality"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "Best (HD)",
            "1080p",
            "720p",
            "480p",
            "360p",
        ])
        quality_layout.addWidget(self.quality_combo)
        main_layout.addLayout(quality_layout)

        output_layout = QVBoxLayout()
        output_layout.addWidget(QLabel("Output Folder"))
        output_folder_layout = QHBoxLayout()
        self.output_folder_input = QLineEdit()
        self.output_folder_input.setText("/home/riyan/Downloads")
        output_folder_layout.addWidget(self.output_folder_input)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        output_folder_layout.addWidget(self.browse_button)
        output_layout.addLayout(output_folder_layout)
        main_layout.addLayout(output_layout)

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.start_download)
        main_layout.addWidget(self.download_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("Log"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        log_layout.addWidget(self.log_output)
        main_layout.addLayout(log_layout)

        self.setLayout(main_layout)

    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            return
        try:
            with open(SETTINGS_FILE, "r") as f:
                s = json.load(f)
        except (json.JSONDecodeError, IOError):
            return
        self.url_input.setText(s.get("url", ""))
        self.start_checkbox.setChecked(s.get("start_enabled", False))
        self.start_time_input.setText(s.get("start_time", ""))
        self.end_checkbox.setChecked(s.get("end_enabled", False))
        self.end_time_input.setText(s.get("end_time", ""))
        if s.get("mode") == "audio":
            self.audio_radio.setChecked(True)
        else:
            self.video_radio.setChecked(True)
        quality = s.get("quality", "Best (HD)")
        index = self.quality_combo.findText(quality)
        if index >= 0:
            self.quality_combo.setCurrentIndex(index)
        self.output_folder_input.setText(s.get("output_folder", "/home/riyan/Downloads"))

    def save_settings(self):
        s = {
            "url": self.get_url(),
            "start_enabled": self.start_checkbox.isChecked(),
            "start_time": self.get_start_time_str(),
            "end_enabled": self.end_checkbox.isChecked(),
            "end_time": self.get_end_time_str(),
            "mode": self.get_mode(),
            "quality": self.get_quality(),
            "output_folder": self.get_output_folder(),
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(s, f)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder_input.setText(folder)

    def get_start_time_str(self):
        if not self.start_checkbox.isChecked():
            return ""
        return self.start_time_input.text().strip()

    def get_end_time_str(self):
        if not self.end_checkbox.isChecked():
            return ""
        return self.end_time_input.text().strip()

    def get_mode(self):
        return "audio" if self.audio_radio.isChecked() else "video"

    def get_quality(self):
        return self.quality_combo.currentText()

    def get_output_folder(self):
        return self.output_folder_input.text().strip()

    def get_url(self):
        return self.url_input.text().strip()

    def set_downloading(self, is_downloading):
        self.download_button.setEnabled(not is_downloading)
        self.url_input.setEnabled(not is_downloading)
        self.start_checkbox.setEnabled(not is_downloading)
        self.start_time_input.setEnabled(not is_downloading)
        self.end_checkbox.setEnabled(not is_downloading)
        self.end_time_input.setEnabled(not is_downloading)
        self.video_radio.setEnabled(not is_downloading)
        self.audio_radio.setEnabled(not is_downloading)
        self.quality_combo.setEnabled(not is_downloading)
        self.output_folder_input.setEnabled(not is_downloading)
        self.browse_button.setEnabled(not is_downloading)
        self.progress_bar.setVisible(is_downloading)
        if is_downloading:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(0)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message):
        QMessageBox.information(self, "Info", message)

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)