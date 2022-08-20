import dbus
import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

        
class VideoDownloader():
    def __init__(self, url, para):
        self.video_info = []
        self.url = url
        self.para = para
        self.id = 0

    def notify(self, icon, summary, body):
        bus = dbus.SessionBus().get_object("org.freedesktop.Notifications", "/org/freedesktop/Notifications")
        bus = dbus.Interface(bus, "org.freedesktop.Notifications")
        return bus.Notify("Youtube downloader",            # app name
                        self.id,                    # replaces id
                        icon,                       # app icon
                        summary,                    # summary
                        body,                       # body
                        [],
                        {},                         # hints
                        0)                          # expire timeout


    # TODO original notification is not replaced
    def progress_notify(self, d):
        if d['status'] == 'finished':
            self.notify(
                "/usr/share/icons/Adwaita/32x32/emblems/emblem-ok-symbolic.symbolic.png",         # app icon
                "Finished download",        # summary
                self.video_info['title'],   # body
            )
        

    def download(self):
        """downloads the video corresponding to the url and sends a notification"""

        # TODO add different codecs
        options = {
            'progress_hooks': [self.progress_notify],
            'outtmpl': "%(title)s.%(ext)s",
            'paths': {'home': self.para.path},
        }

        if self.para.type == "audio":
            extra_opt = {
                'format': 'm4a/bestaudio/best',
                'postprocessors': [{  # Extract audio using ffmpeg
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.para.format,
                }],
            }
        else: 
            extra_opt = {
                'format': "bv*[ext={0}]+ba[ext=m4a]/b[ext={0}] / bv*+ba/b".format(self.para.format),
            }
        
        options.update(extra_opt)

        # extract title and send notification
        with yt_dlp.YoutubeDL(options) as ydl:
            try:
                self.video_info = ydl.extract_info(self.url, download=False)
            except BaseException as err:
                print(err)
                return

        self.id = self.notify(
            "/usr/share/icons/Adwaita/32x32/places/folder-download-symbolic.symbolic.png",         # app icon
            "Downloading video",                 # summary
            self.video_info['title'],            # body
        )
        

        # download the video
        with yt_dlp.YoutubeDL(options) as ydl:
            try:
                ydl.download(self.url)
            except DownloadError as err:
                print(err)
                return