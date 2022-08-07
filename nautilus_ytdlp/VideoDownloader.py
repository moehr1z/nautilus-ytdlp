import dbus
import os
import yt_dlp

class VideoDownloader():
    def __init__(self):
        self.id = str(os.getpid())     # TODO unique id
        self.bus = dbus.SessionBus().get_object("org.freedesktop.Notifications", "/org/freedesktop/Notifications")
        self.bus = dbus.Interface(self.bus, "org.freedesktop.Notifications")
        self.video_info = []


    def notify(self, d):
        if d['status'] == 'finished':
            self.bus.Notify("Youtube downloader",       # app name
                            self.id,                    # replaces id
                            "/usr/share/icons/Adwaita/32x32/emblems/emblem-ok-symbolic.symbolic.png",         # TODO icon     # app icon
                            "Finished download",        # summary
                            self.video_info['title'],   # body
                            [],
                            {},                         # hints
                            1000000)                    # expire timeout
        

    def download(self, url: str, para: VideoParams):
        """downloads the video corresponding to the url and sends a notification"""

        options = {}

        # TODO use proper formats
        if para.type == "audio":
            options = {
                'format': 'm4a/bestaudio/best',
                # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
                'postprocessors': [{  # Extract audio using ffmpeg
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                }],
                'outtmpl': "%(title)s .%(ext)s",
            }
        else: 
            options = {
                # 'progress_hooks': [self.notify],
                'format_sort': ['ext'],
                'outtmpl': "%(title)s .%(ext)s",
            }

        # extract title and send notification
        with yt_dlp.YoutubeDL(options) as ydl:
            self.video_info = ydl.extract_info(url, download=False)

        # TODO the message only gets sent, when the process is joined above...weird
        self.id = self.bus.Notify("Youtube downloader",       # app name
                        0,                    # replaces id
                        "/usr/share/icons/Adwaita/32x32/places/folder-download-symbolic.symbolic.png",         # TODO icon     # app icon
                        "Downloading video",        # summary
                        self.video_info['title'],   # body
                        [],
                        {},                         # hints
                        1000000)                          # expire timeout

        # download the video
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download(url)