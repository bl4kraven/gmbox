#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import gtk
import glib

def get_program_root_path():
    '''获取程序根目录地址

    在win下用py2exe打包后，跟直接运行py文件，程序地址有所不同
    '''

    if hasattr(sys, "frozen"):
        program_file_path = unicode(sys.executable, sys.getfilesystemencoding())
        program_root_path = os.path.dirname(program_file_path)
    else:
        program_file_path = unicode(os.path.abspath(__file__), sys.getfilesystemencoding())
        program_root_path = os.path.dirname(os.path.dirname(program_file_path))
    return program_root_path

PROGRAM_ROOT_PATH = get_program_root_path()

def get_glade_file_path(filename):
    """ 获得glade文件路径"""
    glade_folder_path = "%s/data/glade" % PROGRAM_ROOT_PATH
    return "%s/%s" % (glade_folder_path,  filename)

def get_pixbuf_file_path(filename):
    """ 获得pixbuf文件路径"""
    pixbuf_folder_path = "%s/data/pixbufs" % PROGRAM_ROOT_PATH
    return "%s/%s" % (pixbuf_folder_path,  filename)

def create_icon_dict():
    '''创建图标集'''
    global PROGRAM_ROOT_PATH

    icon_names = ["gmbox", "song", "songlist", "directory", "refresh", "info"]
    icon_dict = {}
    for name in icon_names:
        filename = name + ".png"
        icon_path = get_pixbuf_file_path(filename)
        icon = gtk.gdk.pixbuf_new_from_file(icon_path)
        icon_dict[name] = icon
    return icon_dict

ICON_DICT = create_icon_dict()

def get_default_player():
    '''获取默认播放器路径'''

    if sys.platform == "win32":
        return "C:\\Program Files\\Windows Media Player\\wmplayer.exe";
    else:
        try:
            import gio
            app = gio.app_info_get_default_for_type('audio/mpeg', False)
            cmd = app.get_commandline()
            # 命令中可能有 “%F” 或 “%f”，要去掉。例如 “exaile %F”, 之需要 “exaile”.
            return cmd.split()[0];
        except:
            return ""

def get_download_folder():
    '''获取下载文件夹'''

    download_folder = glib.get_user_special_dir(glib.USER_DIRECTORY_MUSIC)
    if download_folder is None:
        download_folder = os.path.expanduser("~/Music")
    return download_folder

# 默认设置
CONFIG = {
    # 常规
    "download_folder": get_download_folder(),
    "filename_template" : "${ALBUM}/${ARTIST} - ${TITLE}",
    "download_cover" : True,
    "download_lyric" : True,
    # 播放器
    "player_use_internal" : False,
    "player_path" : get_default_player(),
    "player_single" : "${URL}",
    "player_multi" : "${URLS}",
    # 下载程序
    "downloader_use_internal" : True,
    "downloader_path" : "",
    "downloader_single" : "${URL} -O ${FILEPATH}",
    "downloader_multi" : "${URLS}",
    "downloader_mkdir" : True,
    # 杂项
    "show_status_icon" : True,
    "use_http_proxy" : False,
    "http_proxy_url" : "127.0.0.1:8080",
}

def get_config_folder():
    '''获取设置文件夹'''

    config_folder = "%s/gmbox" % glib.get_user_config_dir()
    if config_folder is None:
        config_folder = "%s/config/" % PROGRAM_ROOT_PATH
    return config_folder

CONFIG_FOLDER = get_config_folder()

def load_config_file():
    '''读取配置文件'''

    config_file_path = "%s/gmbox.conf" % CONFIG_FOLDER

    if not os.path.exists(config_file_path):
        return

    config_file = open(config_file_path)
    text = config_file.read()
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        key, value = line.split("=", 1)
        if value in ["True", "true", "yes", "1"]:
            value = True
        if value in ["False", "false", "no", "0"]:
            value = False
        CONFIG[key] = value

def save_config_file():
    '''保存配置文件'''

    if not os.path.exists(CONFIG_FOLDER):
        os.mkdir(CONFIG_FOLDER)

    config_file_path = "%s/gmbox.conf" % CONFIG_FOLDER
    config_file = open(config_file_path, "w")
    for key, value in CONFIG.items():
        config_file.write("%s=%s\n" % (key, value))
    config_file.flush()
    config_file.close()
