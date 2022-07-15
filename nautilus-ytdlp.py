from gi.repository import Nautilus, GObject, Gtk, GLib, Notify
import subprocess 
import threading
import urllib.request
import json
import urllib
import pprint


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

        

        
    def download_video(url, para): 
        # assemble yt-dlp call string 
        format_str = ""
        if para.type == "audio":
            format_str = "--extract-audio --audio-format " + para.format
        else:
            format_str = "--format " + para.format

        cmd = "yt-dlp " + "--paths " + para.path + " " + format_str + " " + url
                 

        # call yt-dlp with specified args
        subprocess.run(cmd.split())
        
    def get_video_title(self, url):
        """returns the name of the video corresponding the url"""
        params = {"format": "json", "url": url}
        url = "https://www.youtube.com/oembed"
        query_string = urllib.parse.urlencode(params)
        url = url + "?" + query_string

        with urllib.request.urlopen(url) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            return data['title']

    def cancel_download(self, thread):
        return 0

    def on_download_pressed(self, button, prompt, para):
        # get entered video url from entry
        video_url = prompt.entry.get_buffer().get_text()
        
        # make url list
        video_url = video_url.split()

        # download every video in a seperate thread
        for url in video_url:
            x = threading.Thread(target=YTDLPExtension.download_video, args=(url, para,))
            x.start()
            
            # notify user about started download
            Notify.init("YouTube Downloader")
            video_title = self.get_video_title(url)
            notification = Notify.Notification.new(
                "Downloading video",
                video_title,
                "emblem-downloads", #TODO replace with proper download icon
            )
            notification.add_action(
                "action_click",
                "Cancel",
                self.cancel_download,
                x 
            ) 
            
            notification.show()
            


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
