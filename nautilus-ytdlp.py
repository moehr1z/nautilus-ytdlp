from gi.repository import Nautilus, GObject

class YTDLPExtension(GObject.GObject, Nautilus.MenuProvider):
    """A context menu for ytdlp"""

    def __init__(self):
        pass
        

    def get_background_items(self, window, file):

        submenu = Nautilus.Menu()
        submenu.append_item(Nautilus.MenuItem(name='YTDLPExtension::video_h264', 
                                         label='Download video (H.264)'))

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


