from gi.repository import Nautilus, GObject, Gtk, GLib


class EntryWindow(Gtk.Window):
    """Class for the url prompt entry"""

    def __init__(self):
        super().__init__(title="Video downloader")
        self.set_size_request(200, 100)

        self.timeout_id = None

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter video url")
        vbox.pack_start(self.entry, True, True, 0)

        hbox = Gtk.Box(spacing=6)
        vbox.pack_start(hbox, True, True, 0)

        self.entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "system-search-symbolic")
        

        

class YTDLPExtension(GObject.GObject, Nautilus.MenuProvider, Nautilus.LocationWidgetProvider):
    """A context menu for ytdlp"""

    def __init__(self):
        GObject.Object.__init__(self)
        
        self.video_url = ""
        

    def show_url_prompt(self, menu, url_prompt):
        url_prompt = EntryWindow()
        url_prompt.connect("destroy", Gtk.main_quit)
        url_prompt.show_all()
        

    def get_background_items(self, window, file):
        url_prompt = self.get_widget("", window)

        submenu = Nautilus.Menu()
        
        video_h264 = Nautilus.MenuItem(name='YTDLPExtension::video_h264', 
                                         label='Download video (H.264)')
        video_h264.connect('activate', self.show_url_prompt, url_prompt)
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
