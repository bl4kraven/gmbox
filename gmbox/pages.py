#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import gobject
import threading
from libgmbox import Song, Songlist
from config import ICON_DICT

class ResultPageLabel(gtk.EventBox):

    def __init__(self, result_page, page_text, page_key):
        gtk.EventBox.__init__(self)
        self.result_page = result_page
        self.page_text = page_text
        self.page_key = page_key
        self.init_layout()
        self.show_all()

    def init_layout(self):
        self.add(gtk.Label(self.page_text))

class ResultPage(gtk.ScrolledWindow):

    class RefreshNode():

        def __init__(self, name):
            self.name = name
            self.artist = ""
            self.album = ""
            self.icon = ICON_DICT["refresh"]
            self.loaded = False

    class InfoNode():

        def __init__(self, name):
            self.name = name
            self.artist = ""
            self.album = ""
            self.icon = ICON_DICT["info"]
            self.loaded = False

    class LoadSongsThread(threading.Thread):

        def __init__(self, songlist, path, callback):
            threading.Thread.__init__(self)
            self.songlist = songlist
            self.path = path
            self.callback = callback

        def run(self):
            self.songlist.load_songs()
            self.callback(self.songlist, self.path)

    class LoadMoreThread(threading.Thread):

        def __init__(self, target, args, callback):
            threading.Thread.__init__(self)
            self.target = target
            self.args = args
            self.callback = callback

        def run(self):
            result = self.target(self.args[0], self.args[1])
            self.callback(result)

    def __init__(self, gmbox):
        gtk.ScrolledWindow.__init__(self)
        self.gmbox = gmbox

        self.treeview = gtk.TreeView()
        self.init_treeview()

        # scrolled window finally setting
        self.add(self.treeview)
        self.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.show_all()

    def load_result(self, result):
        self.result = result
        if isinstance(self.result, Songlist):
            self.songlist = result
            self.init_liststore()
            self.treeview.set_model(self.liststore)
        else:
            self.directory = result
            self.init_treestore()
            self.treeview.set_model(self.treestore)

    # if something wrong, e.g  no result or network problem
    def load_message(self, text):
        self.liststore = gtk.ListStore(gobject.TYPE_PYOBJECT)
        info_node = ResultPage.InfoNode(text)
        self.liststore.append((info_node,))
        self.treeview.set_model(self.liststore)

    def init_treeview(self):

        def pixbuf_cell_data_func(column, cell, model, iter, data=None):
            value = model.get_value(iter, 0)
            cell.set_property("pixbuf", value.icon)

        def text_cell_data_func(column, cell, model, iter, data=None):
            song = model.get_value(iter, 0)
            cell.set_property("text", getattr(song, data))

        # icon and name
        renderer = gtk.CellRendererPixbuf()
        column = gtk.TreeViewColumn("名称")
        column.pack_start(renderer, False)
        column.set_cell_data_func(renderer, pixbuf_cell_data_func)
        renderer = gtk.CellRendererText()
        column.pack_start(renderer)
        column.set_cell_data_func(renderer, text_cell_data_func, "name")
        column.set_resizable(True)
        column.set_expand(True)
        self.treeview.append_column(column)

        text = ["艺术家", "专辑"]
        data = ["artist", "album"]
        for i in range(len(text)):
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(text[i], renderer)
            column.set_cell_data_func(renderer, text_cell_data_func, data[i])
            column.set_resizable(True)
            column.set_expand(True)
            self.treeview.append_column(column)

        self.treeview.set_model(gtk.ListStore(gobject.TYPE_PYOBJECT))
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.treeview.connect("button-press-event", self.on_button_press_event)
        self.treeview.connect("row-expanded", self.on_treeview_row_expanded)

    def init_liststore(self):
        self.liststore = gtk.ListStore(gobject.TYPE_PYOBJECT)
        self.page_num = 1
        songs = self.songlist.songs
        self.append_songs_to_liststore(songs)

    def init_treestore(self):
        self.treestore = gtk.TreeStore(gobject.TYPE_PYOBJECT)
        self.page_num = 1
        songlists = self.directory.songlists
        self.append_songlists_to_treestore(songlists)

    def append_songs_to_liststore(self, songs):
        for song in songs:
            if not hasattr(song, "artist"):
                song.artist = ""
            if not hasattr(song, "album"):
                song.album = ""
            song.icon = ICON_DICT["song"]
            self.liststore.append((song,))
        if self.result.has_more:
            refresh_node = ResultPage.RefreshNode("载入第 %d 页" % (self.page_num + 1))
            self.liststore.append((refresh_node,))

    def append_songlists_to_treestore(self, songlists):
        refresh_node = ResultPage.RefreshNode("正在读取")
        for songlist in songlists:
            songlist.appended = False
            if not hasattr(songlist, "artist"):
                songlist.artist = ""
            if not hasattr(songlist, "album"):
                songlist.album = ""
            songlist.icon = ICON_DICT["songlist"]
            parent_index = self.treestore.append(None, (songlist,))
            self.treestore.append(parent_index, (refresh_node,))
        if self.result.has_more:
            refresh_node = ResultPage.RefreshNode("载入第 %d 页" % (self.page_num + 1))
            self.treestore.append(None, (refresh_node,))

    def on_treeview_row_expanded(self, widget, iter, path, data=None):
        model = self.treeview.get_model()
        songlist = model.get_value(iter, 0)
        if not songlist.appended:
            load_songs_thread = ResultPage.LoadSongsThread(songlist, path, self.append_songs_to_treestore)
            load_songs_thread.start()

    def append_songs_to_treestore(self, songlist, path):
        songs = songlist.songs
        iter = self.treestore.get_iter(path)
        # remove refresh holder
        refresh_iter = self.treestore.iter_children(iter)
        self.treestore.remove(refresh_iter)
        # append song
        for song in songs:
            if not hasattr(song, "artist"):
                song.artist = ""
            if not hasattr(song, "album"):
                song.album = ""
            song.icon = ICON_DICT["song"]
            self.treestore.append(iter, (song,))
        songlist.appended = True
        self.treeview.expand_to_path(path)

    def on_button_press_event(self, widget, event, data=None):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            model, rows = self.treeview.get_selection().get_selected_rows()
            if len(rows) == 0:
                return False
            for path in rows:
                iter = model.get_iter(path)
                value = model.get_value(iter, 0)
                if isinstance(value, Song):
                    self.gmbox.play_songs([value])
                elif isinstance(value, ResultPage.RefreshNode):
                    if not value.loaded:
                        self.load_more_result()
                        value.loaded = True
        elif event.button == 3:
            songs = []
            model, rows = self.treeview.get_selection().get_selected_rows()
            for path in rows:
                iter = model.get_iter(path)
                value = model.get_value(iter, 0)
                if isinstance(value, Song):
                    songs.append(value)
            self.gmbox.popup_content_menu(songs, event, self)
            return True

    def load_more_result(self):
        if isinstance(self.result, Songlist):
            target = self.songlist.load_songs
            callback = self.append_songs_to_liststore
        else:
            target = self.directory.load_songlists
            callback = self.append_songlists_to_treestore
        args = (self.page_num * 20, 20)
        load_more_thread = ResultPage.LoadMoreThread(target, args, callback)
        load_more_thread.start()
        self.page_num += 1
