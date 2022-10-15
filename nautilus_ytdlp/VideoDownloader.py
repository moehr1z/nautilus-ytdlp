import yt_dlp
from multiprocessing import Process, Queue
import winotify
import os

file_path = os.path.realpath(__file__)
r = winotify.Registry("Video Downloader", winotify.PY_EXE, repr(file_path))
notifier = winotify.Notifier(r)
        
class VideoDownloader():
    def __init__(self, url, para):
        self.video_info = []
        self.url = url
        self.para = para
        self.ret_q = Queue()
        notifier.start()

    @notifier.register_callback
    def cancel_download(self, *_):
        self.ret_q.put("cancelled")
        self.proc.terminate()

        
    def ydl_dwl(self):
        with yt_dlp.YoutubeDL(options) as ydl:
            ret_code = ydl.download(self.url)
            self.ret_q.put(ret_code)


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
                ntfc = notifier.create_notification(
                    title="Error downloading video",
                    msg=repr(err),
                    duration="long",
                )
                ntfc.show()
                
                return

        ntfc = notifier.create_notification(
            title="Downloading Video",
            msg=self.video_info['title'],
            duration="long",
        )
        ntfc.add_actions(
            label="Cancel",
            launch=self.cancel_download,
        )
        ntfc.show()

        # download the video
        self.proc = Thread(target=self.ydl_dwl, args=())
        self.proc.start()
            
        self.proc.join()
        code = self.ret_q.get()
        ntfc.close()
        if code == "cancelled":
            ntfc = notifier.create_notification(
                title="Canceled download",
                msg=self.video_info['title'],
                duration="long",
            )
        elif code:
            ntfc = notifier.create_notification(
                title="Error downloading video",
                msg=repr(err),
                duration="long",
            )
        else:
            ntfc = notifier.create_notification(
                title="Finished download",
                msg=self.video_info['title'],
                duration="long",
            )

        ntfc.show()

        
