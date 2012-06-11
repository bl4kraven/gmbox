#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import gobject
from libgmbox import (Song, Songlist, Directory,
                      CHARTLISTING_DIR, TAG_DIR)
from config import ICON_DICT
from downloader import Downloader

class CategoryTreeview(gtk.TreeView):

    class CategoryNode():

        def __init__(self, name, id, type):
            self.name = name
            self.id = id
            self.type = type
            self.init_icon()

        def init_icon(self):
            if self.type == Song:
                self.icon = ICON_DICT["song"]
            if self.type == Songlist:
                self.icon = ICON_DICT["songlist"]
            if self.type == Directory:
                self.icon = ICON_DICT["directory"]

    def __init__(self, gmbox):
        gtk.TreeView.__init__(self)
        self.gmbox = gmbox
        self.init_treestore()
        self.init_column()
        self.init_menu()
        self.set_headers_visible(False)
        self.set_model(self.treestore)
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.connect("button-press-event", self.on_button_press_event)

    def init_treestore(self):
        self.treestore = gtk.TreeStore(gobject.TYPE_PYOBJECT)

        # chartlisting
        parent_song = CategoryTreeview.CategoryNode("排行榜 - 歌曲", None, Directory)
        parent_song_iter = self.treestore.append(None, (parent_song,))

        parent_album = CategoryTreeview.CategoryNode("排行榜 - 专辑", None, Directory)
        parent_album_iter = self.treestore.append(None, (parent_album,))

        for value in CHARTLISTING_DIR:
            if "songs" in value[1]:
                node = CategoryTreeview.CategoryNode(value[0], value[1], Song)
                self.treestore.append(parent_song_iter, (node,))
            elif "albums" in value[1]:
                node = CategoryTreeview.CategoryNode(value[0], value[1], Songlist)
                self.treestore.append(parent_album_iter, (node,))

        # tag
        parent_song = CategoryTreeview.CategoryNode("标签 - 歌曲", None, Directory)
        parent_song_iter = self.treestore.append(None, (parent_song,))

        parent_topics = CategoryTreeview.CategoryNode("标签 - 专题", None, Directory)
        parent_topics_iter = self.treestore.append(None, (parent_topics,))

        for value in TAG_DIR:
            node = CategoryTreeview.CategoryNode(value, "tag", Song)
            self.treestore.append(parent_song_iter, (node,))
            node = CategoryTreeview.CategoryNode(value, "tag", Songlist)
            self.treestore.append(parent_topics_iter, (node,))

        # other
        parent_other = CategoryTreeview.CategoryNode("其它", None, Directory)
        parent_other_iter = self.treestore.append(None, (parent_other,))
        node = CategoryTreeview.CategoryNode("最新音乐专题", "topiclistingdir", Songlist)
        self.treestore.append(parent_other_iter, (node,))
        node = CategoryTreeview.CategoryNode("大牌私房歌", "starrecommendationdir", Songlist)
        self.treestore.append(parent_other_iter, (node,))

    def init_column(self):

        def pixbuf_cell_data_func(column, cell, model, iter, data=None):
            category_node = model.get_value(iter, 0)
            cell.set_property("pixbuf", category_node.icon)

        def text_cell_data_func(column, cell, model, iter, data=None):
            category_node = model.get_value(iter, 0)
            cell.set_property("text", category_node.name)

        renderer = gtk.CellRendererPixbuf()
        column = gtk.TreeViewColumn("test")
        column.pack_start(renderer, False)
        column.set_cell_data_func(renderer, pixbuf_cell_data_func)
        renderer = gtk.CellRendererText()
        column.pack_start(renderer)
        column.set_cell_data_func(renderer, text_cell_data_func)
        column.set_resizable(True)
        self.append_column(column)

    def init_menu(self):
        self.menu = gtk.Menu()
        self.menuitem = gtk.MenuItem("获取")
        self.menu.append(self.menuitem)
        self.menu.connect("selection-done", self.on_menu_selection_done)
        self.menuitem.connect("activate", self.on_menuitem_activate)
        self.menu.show_all()

    def analyze_and_search(self, node):
        if node.id == "tag":
            self.gmbox.do_tag(node.name, node.type)
        elif node.id == "topiclistingdir":
            self.gmbox.do_topiclistingdir()
        elif node.id == "starrecommendationdir":
            self.gmbox.do_starrecommendationdir()
        else:
            # chartlisting
            self.gmbox.do_chartlisting(node.name, node.type)

    def on_button_press_event(self, widget, event, data=None):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            model, rows = self.get_selection().get_selected_rows()
            if len(rows) == 0:
                return False
            for path in rows:
                iter = model.get_iter(path)
                if model.iter_depth(iter) != 0:
                    node = model.get_value(iter, 0)
                    self.analyze_and_search(node)
        elif event.button == 3:
            self.menu.popup(None, None, None, event.button, event.time)
            return True

    def on_menu_selection_done(self, widget, data=None):
        self.queue_draw()

    def on_menuitem_activate(self, widget, data=None):
        model, rows = self.get_selection().get_selected_rows()
        if len(rows) == 0:
            return

        for path in rows:
            iter = model.get_iter(path)
            node = model.get_value(iter, 0)
            self.analyze_and_search(node)
        self.get_selection().unselect_all()

