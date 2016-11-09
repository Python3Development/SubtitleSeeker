from operator import methodcaller
from PyQt5 import QtCore, QtWidgets
from subtitleseeker import dialog, util


class RTableView(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__menu = QtWidgets.QMenu(self)
        self.__remove_action = QtWidgets.QAction(util.icon('delete.png'),'Remove', self)
        self.__remove_action.triggered.connect(self.__remove_rows)
        self.__menu.addAction(self.__remove_action)

    def contextMenuEvent(self, event):
        if self.selectionModel().selectedRows():
            self.__menu.exec_(self.mapToGlobal(event.pos()))
        return QtWidgets.QTableView.contextMenuEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            if self.selectionModel().selectedRows():
                self.__remove_rows()
        return QtWidgets.QTableView.keyPressEvent(self, event)

    def __remove_rows(self):
        rows = sorted(self.selectionModel().selectedRows(), key=methodcaller('row'), reverse=True)
        if dialog.confirm(self, "Confirm Delete", "Are you sure you want to delete {} item(s)?".format(len(rows))):
            for r in rows:
                self.model().removeRow(r.row())
            self.clearSelection()
