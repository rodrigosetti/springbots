#! /usr/bin/python

import sys
from PyQt5 import QtGui, QtWidgets
from mainwindow import MainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()

    window.showMaximized()
    sys.exit(app.exec_())
