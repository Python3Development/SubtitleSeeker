import os
from subtitleseeker import util

STATE = ('[INVALID]', 'Indeterminate', 'Downloading', 'Complete', 'Failed')


class SubtitleSearch(object):
    def __init__(self, file):
        self.file = file
        self.icon = util.file_icon(file)
        self.__clean = False
        self.__custom = False
        self.__state = 1
        self.__setup()

    # region Setup
    def __setup(self):
        path_split = os.path.split(self.file)
        if os.path.isfile(self.file):
            file_split = os.path.splitext(path_split[1])
            self.name = file_split[0]
            self.ext = file_split[1]
        else:
            self.name = path_split[1]
            self.ext = ''
        self.__search = self.name
        self.srt = os.path.splitext(self.file)[0] + '.srt'
    # endregion

    # region Properties
    @property
    def state(self):
        return self.state

    @state.setter
    def state(self, state):
        self.__state = state if state < len(STATE) else 0

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
    def value(self, index):
        if index == 0:
            return self.name + self.ext
        elif index == 1:
            return self.__search
        elif index == 2:
            return STATE[self.__state]
        else:
            return None

    def value_changed(self):
        return self.__clean and self.__search != self.name
    # endregion

    pass
