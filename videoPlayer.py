import cv2
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
import vlc
import snscrape.modules.twitter as sntwitter
from pytube import YouTube
from yt_dlp import YoutubeDL
import time

class VidPlayer():

    def __init__(self, root):
        self.root = root
        self.root.title("Video Player")
        self.root.geometry("1920x1080")

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.downloaded_videos = []

        self.video_frame = tk.Frame(self.root, bg="black")
        self.video_frame.pack(fill=tk.BOTH, expand=1)

        self.canvas = tk.Canvas(self.video_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=1)

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack()

        self.play_button = tk.Button(self.control_frame, text="play", command=self.play_video)
        self.play_button.grid(row=0, column=0)

        self.pause_button = tk.Button(self.control_frame, text="pause", command=self.pause_video)
        self.pause_button.grid(row=0, column=1)

        self.stop_button = tk.Button(self.control_frame, text="stop", command=self.stop_video)
        self.stop_button.grid(row=0, column=2)

        self.fast_forward_button = tk.Button(self.control_frame, text="forward", command=self.fast_forward)
        self.fast_forward_button.grid(row=0, column=3)

        self.rewind_button = tk.Button(self.control_frame, text="rewind", command=self.rewind)
        self.rewind_button.grid(row=0, column=4)

        self.openFile_button = tk.Button(self.control_frame, text="file", command=self.open_file)
        self.openFile_button.grid(row=0, column=5)

        self.openUrl_button = tk.Button(self.control_frame, text="url", command=self.open_url)
        self.openUrl_button.grid(row=0, column=6)

        self.twitter_video_button = tk.Button(self.control_frame, text="Twitter Video", command=self.open_twitter_video)
        self.twitter_video_button.grid(row=0, column=7)

        # Set the media player to render the video in the Tkinter frame
        self.player.set_hwnd(self.canvas.winfo_id())

        # Register the event manager
        self.events = self.player.event_manager()
        self.events.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_end_reached)

        # Cleanup downloaded videos on application close
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup_on_exit)


    def play_video(self):
        if self.player.get_media():
            self.player.play()

    def pause_video(self):
        self.player.pause()

    def stop_video(self):
        self.player.stop()

    def fast_forward(self):
        curr_time = self.player.pygame.time.get_time()
        self.player.set_time(curr_time + 10000)

    def rewind(self):
        curr_time = self.player.time.get_time()
        self.player.set_time(curr_time - 10000)
        
    def open_file(self):
        self.video_path = filedialog.askopenfilename(title="select ur vid file", filetypes=[("Video Files", "*.mp4;*.avi")])
        if self.video_path:
            media = self.instance.media_new(self.video_path)
            self.player.set_media(media)
            self.play()

    def open_url(self):
        url = simpledialog.askstring("Open URL", "Enter video URL:")
        if url:
            if "youtube.com" in url or "youtu.be" in url:
                try:
                    print("Downloading from Youtube directly ...")
                    ydl_opts = {
                        'format': 'best[ext=mp4]/best',
                        'outtmpl': 'downloaded_video.mp4',  # File will be named 'downloaded_video.mp4'
                        'quiet': True  # Suppresses the download log
                    }
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download(url)

                    video_path = 'downloaded_video.mp4'
                    self.downloaded_videos.append(video_path)
                    print("Download complete. Playing video...")
                    self.player.set_media(self.instance.media_new(video_path))
                    self.play_video()
                except Exception as e:
                    print("Failed to download video:", e)
            else:
                # For non-YouTube URLs, try to stream directly
                try:
                    media = self.instance.media_new(url)
                    self.player.set_media(media)
                    time.sleep(0.1)  # Small delay for media initialization
                    self.play_video()
                except Exception as e:
                    print("Failed to stream video:", e)

    def open_twitter_video(self):
        tweet_url = simpledialog.askstring("Twitter Video", "Enter Twitter tweet URL:")
        if tweet_url:
            try:
                tweet_id = tweet_url.strip().split('/')[-1]
                tweet = next(sntwitter.TwitterTweetScraper(tweet_id).get_items())
                media_url = None
                for media in tweet.media:
                    if isinstance(media, sntwitter.Video):
                        media_url = media.variants[0].url  # Get the first variant URL
                        break

                if media_url:
                    youtube = YouTube(media_url)
                    video_stream = youtube.streams.filter(progressive=True, file_extension="mp4").first()
                    if video_stream:
                        video_path = video_stream.download(filename=f"twitter_video_{tweet_id}.mp4")
                        self.downloaded_videos.append(video_path)
                        self.player.set_media(self.instance.media_new(video_path))
                        self.play()
                    else:
                        print("No suitable video stream found.")
                else:
                    print("No video found in this tweet.")
            except Exception as e:
                print("Error downloading video:", e)

    def on_end_reached(self, event):
        # Cleanup the video file after playback ends
        self.cleanup_current_video()

    def cleanup_current_video(self):
        # Delete the current video if it is in the downloaded videos list
        current_media = self.player.get_media()
        if current_media:
            media_path = current_media.get_mrl().replace("file:///", "")
            if media_path in self.downloaded_videos:
                try:
                    if os.path.exists(media_path):
                        os.remove(media_path)
                        print(f"Deleted downloaded video: {media_path}")
                    self.downloaded_videos.remove(media_path)
                except Exception as e:
                    print("Error deleting video file:", e)

    def cleanup_on_exit(self):
        # Clean up all downloaded videos upon application exit
        for video_path in self.downloaded_videos:
            try:
                if os.path.exists(video_path):
                    os.remove(video_path)
                    print(f"Deleted downloaded video: {video_path}")
            except Exception as e:
                print(f"Error deleting video file {video_path}: {e}")
        self.root.destroy()

    def update(self):
        if not self.paused:
            ret, frame = self.cap.read()
            if ret:
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)