from gi.repository import Nautilus, GObject
import subprocess

class YTDLPExtension(GObject.GObject, Nautilus.MenuProvider):
    """A context menu for ytdlp"""

    def __init__(self):
        GObject.Object.__init__(self)

    def menu_activate_cb(self, menu, file):
        # Remove "file://" from uri
        path = str(file.get_uri())
        path = path.split("file://")[1]

        # run main program
        args = ['nautilus-ytdlp', path] 
        subprocess.Popen(args)


    def get_background_items(self, window, file):
        submenu = Nautilus.Menu()
        
        item = Nautilus.MenuItem(name='YTDLPExtension::download', 
                                         label='Download video/audio')
        item.connect('activate', self.menu_activate_cb, file)
        submenu.append_item(item)

        return item,