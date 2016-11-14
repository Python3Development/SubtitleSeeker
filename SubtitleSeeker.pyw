import sys
import urllib.parse
import webbrowser
from queue import Queue
from time import time
from PyQt5 import QtWidgets, QtGui, QtCore
from subtitleseeker import resources, util, view, constant, model, adapter, dialog, thread


class Window(QtWidgets.QMainWindow):
    q = Queue()
    threads = [thread.DownloadThread() for _ in range(10)]

    def __init__(self):
        super().__init__()
        self.__setup()
        self.__menu()
        self.__layout()
        self.setWindowTitle('SubtitleSeeker')
        self.setWindowIcon(util.icon('app.png'))
        self.resize(800, 600)

    # region Setup
    def __setup(self):
        self.__is_running = False
        self.__tasks = 0
        self.__start_time = 0
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
        self.__progress_bar.setValue(0)

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
        action_layout = QtWidgets.QHBoxLayout()  # Has NO parent, we add it manually
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

    # region Handlers
    def __handle_clean_checkbox_state_change(self, state):
        if self.__adapter:
            clean = (state == QtCore.Qt.Checked)
            self.__adapter.update_clean(clean)

    def __handle_download_button_click(self):
        models = self.__table_view.model().data_set
        if not self.__is_running and models:
            fails = self.__check_run_fails(models)
            self.__execute(fails or models)

    def __handle_item_state_change(self, item, state, progress_inc):
        self.__adapter.update_item_state(item, state)
        # Each item has a total of 4 increments to deliver to the progressbar, one for each state
        # (ref. DownloadThread.__process)
        self.__progress_bar.setValue(self.__progress_bar.value() + progress_inc)
        if state not in (4, 5):
            self.q.put(item)
        else:
            self.__finish_download()
    # endregion

    # region Methods
    def __import(self, dir_):
        if not self.__is_running and dir_:
            files = util.filter_media(dir_)
            if files:
                self.__set_content([model.SubtitleSearchModel(f) for f in files])
            else:
                dialog.alert(self, "Media Not Found", "No media files were found ...")

    def __set_content(self, models):
        self.__adapter = adapter.TableViewAdapter(models, ['File', 'Search', 'State'])
        self.__table_view.setModel(self.__adapter)
        self.__table_view.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        self.__progress_bar.setValue(0)
        self.__status_bar.showMessage('')
    # endregion

    # region Helpers
    def __check_run_fails(self, models):
        fails = [m for m in models if m.state == 5]
        if fails:
            for f in fails:
                f.state = 0
            self.__set_content(fails)
        return fails
    # endregion

    # region Script
    def __execute(self, models):
        self.__tasks = len(models)
        # Multiplier is 4 because each state (4) needs to be reflected in the progress
        # (ref. Window.__handle_item_state_change)
        self.__progress_bar.setRange(0, len(models) * 4)

        if self.__automatic_radio.isChecked():
            self.__auto_download(models)
        else:
            self.__manual_download(models)

    def __finish_download(self):
        self.__tasks -= 1
        print(self.__tasks)
        if self.__tasks == 0:
            self.__is_running = False
            self.__status_bar.showMessage('Done in {:.2f}s'.format(time() - self.__start_time))
            if self.__browser_checkbox.isChecked():
                models = self.__table_view.model().data_set
                fails = [m for m in models if m.state == 5]
                if fails:
                    self.__manual_download(fails)

    def __auto_download(self, models):
        if not self.__is_running:
            self.__start_time = time()
            self.__is_running = True

            engine_url = str(self.__combo_box.currentData())
            for t in self.threads:
                t.engine_url = engine_url
                if not t.isRunning():
                    t.q = self.q
                    t.state_changed.connect(self.__handle_item_state_change)
                    t.daemon = True
                    t.start()

            for m in models:
                self.q.put(m)

    def __manual_download(self, models):
        for item in models:
            url = constant.GOOGLE_SEARCH + urllib.parse.quote(item.search)
            webbrowser.open(url)
    # endregion
    pass

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
