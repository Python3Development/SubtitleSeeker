from PyQt5 import QtWidgets


def confirm(parent, title, message):
    answer = QtWidgets.QMessageBox.question(parent, title, message, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
    return answer == QtWidgets.QMessageBox.Yes


def alert(parent, title, message):
    QtWidgets.QMessageBox.warning(parent, title, message)