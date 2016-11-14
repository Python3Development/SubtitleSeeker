from PyQt5 import QtGui, QtCore

MARK = QtGui.QBrush(QtCore.Qt.darkGreen)


class TableViewAdapter(QtCore.QAbstractTableModel):
    def __init__(self, data_set, headers, parent=None):
        super().__init__(parent)
        self.data_set = data_set
        self.headers = headers

    # region Override
    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.data_set)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.headers)

    def data(self, index, role=None):
        if not index.isValid():
            return QtCore.QVariant()

        if role == QtCore.Qt.ForegroundRole:
            if index.column() == 1 and self.data_set[index.row()].search_changed():
                return MARK
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return self.data_set[index.row()].icon
        elif role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
            return self.data_set[index.row()].text(index.column())

        return QtCore.QVariant()

    def flags(self, index):
        if index.column() == 1:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role=None):
        self.data_set[index.row()].search = value
        return True

    def headerData(self, column, orientation, role=None):
        if role == QtCore.Qt.DisplayRole:
            return self.headers[column] if orientation == QtCore.Qt.Horizontal else column + 1

    def removeRow(self, row, parent=None, *args, **kwargs):
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        del self.data_set[row]
        self.endRemoveRows()
        return True
    # endregion

    # region Update
    def update_clean(self, clean):
        self.layoutAboutToBeChanged.emit()
        for model in self.data_set:
            model.clean = clean
        self.layoutChanged.emit()

    def update_item_state(self, item, state):
        self.layoutAboutToBeChanged.emit()
        item.state = state
        self.layoutChanged.emit()
    # endregion

    pass
