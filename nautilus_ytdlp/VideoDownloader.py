import dbus
import yt_dlp


class VideoDownloader():
    def __init__(self, url, para):
        self.video_info = []
        self.url = url
        self.para = para


    def notify(self, d):
        if d['status'] == 'finished':
            bus = dbus.SessionBus().get_object("org.freedesktop.Notifications", "/org/freedesktop/Notifications")
            bus = dbus.Interface(bus, "org.freedesktop.Notifications")
            bus.Notify("Youtube downloader",            # app name
                            self.id,                    # replaces id
                            "/usr/share/icons/Adwaita/32x32/emblems/emblem-ok-symbolic.symbolic.png",         # app icon
                            "Finished download",        # summary
                            self.video_info['title'],   # body
                            [],
                            {},                         # hints
                            0)                          # expire timeout
        

    def download(self):
        """downloads the video corresponding to the url and sends a notification"""

        options = {}

        # TODO use proper formats
        # TODO download to proper path
        if self.para.type == "audio":
            options = {
                'progress_hooks': [self.notify],
                'format': 'm4a/bestaudio/best',
                # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
                'postprocessors': [{  # Extract audio using ffmpeg
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                }],
                'outtmpl': "%(title)s.%(ext)s",
            }
        else: 
            options = {
                'progress_hooks': [self.notify],
                'format_sort': ['ext'],
                'outtmpl': "%(title)s.%(ext)s",
            }

        # extract title and send notification
        with yt_dlp.YoutubeDL(options) as ydl:
            self.video_info = ydl.extract_info(self.url, download=False)

        bus = dbus.SessionBus().get_object("org.freedesktop.Notifications", "/org/freedesktop/Notifications")
        bus = dbus.Interface(bus, "org.freedesktop.Notifications")
        self.id = bus.Notify("Youtube downloader",       # app name
                    0,                                   # replaces id
                    "/usr/share/icons/Adwaita/32x32/places/folder-download-symbolic.symbolic.png",         # app icon
                    "Downloading video",                 # summary
                    self.video_info['title'],            # body
                    [],
                    {},                                  # hints
                    0)                                   # expire timeout
        

        # download the video
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download(self.url)