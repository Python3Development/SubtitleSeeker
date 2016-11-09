import logging
import sys
import urllib.parse
import webbrowser
from time import time
from queue import Queue
from PyQt5 import QtWidgets, QtGui, QtCore
from subtitleseeker import resources, util, view, constant, model, adapter, dialog, thread

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

# region UI
class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.__setup()
        self.__menu()
        self.__layout()
        # TEMP
        self.__import("C:\\Users\\Maikel\\Documents\\Subtitle Dir")
        self.setWindowTitle('SubtitleSeeker')
        self.setWindowIcon(util.icon('app.png'))
        self.resize(800, 600)

    # region Setup
    def __setup(self):
        self.__models = list()
        self.__adapter = None

    def __menu(self):
        # Status Bar
        self.__status_bar = self.statusBar()
        font = QtGui.QFont()
        font.setPointSize(7)
        self.__status_bar.setFont(font)

        # Menu Bar
        menu_bar = self.menuBar()

        # Menu Actions
        action_import = QtWidgets.QAction(util.icon('folder.png'), '&Import', self)
        action_import.setShortcut('Ctrl+I')
        action_import.triggered.connect(lambda: self.__import(QtWidgets.QFileDialog.getExistingDirectory(parent=self)))

        action_quit = QtWidgets.QAction(util.icon('close.png'), '&Exit', self)
        action_quit.setShortcut('Shift+F4')
        action_quit.triggered.connect(QtWidgets.qApp.quit)

        # Menu
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(action_import)
        file_menu.addSeparator()
        file_menu.addAction(action_quit)

    def __layout(self):
        parent = QtWidgets.QWidget()
        self.setCentralWidget(parent)

        # Table View
        self.__table_view = view.RTableView(parent)
        self.__table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        self.__table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # Progress Bar
        self.__progress_bar = QtWidgets.QProgressBar(parent)
        self.__progress_bar.setAlignment(QtCore.Qt.AlignCenter)

        # Options Box
        options_box = QtWidgets.QGroupBox(parent)
        options_box.setTitle("Options")
        options_box_layout = QtWidgets.QVBoxLayout(options_box)

        clean_checkbox = QtWidgets.QCheckBox('Clean search', options_box)
        clean_checkbox.setToolTip('Remove content between square brackets (inclusive) along with trailing chars')
        clean_checkbox.stateChanged.connect(self.__handle_clean_checkbox_state_change)
        options_box_layout.addWidget(clean_checkbox)

        self.__browser_checkbox = QtWidgets.QCheckBox('Browser fallback', options_box)
        self.__browser_checkbox.setToolTip('Open browser for items that fail to download automatically')
        options_box_layout.addWidget(self.__browser_checkbox)

        options_box_layout.addWidget(QtWidgets.QLabel('Search Engine:', options_box))

        self.__combo_box = QtWidgets.QComboBox(options_box)
        self.__combo_box.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        for key, value in constant.SEARCH_ENGINES:
            self.__combo_box.addItem(util.icon('{}.png'.format(key.lower())), key, value)
        options_box_layout.addWidget(self.__combo_box)

        # Download Layout
        action_layout = QtWidgets.QHBoxLayout()  # NOTE: Has NO parent, we add it manually
        action_layout.addSpacerItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding))

        self.__automatic_radio = QtWidgets.QRadioButton('Automatic', self)
        self.__automatic_radio.setChecked(True)
        self.__automatic_radio.setToolTip('Search, download and save subtitle files automatically')
        action_layout.addWidget(self.__automatic_radio)

        manual_radio = QtWidgets.QRadioButton('Manual', self)
        manual_radio.setToolTip('Open all items in browser')
        manual_radio.toggled.connect(lambda checked: self.__browser_checkbox.setDisabled(checked))
        action_layout.addWidget(manual_radio)

        download_button = QtWidgets.QPushButton('Download', self)
        download_button.clicked.connect(self.__handle_download_button_click)
        action_layout.addWidget(download_button)

        # Root Vertical Layout
        root_layout = QtWidgets.QVBoxLayout(parent)
        root_layout.addWidget(self.__table_view)
        root_layout.addWidget(self.__progress_bar)
        root_layout.addWidget(options_box)
        root_layout.addLayout(action_layout)
    # endregion

    # region Handlers and Callbacks
    def __handle_clean_checkbox_state_change(self, state):
        if self.__adapter:
            self.__adapter.set_clean(state == QtCore.Qt.Checked)

    def __handle_download_button_click(self):
        if self.__models:
            self.__progress = 0
            self.__progress_bar.setValue(0)
            is_auto = self.__automatic_radio.isChecked()
            has_fallback = self.__browser_checkbox.isChecked()
            search_engine = str(self.__combo_box.currentData())
            #self.__status_bar.showMessage('Downloading...')
            run_ui(self.__models, is_auto, search_engine, has_fallback)
    # endregion

    # region Helpers
    def __import(self, dir_):
        if dir_:
            files = util.filter_media(dir_)
            if files:
                self.__models = [model.SubtitleSearch(f) for f in files]
                self.__adapter = adapter.TableViewAdapter(self.__models, ['File', 'Search', 'State'])
                self.__table_view.setModel(self.__adapter)
                self.__table_view.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeToContents)
            else:
                dialog.alert(self, "Media Not Found", "No media files were found ...")
    # endregion
    pass
# endregion


# region Backend
def run_ui(model_items, auto, search_engine, fallback):
    if model_items:
        if auto:
            __auto_download(model_items, search_engine, fallback)
        else:
            __manual_download(model_items)


def __auto_download(model_items, search_engine, fallback):
    logging.debug('Before thread loop')
    for i in range(5):
        t = thread.DownloadThread()
        t.start()
    logging.debug('After thread loop')


def __manual_download(model_items):
    for item in model_items:
        url = constant.GOOGLE_SEARCH + urllib.parse.quote(item.search)
        webbrowser.open(url)


def finish(total_time, fallback):
    print('({:.2f} s)'.format(total_time))
    if fallback:
        print("Fallback")
# endregion


# region Exception Hook
sys._excepthook = sys.excepthook

def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

sys.excepthook = my_exception_hook
# endregion


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    try:
        sys.exit(app.exec_())
    except:
        pass
