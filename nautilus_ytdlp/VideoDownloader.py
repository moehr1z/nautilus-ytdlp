import yt_dlp
from winotify import Notification
import os

class VideoDownloader():
    def __init__(self, url, para):
        self.video_info = []
        self.url = url
        self.para = para
        
    def ydl_dwl(self, options):
        with yt_dlp.YoutubeDL(options) as ydl:
            ret_code = ydl.download(self.url)
            return ret_code

    def download(self):
        """downloads the video corresponding to the url and sends a notification"""
            
        # TODO add different codecs
        options = {
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
                ntfc = Notification(
                    app_id="Video Downloader",
                    title="Error downloading video",
                    msg=repr(err),
                    duration="long",
                )
                ntfc.show()
                
                return

        ntfc = Notification(
            app_id="Video Downloader",
            title="Downloading Video",
            msg=self.video_info['title'],
            duration="long",
        )
        ntfc.show()

        # download the video
        code = self.ydl_dwl(options)
            
        if code:
            ntfc = Notification(
                app_id="Video Downloader",
                title="Error downloading video",
                msg=repr(err),
                duration="long",
            )
        else:
            ntfc = Notification(
                app_id="Video Downloader",
                title="Finished download",
                msg=self.video_info['title'],
                duration="long",
            )

        ntfc.show()

        
