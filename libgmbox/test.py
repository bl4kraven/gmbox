#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = '''测试和示例文件

这个文件帮助你了解gmbox核心库的使用方法
'''

from utility import print_song, print_songlist, print_directory
from core import Song
from core import Album, Search, Chartlisting, Topiclisting, ArtistSong, Tag, Screener, Similar, Starrecc
from core import DirSearch, DirChartlisting, DirTopiclistingdir, DirArtist, DirArtistAlbum, DirTag, DirStarrecc

import urllib
from xml.dom import minidom

if __name__ == '__main__':

    #print "%s\n" % Song.musicdownload("S5c956b9af4dc56ba")
    #print_song(Song("Sb1ee641ab6133e1a"))

    #print_songlist(Album("B5f03f5ad567ecbec"))
    #print_songlist(Search("beyond"))
    #print_songlist(Chartlisting("chinese_new_songs_cn"))
    #print_songlist(Topiclisting("top100_autumn_day"))
    #print_songlist(ArtistSong("A887b2d5bdd631594"))
    #print_songlist(Tag("%E6%82%A0%E6%89%AC"))
    #print_songlist(Screener())
    #print_songlist(Similar("Sb1ee641ab6133e1a"))
    #print_songlist(Starrecc("top100_star_chenyixun"))

    #print_directory(DirSearch("海阔天空"))
    #print_directory(DirChartlisting("chinese_new-release_albums_cn"))
    #print_directory(DirTopiclistingdir())
    #print_directory(DirArtist("beyond"))
    #print_directory(DirArtistAlbum("A887b2d5bdd631594"))
    #print_directory(DirTag("%E6%82%A0%E6%89%AC"))
    #print_directory(DirStarrecc())

    #album_url_xml = "http://www.google.cn/music/album?id=B8e369684abdc57c3&output=xml"
    #urlopen = urllib.urlopen(album_url_xml)
    #xml = urlopen.read()

    #dom = minidom.parse("test.xml")
    #node = dom.getElementsByTagName("info")[0]
    #for sub_node in node.childNodes:
    #    print sub_node.nodeName, sub_node.childNodes[0].data

    #node = dom.getElementsByTagName("songList")[0]
    #for song_node in node.childNodes:
    #    for value_node in song_node.childNodes:
    #        print value_node.nodeName, value_node.childNodes[0].data
    #    print

    search = Search()
    search.id = "the end of world"
    search.load_songs(0, 1)

    for song in search.songs:
        for key, value in song.gmattrs.iteritems():
            print key,  value
        print

        similar = Similar(song.id)
        print similar.songs

