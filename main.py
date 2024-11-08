import videoPlayer


if __name__ == "__main__":
    root = videoPlayer.tk.Tk()
    player = videoPlayer.VidPlayer(root)
    root.mainloop()