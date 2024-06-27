# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'homePage.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 768)
        MainWindow.setMinimumSize(QtCore.QSize(800, 600))
        font = QtGui.QFont()
        font.setKerning(False)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.logo = QtWidgets.QLabel(self.centralwidget)
        self.logo.setGeometry(QtCore.QRect(250, 60, 541, 501))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("../Assets/logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setAlignment(QtCore.Qt.AlignCenter)
        self.logo.setObjectName("logo")
        self.tagLine = QtWidgets.QLabel(self.centralwidget)
        self.tagLine.setGeometry(QtCore.QRect(250, 560, 541, 51))
        font = QtGui.QFont()
        font.setFamily("Island Moments")
        font.setPointSize(24)
        self.tagLine.setFont(font)
        self.tagLine.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tagLine.setAlignment(QtCore.Qt.AlignCenter)
        self.tagLine.setObjectName("tagLine")
        self.findArecipeButton = QtWidgets.QPushButton(self.centralwidget)
        self.findArecipeButton.setGeometry(QtCore.QRect(150, 650, 331, 61))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(139, 196, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(139, 196, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(139, 196, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(139, 196, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(139, 196, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(139, 196, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(139, 196, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(139, 196, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(139, 196, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.findArecipeButton.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setKerning(True)
        self.findArecipeButton.setFont(font)
        self.findArecipeButton.setStyleSheet("background-color: rgb(139, 196, 190);")
        self.findArecipeButton.setObjectName("findArecipeButton")
        self.findArecipeButton.raise_()
        self.tagLine.raise_()
        self.logo.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1024, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tagLine.setText(_translate("MainWindow", "Your Personal Recipe Manager"))
        self.findArecipeButton.setText(_translate("MainWindow", "Find A Recipe"))