#!/usr/bin/env python
# -*- coding: utf-8 -*-

# copy this file to gmbox-gtk/setup.py, then run
# python setup.py py2exe
# archive the output "dist" folder

from glob import glob
from distutils.core import setup
import py2exe

setup(
    name = 'gmbox-gtk',
    description = 'Google Music Box GTK',
    version = '0.4',
    windows = [
        {
            'script':'gmbox-gtk.py',
            'icon_resources':[(1, 'data/pixbufs/gmbox.ico')],
        }
    ],
    options = {
        'py2exe': {
            'packages' : 'encodings',
            'includes' : 'cairo, pango, pangocairo, atk, gobject, gio',
            'dist_dir' : 'dist',
        }
    },
    data_files = [
        ('data/glade', glob('data/glade/*')),
        ('data/pixbufs', glob('data/pixbufs/*')),
    ]
)
