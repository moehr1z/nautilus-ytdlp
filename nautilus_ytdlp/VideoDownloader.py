import yt_dlp
from yt_dlp.utils import DownloadError
from multiprocessing import Process, Queue

from dbus.mainloop.glib import DBusGMainLoop

import gi
from gi.repository import Notify
gi.require_version('Notify', '0.7')
        
class VideoDownloader():
    def __init__(self, url, para):
        self.video_info = []
        self.url = url
        self.para = para
        self.ret_q = Queue()

    def cancel_download(self, *_):
        self.ret_q.put("cancelled")
        self.proc.terminate()

        
    def ydl_dwl(self, ydl):
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
                ntfc = Notify.Notification.new(
                    "Error downloading video",
                    repr(err),
                    "/usr/share/icons/Adwaita/32x32/emblems/emblem-important-symbolic.symbolic.png"
                )
                ntfc.set_timeout(0)
                ntfc.show()
                
                return

        ntfc = Notify.Notification.new(
            "Downloading video",
            self.video_info['title'],            
            "/usr/share/icons/Adwaita/32x32/places/folder-download-symbolic.symbolic.png",        
        )
        ntfc.add_action(
            "action_click",
            "Cancel",
            self.cancel_download,
            None # Arguments
        )
        ntfc.set_timeout(0)
        ntfc.show()

        # download the video
        with yt_dlp.YoutubeDL(options) as ydl:
            self.proc = Process(target=self.ydl_dwl, args=(ydl,))
            self.proc.start()
            
        self.proc.join()
        code = self.ret_q.get()
        ntfc.close()
        if code == "cancelled":
            ntfc = Notify.Notification.new(
                "Canceled download",
                self.video_info['title'],            
                "/usr/share/icons/Adwaita/32x32/emblems/emblem-important-symbolic.symbolic.png",        
            )
        elif code:
            ntfc = Notify.Notification.new(
                "Error downloading video",
                repr(err),
                "/usr/share/icons/Adwaita/32x32/emblems/emblem-important-symbolic.symbolic.png"
            )
        else:
            ntfc = Notify.Notification.new(
                "Finished download",
                self.video_info['title'],   
                "/usr/share/icons/Adwaita/32x32/emblems/emblem-ok-symbolic.symbolic.png",      
            )

        ntfc.show()
        ntfc.set_timeout(0)

            
