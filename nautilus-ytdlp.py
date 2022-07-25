import gi
gi.require_version('Notify', '0.7')
gi.require_version('GObject', '2.0')
gi.require_version('GLib', '2.0')
gi.require_version('Nautilus', '3.0')
from gi.repository import Nautilus, GObject, Gtk, GLib, Notify
import subprocess 
from multiprocessing import Process
import urllib.request
import json
import urllib
import pprint
import yt_dlp
import dbus

class EntryWindow(Gtk.Window):
    """Class for the url prompt entry"""

    def __init__(self):
        self.url = ""   # the url entered, initially empty


        super().__init__(title="Video downloader")
        self.set_size_request(400, 100)
        # TODO attach to main window

        self.timeout_id = None

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter video url")
        vbox.pack_start(self.entry, True, True, 0)

        hbox = Gtk.Box(spacing=6)
        vbox.pack_start(hbox, True, True, 0)

        self.entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "system-search-symbolic")
         
        self.button_download = Gtk.Button(label="Download")
        hbox.pack_start(self.button_download, True, True, 0)
        
class VideoParams:
    """Describes parameters for a video"""
    def __init__(self, type, format, path):
        self.type = type
        self.format = format
        self.path = path

class VideoDownloader(GObject.GObject):

    def cancel_download():
        return 0

    def download(self, url: str, para: VideoParams):
        """downloads the video corresponding to the url and sends a notification"""

        # download video
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
                'format_sort': ['ext'],
                'outtmpl': "%(title)s .%(ext)s",
            }

        with yt_dlp.YoutubeDL(options) as ydl:
            video_info = ydl.extract_info(url, download=False)

        obj = dbus.SessionBus().get_object("org.freedesktop.Notifications", "/org/freedesktop/Notifications")
        obj = dbus.Interface(obj, "org.freedesktop.Notifications")
        obj.Notify( "Youtube downloader",       # app name
                    0,                          # replaces id
                    "",         # TODO icon     # app icon
                    "Downloading video",        # summary
                    video_info['title'],        # body
                    ['1', 'Cancel'],         #  TODO org.freedesktop.Notifications.ActionInvoked # actions
                    {"urgency": 1},             # hints
                    10000)                      # expire timeout


        # TODO exit process



class YTDLPExtension(GObject.GObject, Nautilus.MenuProvider, Nautilus.LocationWidgetProvider):
    """A context menu for ytdlp"""

    def __init__(self):
        GObject.Object.__init__(self)

    def create_prompt(self, menu, file, type, format):
        # initialize video params
        path = str(file.get_uri())
        path = path.split("file://")[1]
        para = VideoParams(type, format, path)        

        # create url entry prompt
        url_prompt = EntryWindow()
        url_prompt.connect("destroy", Gtk.main_quit)
        url_prompt.show_all()
        url_prompt.button_download.connect("pressed", self.on_download_pressed, url_prompt, para)


    def on_download_pressed(self, button, prompt, para):
        # get entered video url from entry
        video_url = prompt.entry.get_buffer().get_text()
        
        # make url list
        video_url = video_url.split()

        # download every video in a seperate thread
        for url in video_url:
            # TODO the process doesnt terminate
            downloader = VideoDownloader()
            x = Process(target=downloader.download, args=(url, para,))
            x.start()


    def get_background_items(self, window, file):
        url_prompt = self.get_widget("", window)

        submenu = Nautilus.Menu()
        
        video_mp4 = Nautilus.MenuItem(name='YTDLPExtension::video_mp4', 
                                         label='Download video (MP4)')
        video_mp4.connect('activate', self.create_prompt, file, "video", "mp4")
        submenu.append_item(video_mp4)

        audio_mp3 = Nautilus.MenuItem(name='YTDLPExtension::audio_mp3', 
                                         label='Download audio (MP3)')
        audio_mp3.connect('activate', self.create_prompt, file, "audio", "mp3")
        submenu.append_item(audio_mp3)

        audio_wav = Nautilus.MenuItem(name='YTDLPExtension::audio_wav', 
                                         label='Download audio (WAV)')
        audio_wav.connect('activate', self.create_prompt, file, "audio", "wav")
        submenu.append_item(audio_wav)

        menuitem = Nautilus.MenuItem(name='YTDLPExtension::Top', 
                                         label='YouTube downloader')
        menuitem.set_submenu(submenu)

        return menuitem,