class PlaylistTreeview(gtk.TreeView):

    def __init__(self, gmbox):
        gtk.TreeView.__init__(self)
        self.gmbox = gmbox
        self.liststore = gtk.ListStore(gobject.TYPE_PYOBJECT)
        self.ids = []
        self.init_column()
        self.set_model(self.liststore)
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.connect("button-press-event", self.on_button_press_event)

    def init_column(self):

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
        self.append_column(column)

        text = ["艺术家", "专辑", "状态"]
        data = ["artist", "album", "play_status"]
        for i in range(len(text)):
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(text[i], renderer)
            column.set_cell_data_func(renderer, text_cell_data_func, data[i])
            column.set_resizable(True)
            column.set_expand(True)
            self.append_column(column)

    def append_songs(self, songs):
        for song in songs:
            if song.id not in self.ids:
                self.ids.append(song.id)
                self.liststore.append((song,))

    def on_button_press_event(self, widget, event, data=None):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            model, rows = self.get_selection().get_selected_rows()
            if len(rows) == 0:
                return False
            for path in rows:
                iter = model.get_iter(path)
                value = model.get_value(iter, 0)
                self.gmbox.play_songs([value])
        elif event.button == 3:
            songs = []
            model, rows = self.get_selection().get_selected_rows()
            for path in rows:
                iter = model.get_iter(path)
                value = model.get_value(iter, 0)
                if isinstance(value, Song):
                    songs.append(value)
            self.gmbox.popup_content_menu(songs, event, self)
            return True

    def get_next_song(self, song):
        length = len(self.liststore)
        for i in range(length):
            if song == self.liststore[i][0]:
                if i < length - 1:
                    # not the last one
                    return self.liststore[i + 1][0]
                break
        # just return the first one
        return self.liststore[0][0]

    def get_last_song(self, song):
        length = len(self.liststore)
        # is the first one, then return last one
        if song == self.liststore[0][0]:
            return self.liststore[length - 1][0]

        for i in range(length):
            if song == self.liststore[i][0]:
                return self.liststore[i - 1][0]

    def remove_songs(self, songs):
        for row in self.liststore:
            song = row[0]
            if song in songs:
                iter = self.liststore.get_iter(row.path)
                self.liststore.remove(iter)
                self.ids.remove(song.id)

    def clear_songs(self):
        self.liststore.clear()
        self.ids = []

class DownlistTreeview(gtk.TreeView):

    def __init__(self, gmbox):
        gtk.TreeView.__init__(self)
        self.gmbox = gmbox
        self.liststore = gtk.ListStore(gobject.TYPE_PYOBJECT)
        self.ids = []
        self.init_column()
        self.set_model(self.liststore)
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.connect("button-press-event", self.on_button_press_event)

    def init_column(self):

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
        self.append_column(column)

        text = ["艺术家", "专辑", "下载进度", "状态"]
        data = ["artist", "album", "down_process", "down_status"]
        for i in range(len(text)):
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(text[i], renderer)
            column.set_cell_data_func(renderer, text_cell_data_func, data[i])
            column.set_resizable(True)
            column.set_expand(True)
            self.append_column(column)

    def append_songs(self, songs):
        for song in songs:
            if song.id not in self.ids:
                song.remove_lock = False
                self.ids.append(song.id)
                self.liststore.append((song,))

    def on_button_press_event(self, widget, event, data=None):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            model, rows = self.get_selection().get_selected_rows()
            if len(rows) == 0:
                return False
            for path in rows:
                iter = model.get_iter(path)
                value = model.get_value(iter, 0)
                self.gmbox.play_songs([value])
        elif event.button == 3:
            songs = []
            model, rows = self.get_selection().get_selected_rows()
            for path in rows:
                iter = model.get_iter(path)
                value = model.get_value(iter, 0)
                if isinstance(value, Song):
                    songs.append(value)
            self.gmbox.popup_content_menu(songs, event, self)
            return True

    def get_waitting_song(self):
        for row in self.liststore:
            song = row[0]
            if song.down_status in ["等待中"]:
                return song

    def start_downloader(self):
        if not hasattr(self, "downloaders"):
            self.downloaders = 0
        if not hasattr(self, "refreshing"):
            self.refreshing = False

        while self.downloaders < 3:
            song = self.get_waitting_song()
            if song is None:
                break

            song.down_status = "开始下载"
            Downloader(song, self.downloader_callback).start()
            self.downloaders += 1
            if not self.refreshing:
                gobject.timeout_add(1000, self.refresh_treeview)
                self.refreshing = True

    def downloader_callback(self):
        self.downloaders -= 1
        self.start_downloader()

    def refresh_treeview(self):
        self.queue_draw()
        if self.downloaders == 0:
            self.refreshing = False
            return False
        else:
            return True

    def remove_songs(self, songs):
        for row in self.liststore:
            song = row[0]
            if song.remove_lock:
                continue
            if song in songs:
                iter = self.liststore.get_iter(row.path)
                self.liststore.remove(iter)
                self.ids.remove(song.id)

    def clear_songs(self):
        for row in self.liststore:
            song = row[0]
            if song.remove_lock:
                continue
            iter = self.liststore.get_iter(row.path)
            self.liststore.remove(iter)
            self.ids.remove(song.id)
