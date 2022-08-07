from gi.repository import Gtk


class NautilusYTDLPDialog(Gtk.Window):
    """Class for the url prompt entry"""

    def __init__(self):
        super().__init__(title="Hello World")
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


    def on_download_pressed(self, button, para):
        # get entered video url from entry
        video_urls = self.entry.get_buffer().get_text()
        
        # make url list
        video_urls = video_urls.split()

        # download every video in a seperate thread
        # downloaders = [(VideoDownloader(), url) for url in video_urls]
        # pool = [Process(target=downloader.download, args=(url, para)) for (downloader, url) in downloaders]
        # for p in pool:
        #     p.start() 

        # connection.wait(p.sentinel for p in pool)