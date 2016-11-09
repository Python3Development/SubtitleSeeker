import urllib.parse
import logging
from bs4 import BeautifulSoup
from PyQt5 import QtCore
from subtitleseeker import util, constant

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

class DownloadThread(QtCore.QThread):

    def run(self):
        logging.debug('running')
        return
