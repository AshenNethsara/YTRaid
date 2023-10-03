# YTRaid First Release
# A Python GUI program for downloading YouTube videos with choosable multiple qualities

# Importing the required modules
import tkinter as tk
import pytube

# Creating the main window
window = tk.Tk()
window.title("YouTube Downloader")
window.geometry("600x400")

# Creating the widgets
url_label = tk.Label(window, text="Enter the YouTube video URL:")
url_entry = tk.Entry(window, width=50)
quality_label = tk.Label(window, text="Choose the video quality:")
quality_var = tk.StringVar(window)
quality_var.set("720p")
quality_menu = tk.OptionMenu(window, quality_var, "1080p", "720p", "480p", "360p", "240p", "144p")
download_button = tk.Button(window, text="Download", command=lambda: download_video(url_entry.get(), quality_var.get()))
status_label = tk.Label(window, text="")

# Placing the widgets on the window
url_label.pack(pady=10)
url_entry.pack(pady=10)
quality_label.pack(pady=10)
quality_menu.pack(pady=10)
download_button.pack(pady=10)
status_label.pack(pady=10)

# Defining the function to download the video
def download_video(url, quality):
    # Try to create a YouTube object with the given URL
    try:
        video = pytube.YouTube(url)
    # If the URL is invalid, show an error message and return
    except:
        status_label.config(text="Invalid URL. Please enter a valid YouTube video URL.", fg="red")
        return
    # Get the stream object with the given quality
    stream = video.streams.filter(res=quality).first()
    # If the stream is not available, show an error message and return
    if stream is None:
        status_label.config(text=f"Video quality {quality} is not available for this video. Please choose another quality.", fg="red")
        return
    # Show a message that the download is starting
    status_label.config(text=f"Downloading {video.title} in {quality} quality...", fg="green")
    # Download the stream to the current directory
    stream.download()
    # Show a message that the download is complete
    status_label.config(text=f"Download complete. You can find the video in {stream.default_filename}.", fg="green")

# Running the main loop
window.mainloop()