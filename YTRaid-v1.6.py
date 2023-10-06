# YTRaid Version 1.6
# A Python GUI program for downloading YouTube videos with choosable multiple qualities and paths
import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QComboBox, QFileDialog, QVBoxLayout, QMessageBox, QDialog, QLabel, QProgressBar
import pytube

class LoadingPopup(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Loading...")
        self.setGeometry(100, 100, 400, 100)  # Adjust the size here
        layout = QVBoxLayout()

        self.loading_label = QLabel("Finding Available Qualities For This Video")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Infinite progress

        layout.addWidget(self.loading_label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

class YouTubeVideoDownloader(QWidget):
    def __init__(self):
        super().__init__()

        # Create a layout for the GUI.
        layout = QVBoxLayout()

        # Create a line edit for the video URL.
        self.video_url_edit = QLineEdit()

        # Create a submit button to fetch available resolutions.
        self.submit_button = QPushButton('Submit')

        # Create a dropdown menu for the quality.
        self.quality_comboBox = QComboBox()

        # Create a button to download the video.
        self.download_button = QPushButton('Download')

        # Create a button to change the downloading path.
        self.change_download_path_button = QPushButton('Change Download Path')

        # Create a label to display the download path.
        self.download_path_label = QLineEdit()
        self.download_path_label.setText('C:/Desktop/YT-Raid')

        # Add the widgets to the layout.
        layout.addWidget(self.video_url_edit)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.quality_comboBox)
        layout.addWidget(self.download_button)
        layout.addWidget(self.change_download_path_button)
        layout.addWidget(self.download_path_label)

        # Set the layout of the GUI.
        self.setLayout(layout)

        # Connect the submit button to a slot to fetch resolutions.
        self.submit_button.clicked.connect(self.fetch_resolutions)

        # Connect the download button to a slot.
        self.download_button.clicked.connect(self.download_video)

        # Connect the change download path button to a slot.
        self.change_download_path_button.clicked.connect(self.change_download_path)

        # Initialize loading popup
        self.loading_popup = None

    def show_loading_popup(self):
        self.loading_popup = LoadingPopup()
        self.loading_popup.setModal(True)
        self.loading_popup.show()

    def close_loading_popup(self):
        if self.loading_popup:
            self.loading_popup.close()

    def fetch_resolutions(self):
        # Get the video URL from the line edit.
        video_url = self.video_url_edit.text()

        # Check if the video URL is valid.
        if not video_url.startswith('https://www.youtube.com/watch?v='):
            QMessageBox.warning(self, 'Invalid video URL', 'The video URL is not valid.')
            return

        # Show loading popup while fetching resolutions
        self.show_loading_popup()

        def fetch_resolutions_worker():
            try:
                youtube = pytube.YouTube(video_url)
                streams = youtube.streams.filter(progressive=True, file_extension="mp4")
                resolutions = set()
                for stream in streams:
                    resolutions.add(stream.resolution)
                resolutions_list = sorted(list(resolutions))
                self.quality_comboBox.clear()
                self.quality_comboBox.addItems(resolutions_list)
            except Exception as e:
                # Show an error message.
                QMessageBox.critical(self, 'Error', str(e))
            finally:
                # Close loading popup
                self.close_loading_popup()

        # Start a worker thread to fetch resolutions
        thread = threading.Thread(target=fetch_resolutions_worker)
        thread.start()

    def download_video(self):
        # Get the video URL from the line edit.
        video_url = self.video_url_edit.text()

        # Check if the video URL is valid.
        if not video_url.startswith('https://www.youtube.com/watch?v='):
            QMessageBox.warning(self, 'Invalid video URL', 'The video URL is not valid.')
            return

        # Get the quality to download from the dropdown menu.
        quality = self.quality_comboBox.currentText()

        # Get the download path from the label.
        download_path = self.download_path_label.text()

        # Download the video.
        try:
            download_video(video_url, quality=quality, output_dir=download_path)
        except Exception as e:
            # Show an error message.
            QMessageBox.critical(self, 'Error', str(e))
        else:
            # Show a success message.
            QMessageBox.information(self, 'Success', 'Video downloaded successfully!')

    def change_download_path(self):
        # Open a file dialog to select the new download path.
        new_download_path = QFileDialog.getExistingDirectory(self, 'Select Download Path')

        # Set the download path label to the new download path.
        self.download_path_label.setText(new_download_path)

def download_video(video_url, quality='highestres', output_dir='.'):
    """Downloads a YouTube video to the specified directory in the specified quality.

    Args:
       video_url: The URL of the YouTube video to download.
       output_dir: The directory where the downloaded video should be saved.
       quality: The quality of the video to download. Can be one of the following:
        - 'highestres': The highest resolution available.
        - 'highres': A high resolution video.
        - 'lowres': A low resolution video.
    """

    youtube = pytube.YouTube(video_url)
    stream = youtube.streams.filter(progressive=True, resolution=quality, file_extension="mp4").first()

    if stream:
        stream.download(output_dir)
    else:
        raise Exception("Selected quality is unavailable for this video.")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create the GUI.
    window = YouTubeVideoDownloader()

    # Show the GUI.
    window.show()

    # Start the main loop
    sys.exit(app.exec_())
