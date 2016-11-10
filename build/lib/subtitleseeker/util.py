import os
import re
from PyQt5 import QtGui, QtCore, QtWidgets

EXTENSIONS = ('.mkv', '.mp4', '.avi')
PROVIDER = QtWidgets.QFileIconProvider()


# File
def filter_media(dir_):
    return [f.path for f in os.scandir(dir_) if f.is_dir() or os.path.splitext(f.path)[1] in EXTENSIONS]


# Image
def icon(name):
    return QtGui.QIcon(':/img/{}'.format(name))


def file_icon(file):
    return PROVIDER.icon(QtCore.QFileInfo(file))


# String
def clean_string(value):
    # Remove content between square brackets (included) along with trailing dots or spaces
    return re.sub(r'\[[^)]*\]', '', value).strip(' .-')

