import shutil
import youtube_dl
import pafy
import asyncio
import sys


class Song:
    def __init__(self, author, channel, song):
        self.requester = author
        self.channel = channel
        self.song = song

class MusicPlayer:
    def __init__(self):
        self.songFileUrls = []

    def addSongs(self, url, name):
        self.get_song_file_urls(url)

    def get_song_file_urls(self, url):
        ydl_opts = {
            'formats': 'mp3',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            for f in info["formats"]:
                if f["format_id"] == "http_mp3_128_url - audio only" or f["format_id"] == "http_mp3_128_url":
                    self.songFileUrls.append(f["url"])
                    break
                # else: print(f["format_id"]) <-- useful to see if a track has no mp3 formats