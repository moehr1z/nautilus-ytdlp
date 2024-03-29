import dbus
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib, Gdk
import os

from threading import Thread


import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

from nautilus_ytdlp.VideoDownloader import VideoDownloader
from nautilus_ytdlp.helpers import VideoParams


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, path,  *args, **kwargs):
        # path where videos will get downloaded to
        self.path = path 
        self.para = VideoParams("video", "mp4", self.path)


        super().__init__(*args, **kwargs)
        GLib.set_application_name("Video Downloader")
        self.set_default_size(400, 110)
        self.set_title("Video Downloader")
        self.set_resizable(False)

        Notify.init("Video Downloader")

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
        
        # initialize spinner widget
        self.spinner = Gtk.Spinner()      # we don't use a progress bar as this would be more complicated with mulitple download threads

        self.set_child(self.main_box)
        self.main_box.append(self.url_box) 


        self.url_box.append(self.url_entry)
        self.url_box.append(self.spinner)
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
        self.builder.add_from_file(os.getenv("NAUTILUS_YTDLP_PATH") + "/nautilus_ytdlp/popover.ui")
        self.popover.set_menu_model(self.builder.get_object('options-menu'))

        # action for "show about" dialog
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.show_about)
        self.add_action(action)

        # action for radio buttons
        para = Gio.SimpleAction.new_stateful("radiogroup", \
                           GLib.VariantType.new("s"), \
                           GLib.Variant("s", "radio-mp4"))
        para.connect("activate", self.radio_action)
        self.add_action(para)

    def radio_action(self, act_obj, act_lbl, *args):
        act_obj.set_state(act_lbl)
        act_lbl = act_lbl.get_string()

        # make parameters from selected radio button
        format = "" 
        type = ""
        if act_lbl == "radio-mp3":
            format = "mp3"
            type = "audio"
        elif act_lbl == "radio-wav":
            format = "wav"
            type = "audio"
        else:
            format = "mp4"
            type = "video"
        
        self.para = VideoParams(type, format, self.path)     

        
    def show_about(self, action, param):
        self.about = Gtk.AboutDialog()
        self.about.set_transient_for(self)  # Makes the dialog always appear in from of the parent window
        self.about.set_modal(self)  # Makes the parent window unresponsive while dialog is showing

        self.about.set_authors(["moehr1z"])
        self.about.set_copyright("Copyright 2022 moehr1z")
        self.about.set_license_type(Gtk.License.MIT_X11)
        self.about.set_website("https://github.com/moehr1z/nautilus-ytdlp")
        self.about.set_website_label("Project Github")
        self.about.set_version("1.0")

        self.about.show()

    def on_download_pressed_action(self, button): 
        # get entered video url from entry
        video_urls = self.url_entry.get_buffer().get_text()

        # make url list
        video_urls = video_urls.split()
        

        # download every video in a seperate thread
        downloaders = [VideoDownloader(url, self.para) for url in video_urls]
        pool = [Thread(target=downloader.download, args=()) for downloader in downloaders]
        for p in pool:
            p.start() 
        self.spinner.start()

        for p in pool:
            p.join() 
        self.spinner.stop()
        

    def on_download_pressed(self, button):
        Thread(target=self.on_download_pressed_action, args=(button)).start()


class NautilusYTDLPDialog(Adw.Application):
    """Class for the url prompt entry"""

    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path
        self.connect('activate', self.on_activate)
        
    def on_activate(self, app):
        self.win = MainWindow(self.path, application=app)
        self.win.present()

