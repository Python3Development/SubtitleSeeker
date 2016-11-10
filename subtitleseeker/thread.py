from PyQt5 import QtCore
from subtitleseeker import model, network


class DownloadThread(QtCore.QThread):
    # Arguments: (Model, State, Progress Increment)
    state_changed = QtCore.pyqtSignal(model.SubtitleSearchModel, int, int)

    def __init__(self):
        super().__init__()
        self.q = None
        self.engine_url = None

    def run(self):
        if self.q:
            while True:
                item = self.q.get()
                self.__process(item)
                self.q.task_done()

    def __process(self, item):
        state = item.state
        if state == 0:
            # In a sequential run (1 > 2 > 3 > 4/5), each increment will have the same weight (1) to total 4
            self.state_changed.emit(item, 1, 1)
        elif state == 1:
            url = network.search_request(self.engine_url, item.search)
            if url:
                item.url = url
                self.state_changed.emit(item, 2, 1)
            else:
                # Stage: 1
                # Progress: 1/4
                # Failure compensation: 3 (1/4 + 3/4 = 100%)
                self.state_changed.emit(item, 5, 3)
        elif state == 2:
            url = network.scrape_request(item.url)
            if url:
                item.url = url
                self.state_changed.emit(item, 3, 1)
            else:
                # Stage: 2
                # Progress: 2/4
                # Failure compensation: 2 (2/4 + 2/4 = 100%)
                self.state_changed.emit(item, 5, 2)
        elif state == 3:
            result = network.download_srt(item.url, item.srt)
            if result:
                self.state_changed.emit(item, 4, 1)
            else:
                # Stage: 3
                # Progress: 3/4
                # Failure compensation: 1 (3/4 + 1/4 = 100%)
                self.state_changed.emit(item, 5, 1)


