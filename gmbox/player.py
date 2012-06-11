#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import thread
import subprocess
import time

class Player(threading.Thread):

    def __init__(self, song, running, callback):
        threading.Thread.__init__(self)
        self.song = song
        self.running = running
        self.callback = callback

    def run(self):
        cmd = "mpg123 -R dummy --skip-printing-frames=32".split()
        self.popen = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.open()
        self.play_end = False
        thread.start_new_thread(self.mpg123_response, ())
        self.play_loop()
        self.quit()
        self.popen.terminate()

        if self.play_end:
            self.callback(self.song)

    def play_loop(self):
        while self.running.isSet():
            if not self.play_end:
                time.sleep(1)
            else:
                break

    def open(self):
        self.mpg123_request("LOAD %s" % self.song.songUrl)

    def play(self):
        self.mpg123_request("PAUSE")

    def pause(self):
        self.mpg123_request("PAUSE")

    def stop(self):
        self.mpg123_request("STOP")

    def quit(self):
        self.mpg123_request("QUIT")

    def seek(self):
        pass

    def mpg123_request(self, text):
        self.popen.stdin.write(text)

    def mpg123_response(self):
        while self.running.isSet():
            line = self.popen.stdout.readline()
            if line.startswith("@F"):
                # @F 417 -417 10.89 0.00
                values = line.split()
                prefix = values[0]
                current_frame = values[1]
                frames_remaining = values[2]
                current_time = values[3]
                time_remaining = values[4]
                self.song.play_process = float(current_time) / float(self.song.duration) * 100
                # mpg123 does not auto stop
                if self.song.play_process > 100:
                    self.play_end = True
                    break

