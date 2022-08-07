import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
from multiprocessing import Process

from nautilus_ytdlp.VideoDownloader import VideoDownloader
from nautilus_ytdlp.helpers import VideoParams

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, path,  *args, **kwargs):
        # path where videos will get downloaded to
        self.path = path 

        super().__init__(*args, **kwargs)
        GLib.set_application_name("Youtube Downloader")
        self.set_default_size(400, 110)
        self.set_title("Video Downloader")
        self.set_resizable(False)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.url_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        

        # configure url_box
        self.url_box.set_spacing(10)
        self.url_box.set_margin_top(15)
        self.url_box.set_margin_bottom(10)
        self.url_box.set_margin_start(10)
        self.url_box.set_margin_end(10)
        
        # initialize download button
        self.download_button = Gtk.Button()
        self.download_button.set_icon_name("folder-download-symbolic")
        self.download_button.connect('clicked', self.on_download_pressed)
        self.download_button.set_halign(Gtk.Align.END)
        self.set_default_widget(self.download_button)

        #  initialize url entry
        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("Enter video url")
        self.url_entry.set_hexpand(True)
        self.url_entry.set_halign(Gtk.Align.FILL)
        self.url_entry.set_activates_default(True)

        self.set_child(self.main_box)
        self.main_box.append(self.url_box) 


        self.url_box.append(self.url_entry)
        self.url_box.append(self.download_button)
        
        self.populate_header()
        

    def populate_header(self):
        """ creates header bar buttons """

        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)
        
        # create popover
        self.popover = Gtk.PopoverMenu()  # Create a new popover menu

        # create menu button
        self.hamburger = Gtk.MenuButton()
        self.hamburger.set_popover(self.popover)
        self.hamburger.set_icon_name("open-menu-symbolic")  
        
        # Add menu button to the header bar
        self.header.pack_start(self.hamburger)
        
        # create menu from xml
        self.builder = Gtk.Builder() 
        self.builder.add_from_file("/home/moritz/nautilus-ytdlp/nautilus_ytdlp/popover.ui")
        self.popover.set_menu_model(self.builder.get_object('options-menu'))

        # action for "show about" dialog
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.show_about)
        self.add_action(action)

        # action for radio buttons
        para = Gio.SimpleAction.new_stateful("radiogroup", \
                           GLib.VariantType.new("s"), \
                           GLib.Variant("s", "radio-mp4"))
        para.connect("activate", self.radio_response)
        self.add_action(para)

    def radio_response(self, act_obj, act_lbl):
        act_obj.set_state(act_lbl)
        print(act_lbl)
        
    def show_about(self, action, param):
        self.about = Gtk.AboutDialog()
        self.about.set_transient_for(self)  # Makes the dialog always appear in from of the parent window
        self.about.set_modal(self)  # Makes the parent window unresponsive while dialog is showing

        self.about.set_authors(["Your Name"])
        self.about.set_copyright("Copyright 2022 Your Full Name")
        self.about.set_license_type(Gtk.License.GPL_3_0)
        self.about.set_website("http://example.com")
        self.about.set_website_label("My Website")
        self.about.set_version("1.0")
        self.about.set_logo_icon_name("org.example.example")  # The icon will need to be added to appropriate location
                                                 # E.g. /usr/share/icons/hicolor/scalable/apps/org.example.example.svg

        self.about.show()

    def on_download_pressed(self, button):
        # get entered video url from entry
        video_urls = self.url_entry.get_buffer().get_text()

        # make url list
        video_urls = video_urls.split()
        
        # Video download parameters
        para = VideoParams("video", "mp4", self.path)


        # download every video in a seperate thread
        downloaders = [(VideoDownloader(), url) for url in video_urls]
        pool = [Process(target=downloader.download, args=(url, para)) for (downloader, url) in downloaders]
        for p in pool:
            p.start() 


class NautilusYTDLPDialog(Adw.Application):
    """Class for the url prompt entry"""

    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path
        self.connect('activate', self.on_activate)
        
    def on_activate(self, app):
        self.win = MainWindow(self.path, application=app)
        self.win.present()

