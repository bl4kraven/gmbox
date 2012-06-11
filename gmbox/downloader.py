#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading
import urllib
import traceback
from config import CONFIG

class Downloader(threading.Thread):

    def __init__(self, song, callback):
        threading.Thread.__init__(self)
        self.song = song
        self.callback = callback

    def run(self):
        self.song.remove_lock = True
        if CONFIG["download_cover"]:
            self.download_cover()
        if CONFIG["download_lyric"]:
            self.download_lyric()
        self.download_mp3()
        self.song.remove_lock = False
        self.callback()

    def get_safe_path(self, url):
        not_safe_chars = '''\/:*?<>|'"'''
        if len(url) > 243:
            url = url[:238]
        for char in not_safe_chars:
            url = url.replace(char, "")
        return url

    def get_filepath(self):
        download_folder = CONFIG["download_folder"]
        if download_folder.endswith("/"):
            download_folder = download_folder[:-1]
        filename = CONFIG["filename_template"].replace("${ALBUM}", self.song.album)
        filename = filename.replace("${ARTIST}", self.song.artist)
        filename = filename.replace("${TITLE}", self.get_safe_path(self.song.name))
        if "${TRACK}" in filename:
            # need to load stearm info
            self.song.load_streaming()
            filename = filename.replace("${TRACK}", self.song.providerId[-2:])
        filepath = "%s/%s.mp3" % (download_folder, filename)
        return filepath

    def download_cover(self):
        self.song.down_status = "正在获取封面地址"
        self.song.load_streaming()
        if self.song.albumThumbnailLink == "":
            self.song.albumThumbnailLink = "获取封面地址失败"
            return

        filepath = "%s/cover.jpg" % os.path.dirname(self.get_filepath())

        if os.path.exists(filepath):
            self.song.down_status = "封面已存在"
            return

        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

        try:
            self.song.down_status = "下载封面中"
            urllib.urlretrieve(self.song.albumThumbnailLink, filepath)
            self.song.down_status = "下载封面完成"
        except:
            traceback.print_exc()

    def download_lyric(self):
        self.song.down_status = "正在获取歌词地址"
        self.song.load_streaming()
        if self.song.lyricsUrl == "":
            self.song.down_status = "获取歌词地址失败"
            return

        # remove ".mp3" extension
        filepath = "%s.lrc" % self.get_filepath()[:-4]

        if os.path.exists(filepath):
            self.song.down_status = "歌词文件已存在"
            return

        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

        try:
            self.song.down_status = "下载歌词中"
            urllib.urlretrieve(self.song.lyricsUrl, filepath)
            self.song.down_status = "下载歌词完成"
        except:
            traceback.print_exc()

    def download_mp3(self):
        self.song.down_status = "正在获取地址"
        self.song.load_download()
        if self.song.downloadUrl == "":
            self.song.down_status = "获取地址失败"
            return

        filepath = self.get_filepath()

        if os.path.exists(filepath):
            self.song.down_status = "文件已存在"
            self.song.down_process = "100%"
            return

        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

        print "Downloading %s" % self.song.name
        print self.song.downloadUrl
        print filepath
        try:
            self.song.down_status = "下载中"
            urllib.urlretrieve(self.song.downloadUrl, filepath, self.process)
            self.song.down_status = "下载完成"
        except:
            traceback.print_exc()

    def process(self, block, block_size, total_size):
        downloaded_size = block * block_size
        percent = float(downloaded_size) / total_size
        if percent >= 1:
            process = "100%"
        elif percent <= 0:
            process = "0%"
        elif percent < 0.1:
            process = str(percent)[3:4] + "%"
        else:
            process = str(percent)[2:4] + "%"
        self.song.down_process = process
