#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = '''gmbox核心库

这个库复制解析请求结果，并把结果转换为python对象。

基本对象：
Song: 歌曲
Songlist: 包含Song类的列表，子类是专辑、歌曲排行榜等。
Directory: 包含Songlist类（或子类）的列表，子类是搜索专辑，专辑排行榜等。

解析结果：
谷歌音乐的某些结果提供xml，通过它的flash播放器抓包分析所得。
某些功能没有xml，只好解析html，理论上解析速度会比xml慢。
'''

import xml.dom.minidom as minidom
import logging
import hashlib
import urllib
import re

def get_logger(logger_name):
    ''' 获得一个logger '''
    format = '%(asctime)s %(levelname)s %(message)s'
    #level = logging.DEBUG
    level = logging.WARNING
    logging.basicConfig(format=format, level=level)
    logger = logging.getLogger(logger_name)
    return logger

logger = get_logger('googlemusic')

class GmObject():
    '''gmbox基本类

    定义共享工具类型的方法，子类实现具体方法。
    '''

    def __init__(self):
        self.gmattrs = {}

    def parse_node(self, node):
        '''解析xml节点添加实例属性'''

        for childNode in node.childNodes:
            name = childNode.tagName
            if childNode.hasChildNodes():
                value = childNode.childNodes[0].data
            else:
                value = ""
            self.gmattrs[name] = value
            setattr(self, name, value)

    def parse_dict(self, dict):
        '''解析dict键值添加实例属性'''

        for key, value in dict.iteritems():
            self.gmattrs[key] = value
            setattr(self, key, value)

    @staticmethod
    def decode_html_text(text):
        '''转义html特殊符号'''

        html_escape_table = {
            "&nbsp;" : " ",
            "&quot;" : '"',
            "&ldquo;" : "“",
            "&rdquo;" : "”",
            "&mdash;" : "—",
            "&amp;" : "&",
            "&middot;" : "·"
        }
        for key, value in html_escape_table.iteritems():
            text = text.replace(key, value)
        numbers = re.findall('&#([^;]+);', text)
        for number in numbers:
            text = text.replace("&#%s;" % number, unichr(int(number)))
        return text

class Song(GmObject):
    '''歌曲类'''

    def __init__(self, id=None):
        GmObject.__init__(self)
        if id is not None:
            self.id = id
            self.load_detail()

    def load_streaming(self):
        '''读取stream数据

        stream数据是包含歌词地址，在线播放地址的数据。
        调用这个函数会发出一个http请求，但只会发出一次，
        亦即数据已经读取了就不再发出http请求了。
        '''

        if not hasattr(self, "songUrl"):
            template = "http://www.google.cn/music/songstreaming?id=%s&cd&sig=%s&output=xml"
            flashplayer_key = "343aef99312bc33a887761529031cbad"
            sig = hashlib.md5(flashplayer_key + self.id).hexdigest()
            url = template % (self.id, sig)

            logger.info('读取stream数据地址：%s', url)
            urlopener = urllib.urlopen(url)
            xml = urlopener.read()
            dom = minidom.parseString(xml)
            self.parse_node(dom.getElementsByTagName("songStreaming")[0])

    def load_detail(self):
        '''读取详情数据

        详情数据是包含艺术家编号，封面地址等数据。
        调用这个函数会发出一个http请求，但只会发出一次，
        亦即数据已经读取了就不再发出http请求了。
        '''

        if not hasattr(self, "albumId"):
            template = "http://www.google.cn/music/song?id=%s&output=xml"
            url = template % self.id

            logger.info('读取详情数据地址：%s', url)
            urlopener = urllib.urlopen(url)
            xml = urlopener.read()
            dom = minidom.parseString(xml)
            self.parse_node(dom.getElementsByTagName("song")[0])

    def load_download(self):
        '''读取下载地址数据'''

        if not hasattr(self, "downloadUrl") or self.downloadUrl == "":
            self.downloadUrl = Song.musicdownload(self.id)

    @staticmethod
    def musicdownload(id):
        '''获取下载地址'''

        template = "http://www.google.cn/music/top100/musicdownload?id=%s"
        url = template % id

        logger.info('请求下载信息页地址：%s', url)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        matches = re.search('<a href="/(music/top100/url[^"]+)">', html)
        if matches is not None:
            downloadUrl = "http://www.google.cn/%s" % matches.group(1).replace("&amp;", "&")
            logger.info('歌曲 %s，下载地址：%s', id, downloadUrl)
            return downloadUrl
        else:
            logger.warring('短时间内请求次数太多了，可能出现验证码。')
            return ""

class Songlist(GmObject):
    '''歌曲列表基本类，是歌曲(Song类）的集合

    定义共享解析的方法，分别是xml和html，部分内容可能没有xml提供。
    对于特别的情况，由子类覆盖方法实现。

    '''

    def __init__(self):
        GmObject.__init__(self)
        self.songs = []
        self.has_more = False

    def load_songs(self):
        '''读取歌曲列表里的歌曲，子类应覆盖这个方法

        调用self.load_songs后，self.songs会保存了本次请求的Song类的实例，
        例如：
        第一次调用self.load_songs后，self.songs只包含第一页的20首歌曲
        第二次调用self.load_songs后，self.songs只包含第二页的20首歌曲
        余下同理。

        所以请先从self.songs复制出Song实例后再调用self.load_songs，以免
        前面的结果被覆盖。
        可以检查self.has_more是否还有更多，亦即是否存在下一页。
        '''

        pass

    def parse_xml(self, xml, song_tag="songList"):
        '''解析xml'''

        songs = []
        dom = minidom.parseString(xml)
        info_node = dom.getElementsByTagName("info")
        if len(info_node) > 0:
            self.parse_node(info_node[0])
        for childNode in dom.getElementsByTagName(song_tag)[0].childNodes:
            if (childNode.nodeType == childNode.ELEMENT_NODE):
                song = Song()
                song.parse_node(childNode)
                songs.append(song)
        return songs

    def parse_html(self, html):
        '''解析html'''

        ids = []
        matches = re.findall('<!--freemusic/song/result/([^-]+)-->', html)
        for match in matches:
            ids.append(match)

        names = []
        matches = re.findall('<td class="Title BottomBorder">.+?>(.+?)</.+?></td>', html, re.DOTALL)
        for match in matches:
            match = GmObject.decode_html_text(match)
            names.append(match)

        artists = []
        matches = re.findall('<td class="Artist BottomBorder">(.+?)</td>', html, re.DOTALL)
        for match in matches:
            # TODO 某些歌曲有一个以上的歌手
            match = re.findall('<.+?>(.+?)</.*>', match)
            match = " ".join(match)
            match = GmObject.decode_html_text(match)
            artists.append(match)

        albums = []
        matches = re.findall('<td class="Album BottomBorder"><a .+?>《(.+?)》</a></td>', html, re.DOTALL)
        for match in matches:
            match = GmObject.decode_html_text(match)
            albums.append(match)

        if len(albums) == 0:
            for i in range(len(ids)):
                albums.append("")

        songs = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "artist":artists[i], "album":albums[i]}
            song = Song()
            song.parse_dict(dict)
            songs.append(song)
        return songs

class Album(Songlist):
    '''专辑'''

    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()

    def load_songs(self):
        template = "http://www.google.cn/music/album?id=%s&output=xml"
        url = template % self.id

        logger.info('读取专辑地址：%s', url)
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songs = self.parse_xml(xml)
        self.songs.extend(songs)
        return songs

class Search(Songlist):
    '''搜索'''

    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()

    def load_songs(self, start=0, number=20):
        template = "http://www.google.cn/music/search?cat=song&q=%s&start=%d&num=%d&output=xml"
        url = template % (self.id, start, number + 1)

        logger.info('读取搜索地址：%s', url)
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songs = self.parse_xml(xml)
        if len(songs) == number + 1:
            self.has_more = True
            songs.pop()
        else:
            self.has_more = False
        self.songs.extend(songs)
        return songs

class Chartlisting(Songlist):
    '''排行榜'''

    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()

    def load_songs(self, start=0, number=20):
        template = "http://www.google.cn/music/chartlisting?q=%s&cat=song&start=%d&num=%d&output=xml"
        url = template % (self.id, start, number + 1)

        logger.info('读取排行榜地址：%s', url)
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songs = self.parse_xml(xml)
        if len(songs) == number + 1:
            self.has_more = True
            songs.pop()
        else:
            self.has_more = False
        self.songs.extend(songs)
        return songs

class Topiclisting(Songlist):
    '''专题'''

    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()

    def load_songs(self):
        template = "http://www.google.cn/music/topiclisting?q=%s&cat=song&output=xml"
        url = template % self.id

        logger.info('读取专题地址：%s', url)
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songs = self.parse_xml(xml)
        self.songs.extend(songs)
        return songs

class ArtistSong(Songlist):
    '''艺术家'''

    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()

    def load_songs(self):
        template = "http://www.google.cn/music/artist?id=%s&output=xml"
        url = template % self.id

        logger.info('读取艺术家地址：%s', url)
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songs = self.parse_xml(xml, "hotSongs")
        self.songs.extend(songs)
        return songs

class Tag(Songlist):
    '''标签'''

    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()

    def load_songs(self, start=0, number=20):
        template = "http://www.google.cn/music/tag?q=%s&cat=song&type=songs&start=%d&num=%d"
        url = template % (self.id, start, number + 1)

        logger.info('读取标签地址：%s', url)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songs = self.parse_html(html)
        if len(songs) == number + 1:
            self.has_more = True
            songs.pop()
        else:
            self.has_more = False
        self.songs.extend(songs)
        return songs

class Screener(Songlist):
    '''挑歌

    args_dict 参数示例，字典类型
    {
        'timbre': '0.5', 
        'date_l': '694195200000', 
        'tempo': '0.5', 
        'date_h': '788889600000', 
        'pitch': '0.5', 
        'artist_type': 'male'
    }
    '''

    def __init__(self, args_dict=None):
        Songlist.__init__(self)
        if args_dict is None:
            self.args_dict = {}
        else:
            self.args_dict = args_dict
        self.load_songs()

    def load_songs(self, start=0, number=20):
        template = "http://www.google.cn/music/songscreen?start=%d&num=%d&client=&output=xml"
        url = template % (start, number + 1)

        logger.info('读取挑歌地址：%s', url)
        request_args = []
        for key, value in self.args_dict.iteritems():
            text = "&%s=%s" % (key, value)
            request_args.append(text)
        url = url + "".join(request_args)
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songs = self.parse_xml(xml)
        if len(songs) == number + 1:
            self.has_more = True
            songs.pop()
        else:
            self.has_more = False
        self.songs.extend(songs)
        return songs

class Similar(Songlist):
    '''相似歌曲'''

    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()

    def load_songs(self):
        template = "http://www.google.cn/music/song?id=%s"
        url = template % self.id

        logger.info('读取相似地址：%s', url)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()

        # 去除“听过这首歌的人还听了”歌曲
        m = re.search(r'<table id="song_list".+?>(.+?)</table>', html, re.DOTALL)
        if m:
            songs = self.parse_html(m.group(1))
            self.songs.extend(songs)
            return songs

class Starrecc(Songlist):
    '''大牌私房歌'''

    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()

    def load_songs(self):
        template = "http://www.google.cn/music/playlist/playlist?id=sys:star_recc:%s&type=star_recommendation"
        url = template % self.id

        logger.info('读取大牌私房歌地址：%s', url)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songs = self.parse_html(html)
        self.songs.extend(songs)
        return songs

    def parse_html(self, html):
        ids = []
        matches = re.findall('onclick="window.open([^"]+)"', html)
        for match in matches:
            match = re.search('download.html\?id=([^\\\]+)', urllib.unquote(match)).group(1)
            ids.append(match)

        names = []
        artists = []
        matches = re.findall('<td class="Title"><a .+?>《(.+?)》\n&nbsp;(.+?)</a></td>', html, re.DOTALL)
        for match in matches:
            name = GmObject.decode_html_text(match[0])
            artist = GmObject.decode_html_text(match[1])
            names.append(name)
            artists.append(artist)

        songs = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "artist":artists[i]}
            song = Song()
            song.parse_dict(dict)
            songs.append(song)
        return songs

class Directory(GmObject):
    '''歌曲列表列表基本类，是歌曲列表(Songlist类）的集合，这里简称为“目录”

    类结构和Songlist相同，提供通用的解析方法，特殊情况由子类覆盖方法实现。
    '''

    def __init__(self):
        self.songlists = []
        self.has_more = False

    def load_songlists(self, start=0, number=20):
        '''读取目录里的歌曲列表，子类应覆盖这个方法

        原理类似Songlist类的load_songs方法，请参考该类注释，只不过Songlist类
        实用self.songs而这个类使用self.songlists。
        '''

        pass

class DirSearch(Directory):
    '''专辑搜索'''

    def __init__(self, id):
        Directory.__init__(self)
        self.id = id
        self.load_songlists()

    def load_songlists(self, start=0, number=20):
        template = "http://www.google.cn/music/search?q=%s&cat=album&start=%d&num=%d"
        url = template % (self.id, start, number + 1)

        logger.info('读取专辑搜索地址：%s', url)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songlists = self.parse_html(html)
        if len(songlists) == number + 1:
            self.has_more = True
            songlists.pop()
        else:
            self.has_more = False
        self.songlists.extend(songlists)
        return songlists

    def parse_html(self, html):
        ids = []
        matches = re.findall('<!--freemusic/album/result/([^-]+)-->', html)
        for match in matches:
            ids.append(match)

        names = []
        matches = re.findall('《(.+)》', html)
        for match in matches:
            match = match.replace("<b>", "")
            match = match.replace("</b>", "")
            match = GmObject.decode_html_text(match)
            names.append(match)

        artists = []
        matches = re.findall('<td class="Tracks" colspan="10" align="left">(.+?)</td>', html)
        for match in matches:
            match = match.replace("<b>", "")
            match = match.replace("</b>", "")
            match = match.split()[0]
            match = GmObject.decode_html_text(match)
            artists.append(match)

        thumbnails = []
        matches = re.findall('<img [^/]+ class="thumb-img" [^/]+ src="([^"]+)"', html)
        for match in matches:
            thumbnails.append(match)

        songlists = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "artist":artists[i], "thumbnailLink":thumbnails[i]}
            album = Album()
            album.parse_dict(dict)
            songlists.append(album)
        return songlists

class DirChartlisting(Directory):
    '''专辑排行榜'''

    def __init__(self, id):
        Directory.__init__(self)
        self.id = id
        self.load_songlists()

    def load_songlists(self, start=0, number=20):
        template = "http://www.google.cn/music/chartlisting?q=%s&cat=album&start=%d&num=%d&output=xml"
        url = template % (self.id, start, number + 1)

        logger.info('读取专辑排行榜地址：%s', url)
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songlists = self.parse_xml(xml)
        if len(songlists) == number + 1:
            self.has_more = True
            songlists.pop()
        else:
            self.has_more = False
        self.songlists.extend(songlists)
        return songlists

    def parse_xml(self, xml):
        songlists = []
        dom = minidom.parseString(xml)
        for node in dom.getElementsByTagName("node"):
            if (node.nodeType == node.ELEMENT_NODE):
                album = Album()
                album.parse_node(node)
                songlists.append(album)
        return songlists

class DirTopiclistingdir(Directory):
    '''专辑专题'''

    def __init__(self):
        Directory.__init__(self)
        self.load_songlists()

    def load_songlists(self, start=0, number=20):
        template = "http://www.google.cn/music/topiclistingdir?cat=song&start=%d&num=%d"
        url = template % (start, number + 1)

        logger.info('读取专辑专题地址：%s', url)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songlists = self.parse_html(html)
        if len(songlists) == number + 1:
            self.has_more = True
            songlists.pop()
        else:
            self.has_more = False
        self.songlists.extend(songlists)
        return songlists

    def parse_html(self, html):
        html = urllib.unquote(html)

        ids = []
        matches = re.findall('<a class="topic_title" href="([^"]+)">', html)
        for match in matches:
            match = re.search('topiclisting\?q=([^&]+)&', urllib.unquote(match)).group(1)
            ids.append(match)

        names = []
        matches = re.findall('<a class="topic_title" [^>]+>([^<]+)</a>', html)
        for match in matches:
            match = GmObject.decode_html_text(match)
            names.append(match)

        descriptions = []
        matches = re.findall('<td class="topic_description"><div title="([^"]+)"', html)
        for match in matches:
            match = match.split()[0]
            match = GmObject.decode_html_text(match)
            descriptions.append(match)

        # WorkAround
        if len(matches) != len(ids):
            matches = re.findall('<td class="topic_description"><div([^<]+)<', html)
            for match in matches:
                match = match.split()[0]
                match = GmObject.decode_html_text(match)
                if match.startswith(' title="'):
                    match = match[len((' title="')):]
                elif match.startswith('<'):
                    match = match[2:]
                descriptions.append(match)

        thumbnails = []
        for i in range(len(ids)):
            thumbnails.append("http://www.google.cn/music/images/cd_cover_default_big.png")
        matches = re.findall('<td class="td-thumb-big">.+?topiclisting\?q=(.+?)&.+?src="(.+?)"', html, re.DOTALL)
        for match in matches:
            for i in range(len(ids)):
                if match[0] == ids[i]:
                    thumbnails[i] = match[1]

        songlists = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "descriptions":descriptions[i],
                    "thumbnailLink":thumbnails[i]}
            topiclisting = Topiclisting()
            topiclisting.parse_dict(dict)
            songlists.append(topiclisting)
        return songlists


class DirArtist(Directory):
    '''艺术家搜索'''

    def __init__(self, id):
        Directory.__init__(self)
        self.id = id
        self.load_songlists()

    def parse_html(self, html):
        html = urllib.unquote(html)

        ids = []
        matches = re.findall('<!--freemusic/artist/result/([^-]+)-->', html)
        for match in matches:
            ids.append(match)

        names = []
        matches = re.findall('<a href="/music/url\?q=/music/artist\?id.+?>(.+?)</a>', html)
        for match in matches:
            match = match.replace("<b>", "")
            match = match.replace("</b>", "")
            match = GmObject.decode_html_text(match)
            names.append(match)

        thumbnails = []

        # 某些专辑没有封面，则使用默认
        for i in range(len(ids)):
            thumbnails.append("http://www.google.cn/music/images/shadow_background.png")
        matches = re.findall('<div class="thumb">.+?artist\?id=(.+?)&.+?src="(.+?)"', html, re.DOTALL)
        for match in matches:
            for i in range(len(ids)):
                if match[0] == ids[i]:
                    thumbnails[i] = match[1]

        songlists = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "thumbnailLink":thumbnails[i]}
            artist_song = ArtistSong()
            artist_song.parse_dict(dict)
            songlists.append(artist_song)
        return songlists

    def load_songlists(self, start=0, number=20):
        template = "http://www.google.cn/music/search?q=%s&cat=artist&start=%d&num=%d"
        url = template % (self.id, start, number + 1)

        logger.info('读取艺术家搜索地址：%s', url)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songlists = self.parse_html(html)
        if len(songlists) == number + 1:
            self.has_more = True
            songlists.pop()
        else:
            self.has_more = False
        self.songlists.extend(songlists)
        return songlists

class DirArtistAlbum(Directory):
    ''' 艺术家专辑 '''

    def __init__(self, id):
        Directory.__init__(self)
        self.id = id
        self.load_songlists()

    def parse_html(self, html):

        ids = []
        matches = re.findall('<!--freemusic/album/result/([^-]+)-->', html)
        for match in matches:
            ids.append(match)

        names = []
        matches = re.findall('《(.+)》</a>&nbsp;-&nbsp;', html)
        for match in matches:
            match = match.replace("<b>", "")
            match = match.replace("</b>", "")
            match = GmObject.decode_html_text(match)
            names.append(match)

        artists = []
        matches = re.findall('<td class="Tracks" colspan="10" align="left">(.+?)</td>', html)
        for match in matches:
            match = match.replace("<b>", "")
            match = match.replace("</b>", "")
            match = match.split()[0]
            match = GmObject.decode_html_text(match)
            artists.append(match)

        thumbnails = []
        matches = re.findall('<img [^/]+ class="thumb-img" [^/]+ src="([^"]+)"', html)
        for match in matches:
            thumbnails.append(match)
        # 上面的的正则表达式同样匹配艺术家头像，位置在第一，所以要去掉。
        thumbnails = thumbnails[1:]

        songlists = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "artist":artists[i], "thumbnailLink":thumbnails[i]}
            album = Album()
            album.parse_dict(dict)
            songlists.append(album)
        return songlists

    def load_songlists(self):
        template = "http://www.google.cn/music/artist?id=%s"
        url = template % self.id

        logger.info('读取艺术家专辑地址：%s', url)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songlists = self.parse_html(html)
        self.songlists.extend(songlists)
        return songlists

class DirTag(DirTopiclistingdir):
    '''专辑标签'''

    def __init__(self, id):
        Directory.__init__(self)
        self.id = id
        self.load_songlists()

    def load_songlists(self, start=0, number=20):
        template = "http://www.google.cn/music/tag?q=%s&cat=song&type=topics&start=%d&num=%d"
        url = template % (self.id, start, number + 1)

        logger.info('读取专辑标签地址：%s', url)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songlists = self.parse_html(html)
        if len(songlists) == number + 1:
            self.has_more = True
            songlists.pop()
        else:
            self.has_more = False
        self.songlists.extend(songlists)
        return songlists

class DirStarrecc(Directory):
    '''大牌私房歌歌手列表'''

    def __init__(self):
        Directory.__init__(self)
        self.load_songlists()

    def load_songlists(self):
        template = "http://www.google.cn/music/starrecommendationdir?num=100"
        url = template

        logger.info('读取大牌私房歌歌手列表地址：%s', url)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songlists = self.parse_html(html)
        self.songlists.extend(songlists)
        return songlists

    def parse_html(self, html):
        html = urllib.unquote(html)

        ids = []
        names = []
        matches = re.findall('<div class="artist_name"><a .+?sys:star_recc:(.+?)&.+?>(.+?)</a></div>', html)
        for match in matches:
            id = match[0]
            name = GmObject.decode_html_text(match[1])
            ids.append(id)
            names.append(name)

        descriptions = []
        matches = re.findall('<div class="song_count">(.+?)</div>', html, re.DOTALL)
        for match in matches:
            match = GmObject.decode_html_text(match)
            descriptions.append(match)

        thumbnails = []
        matches = re.findall('<div class="artist_thumb">.+?src="(.+?)".+?</div>', html, re.DOTALL)
        for match in matches:
            thumbnails.append(match)

        songlists = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "descriptions":descriptions[i],
                    "thumbnailLink":thumbnails[i]}
            starrecc = Starrecc()
            starrecc.parse_dict(dict)
            songlists.append(starrecc)
        return songlists
