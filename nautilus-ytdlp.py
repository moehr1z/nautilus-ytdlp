from gi.repository import Nautilus, GObject, Gtk, GLib
import subprocess, threading


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
        

    def create_prompt(self, para):
        url_prompt = EntryWindow()
        url_prompt.connect("destroy", Gtk.main_quit)
        url_prompt.show_all()
        url_prompt.button_download.connect("pressed", self.on_download_pressed, url_prompt, para)

    def on_video_pressed(self, menu, file):
        # initialize video params
        path = str(file.get_uri())
        path = path.split("file://")[1]
        para = VideoParams("video", "h264", path)        
        
        self.create_prompt(para)

        
    def download_video(url, para): 
        # assemble yt-dlp call string 
        format_str = ""
        if para.type == "audio":
            format_str = "--extract-audio --audio-format " + para.format
        else:
            format_str = "--format mp4"

        cmd = "yt-dlp " + "--paths " + para.path + " " + format_str + " " + url
                 
        # call yt-dlp with specified args
        subprocess.run(cmd.split())


    def on_download_pressed(self, button, prompt, para):
        # get entered video url from entry
        video_url = prompt.entry.get_buffer().get_text()
        
        # make url list
        video_url = video_url.split()

        # download every video in a seperate thread
        for url in video_url:
            x = threading.Thread(target=YTDLPExtension.download_video, args=(url, para,))
            x.start()


    def get_background_items(self, window, file):
        url_prompt = self.get_widget("", window)

        submenu = Nautilus.Menu()
        
        video_h264 = Nautilus.MenuItem(name='YTDLPExtension::video_h264', 
                                         label='Download video')
        video_h264.connect('activate', self.on_video_pressed, file)
        submenu.append_item(video_h264)

        submenu.append_item(Nautilus.MenuItem(name='YTDLPExtension::audio_mp3', 
                                         label='Download audio (MP3)'))

        submenu.append_item(Nautilus.MenuItem(name='YTDLPExtension::audio_wav', 
                                         label='Download audio (WAV)'))

        submenu.append_item(Nautilus.MenuItem(name='YTDLPExtension::playlist_h264', 
                                         label='Download video playlist (H.264)'))

        submenu.append_item(Nautilus.MenuItem(name='YTDLPExtension::playlist_mp3', 
                                         label='Download audio playlist (MP3)'))

        menuitem = Nautilus.MenuItem(name='YTDLPExtension::Top', 
                                         label='YouTube downloader')
        menuitem.set_submenu(submenu)

        return menuitem,
