#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = '''打印调试函数'''

def print_song(song):
    '''打印Song类实例信息

    注意：
    在测试Songlist或者Directory类时，
    你可以注释：
    song.load_detail()
    song.load_streaming()
    以免发出过多的http请求。
    '''

    song.load_detail()
    song.load_streaming()

    for key, value in song.gmattrs.iteritems():
        print "%s: %s" % (key , value)
    print

def print_songlist(songlist):
    '''打印Songlist类实例信息

    注意：
    在测试Songlist或者Directory类时，
    你可以注释：
    print_song(song)
    以免发出过多的http请求。
    '''

    for key, value in songlist.gmattrs.iteritems():
        print "%s: %s" % (key , value)

    for song in songlist.songs:
        print_song(song)
    print

def print_directory(directory):
    '''打印Directory类实例信息

    注意：
    在测试Songlist或者Directory类时，
    你可以注释
    songlist.load_songs()
    以免发出过多的http请求。
    '''

    for songlist in directory.songlists:
        songlist.load_songs()
        print_songlist(songlist)
