from easygui import *
import os
import sys
from threading import Thread

from nautilus_ytdlp.VideoDownloader import VideoDownloader
from nautilus_ytdlp.helpers import VideoParams

class NautilusYTDLPDialog():

    def __init__(_, path):
        Notify.init("Video Downloader")
        formats = ["mp4", "mp3", "wav"]
        format = choicebox("Please select download format", choices=formats)
        if format:
            while 1:
                # make parameters 
                format = "" 
                type = ""
                if format == "mp3":
                    format = "mp3"
                    type = "audio"
                elif format == "wav":
                    format = "wav"
                    type = "audio"
                else:
                    format = "mp4"
                    type = "video"
                para = VideoParams(type, format, path)     

                urls = enterbox("Please input your URLs. You can download multiple videos by passing multiple URLs separated by whitespaces. The video will be downloaded to " + para.path)
                if urls:
                    # make url list
                    video_urls = urls.split()
                    print(video_urls)
                    print(path)

                    # download every video in a seperate thread
                    downloaders = [VideoDownloader(url, para) for url in video_urls]
                    pool = [Thread(target=downloader.download, args=()) for downloader in downloaders]
                    for p in pool:
                        p.start() 

                    for p in pool:
                        p.join() 
                else: 
                    sys.exit(0)
        else:
            sys.exit(0)
