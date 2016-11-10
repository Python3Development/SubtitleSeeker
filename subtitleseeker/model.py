import os
from subtitleseeker import util

STATE = ('Indeterminate', 'Searching', 'Scraping', 'Downloading', 'Complete', 'Failed')


class SubtitleSearchModel(object):
    def __init__(self, file):
        self.file = file
        self.icon = util.file_icon(file)
        self.url = None
        self.__search = None
        self.__clean = False
        self.__custom = False
        self.__state = 0
        self.__setup()

    # region Setup
    def __setup(self):
        path_split = os.path.split(self.file)
        if os.path.isfile(self.file):
            file_split = os.path.splitext(path_split[1])
            self.name = file_split[0]
            self.ext = file_split[1]
            self.srt = os.path.splitext(self.file)[0] + '.srt'
        else:
            self.name = path_split[1]
            self.ext = ''
            self.srt = self.file + '.srt'

        self.search = self.name

    # endregion

    # region Properties, getters and setters
    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        self.__state = state if state < len(STATE) else 1

    @property
    def search(self):
        return self.__search

    @search.setter
    def search(self, search):
        self.__search = search
        self.__custom = (self.name != search)

    @property
    def clean(self):
        return self.__clean

    @clean.setter
    def clean(self, clean):
        self.__clean = clean
        if not self.__custom:
            self.__search = util.clean_string(self.name) if self.__clean else self.name
    # endregion

    # region Methods
    def text(self, id_):
        if id_ == 0:
            return self.name + self.ext
        elif id_ == 1:
            return self.__search
        elif id_ == 2:
            return STATE[self.__state]
        else:
            return None

    def search_changed(self):
        return self.__clean and self.__search != self.name
    # endregion

    pass
