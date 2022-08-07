import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(400, 250)
        self.set_title("Video Downloader")

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.url_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        

        # configure url_box
        self.url_box.set_spacing(10)
        self.url_box.set_margin_top(10)
        self.url_box.set_margin_bottom(10)
        self.url_box.set_margin_start(10)
        self.url_box.set_margin_end(10)
        

        #  initialize url entry
        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("Enter video url")
        self.url_entry.set_hexpand(True)
        self.url_entry.set_halign(Gtk.Align.FILL)

        # initialize download button
        self.download_button = Gtk.Button()
        self.download_button.set_icon_name("folder-download-symbolic")
        self.download_button.connect('clicked', self.on_download_pressed)
        self.download_button.set_halign(Gtk.Align.END)


        self.set_child(self.main_box)
        self.main_box.append(self.url_box) 


        self.url_box.append(self.url_entry)
        self.url_box.append(self.download_button)
        


    def on_download_pressed(self, button):
        pass


#   def on_download_pressed(self, button, para):
#         # get entered video url from entry
#         video_urls = self.entry.get_buffer().get_text()

#         # make url list
#         video_urls = video_urls.split()

#         # download every video in a seperate thread
#         # downloaders = [(VideoDownloader(), url) for url in video_urls]
#         # pool = [Process(target=downloader.download, args=(url, para)) for (downloader, url) in downloaders]
#         # for p in pool:
#         #     p.start() 

#         # connection.wait(p.sentinel for p in pool)

class NautilusYTDLPDialog(Adw.Application):
    """Class for the url prompt entry"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        
    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

