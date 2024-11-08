import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import vlc

class VidPlayer():

    def __init__(self, root):
        self.root = root
        self.root.title("Video Player")
        self.root.geometry("1920x1080")

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

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
        self.stop_button.grid(row=0, column=3)

        self.rewind_button = tk.Button(self.control_frame, text="rewind", command=self.rewind)
        self.stop_button.grid(row=0, column=4)

        self.openFile_button = tk.Button(self.control_frame, text="file", command=self.open_file)
        self.stop_button.grid(row=0, column=5)

        self.openUrl_button = tk.Button(self.control_frame, text="url", command=self.open_url)
        self.stop_button.grid(row=0, column=6)

        self.player.set_hwnd(self.canvas.winfo_id())

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
        file_path = filedialog.askopenfilename()
        if file_path:
            media = self.instance.media_new(file_path)
            self.player.set_media(media)
            self.play()

    def update(self):
        if not self.paused:
            ret, frame = self.cap.read()
            if ret:
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)