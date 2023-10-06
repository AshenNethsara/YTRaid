import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QComboBox, QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog, QLabel, QProgressBar
from PyQt5.QtCore import pyqtSignal, QObject
import pytube
import requests

class LoadingPopup(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Loading...")
        self.setGeometry(100, 100, 400, 100)
        layout = QVBoxLayout()

        self.loading_label = QLabel("Finding Available Qualities For This Video")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Infinite progress

        layout.addWidget(self.loading_label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

class MessageHandler(QObject):
    show_warning_signal = pyqtSignal(str, str)

class YouTubeVideoDownloader(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Create a horizontal layout for the video URL input and "Submit" button.
        url_layout = QHBoxLayout()

        self.video_url_edit = QLineEdit()
        self.placeholder_text = "Enter a valid YouTube link"
        self.video_url_edit.setPlaceholderText(self.placeholder_text)

        url_layout.addWidget(self.video_url_edit)

        self.submit_button = QPushButton('Submit')
        self.submit_button.setFixedWidth(60)  # Set the fixed width to make it smaller
        url_layout.addWidget(self.submit_button)

        layout.addLayout(url_layout)

        self.quality_comboBox = QComboBox()

        self.download_button = QPushButton('Download')

        self.change_download_path_button = QPushButton('Change Download Path')

        self.download_path_label = QLineEdit()
        self.download_path_label.setText('C:/Desktop/YT-Raid')

        layout.addWidget(self.quality_comboBox)
        layout.addWidget(self.download_button)
        layout.addWidget(self.change_download_path_button)
        layout.addWidget(self.download_path_label)

        self.setLayout(layout)

        self.submit_button.clicked.connect(self.fetch_resolutions)
        self.download_button.clicked.connect(self.download_video)
        self.change_download_path_button.clicked.connect(self.change_download_path)

        self.loading_popup = None

        self.message_handler = MessageHandler()
        self.message_handler.show_warning_signal.connect(self.show_warning_message)

    def show_loading_popup(self):
        self.loading_popup = LoadingPopup()
        self.loading_popup.setModal(True)
        self.loading_popup.show()

    def close_loading_popup(self):
        if self.loading_popup:
            self.loading_popup.close()

    def fetch_resolutions(self):
        try:
            requests.get("http://www.google.com")
        except requests.ConnectionError:
            self.message_handler.show_warning_signal.emit(
                "No Internet Connection",
                "Please check your internet connection and try again."
            )
            return

        video_url = self.video_url_edit.text()

        if not video_url.startswith('https://www.youtube.com/watch?v='):
            self.message_handler.show_warning_signal.emit(
                "Invalid Video URL",
                "The video URL is not valid. Please enter a valid YouTube link."
            )
            return

        self.show_loading_popup()

        def fetch_resolutions_worker():
            try:
                youtube = pytube.YouTube(video_url)
                streams = youtube.streams.filter(progressive=True, file_extension="mp4")

                # Define the desired resolutions
                desired_resolutions = ["144p", "360p", "480p", "720p", "1080p"]

                # Create a list to store unique resolutions
                resolutions = set()

                # Loop through the streams and add resolutions to the set
                for stream in streams:
                    resolutions.add(stream.resolution)

                # Include the desired resolutions and keep available quality
                resolutions_list = sorted(list(resolutions.union(desired_resolutions)))

                self.quality_comboBox.clear()
                self.quality_comboBox.addItems(resolutions_list)
            except Exception as e:
                self.message_handler.show_warning_signal.emit("Error", str(e))
            finally:
                self.close_loading_popup()

        thread = threading.Thread(target=fetch_resolutions_worker)
        thread.start()

    def download_video(self):
        video_url = self.video_url_edit.text()

        if not video_url.startswith('https://www.youtube.com/watch?v='):
            self.message_handler.show_warning_signal.emit(
                "Invalid Video URL",
                "The video URL is not valid. Please enter a valid YouTube link."
            )
            return

        quality = self.quality_comboBox.currentText()
        download_path = self.download_path_label.text()

        try:
            download_video(video_url, quality=quality, output_dir=download_path)
        except Exception as e:
            self.message_handler.show_warning_signal.emit("Error", str(e))
        else:
            QMessageBox.information(self, 'Success', 'Video downloaded successfully!')

    def change_download_path(self):
        new_download_path = QFileDialog.getExistingDirectory(self, 'Select Download Path')
        self.download_path_label.setText(new_download_path)

    def show_warning_message(self, title, message):
        QMessageBox.warning(self, title, message)

def download_video(video_url, quality='highestres', output_dir='.'):
    try:
        youtube = pytube.YouTube(video_url)
        streams = youtube.streams.filter(progressive=True, file_extension="mp4")
        resolutions = set()
        for stream in streams:
            resolutions.add(stream.resolution)
        resolutions_list = sorted(list(resolutions))
        if not resolutions_list:
            raise Exception("No video resolutions available.")
        quality = resolutions_list[-1]  # Select the highest available resolution
        stream = streams.filter(resolution=quality).first()

        if stream:
            stream.download(output_dir)
        else:
            raise Exception("Selected quality is unavailable for this video.")
    except Exception as e:
        raise Exception(str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YouTubeVideoDownloader()
    window.show()
    window.setWindowTitle("YTRaid - YouTube Downloader")
    sys.exit(app.exec_())
