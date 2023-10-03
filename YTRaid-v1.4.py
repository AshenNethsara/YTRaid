# YTRaid Version 1.4
# A Python GUI program for downloading YouTube videos with choosable multiple qualities and paths
# The UI is upgraded to match the Windows 11 theme and a progress bar is added

# Importing the required modules
import tkinter as tk
import pytube
import os
import tkinter.filedialog
import threading
import tkinter.ttk

# Creating the main window
window = tk.Tk()
window.title("YouTube Downloader")
window.geometry("600x400")

# Setting the style of the widgets to match the Windows 11 theme
style = tkinter.ttk.Style()
style.theme_use("vista")
style.configure("TLabel", font=("Segoe UI Black", 12))
style.configure("TEntry", font=("Segoe UI Black", 12))
style.configure("TButton", font=("Segoe UI Black", 12))
style.configure("TProgressbar", thickness=10)

# Creating the widgets
url_label = tkinter.ttk.Label(window, text="Enter the YouTube video URL:")
url_entry = tkinter.ttk.Entry(window, width=50)
quality_label = tkinter.ttk.Label(window, text="Choose the video quality:")
quality_var = tk.StringVar(window)
quality_var.set("720p")
quality_menu = tkinter.ttk.OptionMenu(window, quality_var, "1080p", "720p", "480p", "360p", "240p", "144p")
path_label = tkinter.ttk.Label(window, text="Choose the download path:")
path_entry = tkinter.ttk.Entry(window, width=50)
path_button = tkinter.ttk.Button(window, text="Browse", command=lambda: browse_path(path_entry))
download_button = tkinter.ttk.Button(window, text="Download", command=lambda: threading.Thread(target=download_video, args=(url_entry.get(), quality_var.get(), path_entry.get())).start())
status_label = tkinter.ttk.Label(window, text="")
progress_bar = tkinter.ttk.Progressbar(window, orient=tk.HORIZONTAL, mode="determinate")

# Placing the widgets on the window
url_label.pack(pady=10)
url_entry.pack(pady=10)
quality_label.pack(pady=10)
quality_menu.pack(pady=10)
path_label.pack(pady=10)
path_entry.pack(pady=10)
path_button.pack(pady=10)
download_button.pack(pady=10)
status_label.pack(pady=10)
progress_bar.pack(pady=10, fill=tk.X)

# Defining the function to browse the download path
def browse_path(entry):
    # Use tkinter filedialog to ask for a directory
    path = tkinter.filedialog.askdirectory()
    # If a path is selected, insert it into the entry widget
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

# Defining the function to update the progress bar
def update_progress(stream, chunk, bytes_remaining):
    # Calculate the percentage of completion
    percentage = (stream.filesize - bytes_remaining) / stream.filesize * 100
    # Update the progress bar value and text
    progress_bar["value"] = percentage
    progress_bar["text"] = f"{percentage:.2f}%"

# Defining the function to download the video
def download_video(url, quality, path):
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
    # If the path is empty, use the current directory as the default path
    if not path:
        path = os.getcwd()
    # Show a message that the download is starting and reset the progress bar value and text
    status_label.config(text=f"Downloading {video.title} in {quality} quality to {path}...", fg="green")
    progress_bar["value"] = 0
    progress_bar["text"] = ""
    # Download the stream to the given path and register a callback function to update the progress bar
    stream.download(path, on_progress_callback=update_progress)
    # Show a message that the download is complete and set the progress bar value and text to 100%
    status_label.config(text=f"Download complete. You can find the video in {os.path.join(path, stream.default_filename)}.", fg="green")
    progress_bar["value"] = 100
    progress_bar["text"] = "100%"

# Running the main loop
try: # Adding a try-except block to catch the error
    window.mainloop()
except AttributeError as e: # Catching the AttributeError and printing the error message
    print(f"An error occurred: {e}")