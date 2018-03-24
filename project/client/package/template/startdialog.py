# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'startdialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_StartDialog(object):
    def setupUi(self, StartDialog):
        StartDialog.setObjectName("StartDialog")
        StartDialog.resize(270, 157)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("res/favicon.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        StartDialog.setWindowIcon(icon)
        StartDialog.setWindowOpacity(1.0)
        self.verticalLayout = QtWidgets.QVBoxLayout(StartDialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gamename = QtWidgets.QLabel(StartDialog)
        self.gamename.setAlignment(QtCore.Qt.AlignCenter)
        self.gamename.setObjectName("gamename")
        self.verticalLayout.addWidget(self.gamename)
        self.nicknameValue = QtWidgets.QLineEdit(StartDialog)
        self.nicknameValue.setText("")
        self.nicknameValue.setObjectName("nicknameValue")
        self.verticalLayout.addWidget(self.nicknameValue)
        self.serverValue = QtWidgets.QLineEdit(StartDialog)
        self.serverValue.setObjectName("serverValue")
        self.verticalLayout.addWidget(self.serverValue)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.errorMsgText = QtWidgets.QLabel(StartDialog)
        self.errorMsgText.setText("")
        self.errorMsgText.setObjectName("errorMsgText")
        self.horizontalLayout.addWidget(self.errorMsgText)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.ConnectButton = QtWidgets.QPushButton(StartDialog)
        self.ConnectButton.setObjectName("ConnectButton")
        self.horizontalLayout.addWidget(self.ConnectButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(StartDialog)
        QtCore.QMetaObject.connectSlotsByName(StartDialog)

    def retranslateUi(self, StartDialog):
        _translate = QtCore.QCoreApplication.translate
        StartDialog.setWindowTitle(_translate("StartDialog", "Hello Game - Start a game"))
        self.gamename.setText(_translate("StartDialog", "<html><head/><body><p><span style=\" font-size:18pt; font-weight:600; color:#ff0000;\">H</span><span style=\" font-size:18pt; font-weight:600;\">e</span><span style=\" font-size:18pt; font-weight:600; color:#ffaa00;\">l</span><span style=\" font-size:18pt; font-weight:600;\">l</span><span style=\" font-size:18pt; font-weight:600; color:#55aa00;\">o</span><span style=\" font-size:14pt; font-weight:600;\"/><span style=\" font-size:11pt;\">Game</span></p></body></html>"))
        self.nicknameValue.setPlaceholderText(_translate("StartDialog", "Nickname"))
        self.serverValue.setPlaceholderText(_translate("StartDialog", "Server"))
        self.ConnectButton.setText(_translate("StartDialog", "Connect"))

