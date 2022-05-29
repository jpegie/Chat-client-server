# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chat-client.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Window_Main(object):
    def setupUi(self, Window_Main):
        Window_Main.setObjectName("Window_Main")
        Window_Main.resize(539, 736)
        Window_Main.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(Window_Main)
        self.centralwidget.setObjectName("centralwidget")
        self.Button_SetupFolder = QtWidgets.QPushButton(self.centralwidget)
        self.Button_SetupFolder.setGeometry(QtCore.QRect(10, 40, 501, 31))
        self.Button_SetupFolder.setObjectName("Button_SetupFolder")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(10, 550, 501, 111))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.TextBox_Message = QtWidgets.QTextEdit(self.frame)
        self.TextBox_Message.setGeometry(QtCore.QRect(130, 40, 321, 31))
        self.TextBox_Message.setLineWidth(1)
        self.TextBox_Message.setObjectName("TextBox_Message")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(130, 0, 321, 41))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.Button_AddAttach = QtWidgets.QPushButton(self.frame)
        self.Button_AddAttach.setGeometry(QtCore.QRect(460, 40, 31, 31))
        self.Button_AddAttach.setObjectName("Button_AddAttach")
        self.TextBox_Receiver = QtWidgets.QTextEdit(self.frame)
        self.TextBox_Receiver.setGeometry(QtCore.QRect(10, 40, 111, 31))
        self.TextBox_Receiver.setLineWidth(1)
        self.TextBox_Receiver.setObjectName("TextBox_Receiver")
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setGeometry(QtCore.QRect(10, 0, 111, 41))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.Label_AttachedFile = QtWidgets.QLabel(self.frame)
        self.Label_AttachedFile.setGeometry(QtCore.QRect(130, 70, 321, 41))
        self.Label_AttachedFile.setAlignment(QtCore.Qt.AlignCenter)
        self.Label_AttachedFile.setObjectName("Label_AttachedFile")
        self.Label_AttachedFile_2 = QtWidgets.QLabel(self.frame)
        self.Label_AttachedFile_2.setGeometry(QtCore.QRect(10, 70, 111, 41))
        self.Label_AttachedFile_2.setAlignment(QtCore.Qt.AlignCenter)
        self.Label_AttachedFile_2.setObjectName("Label_AttachedFile_2")
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(10, 80, 501, 51))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.Button_Connect = QtWidgets.QPushButton(self.frame_2)
        self.Button_Connect.setGeometry(QtCore.QRect(400, 10, 91, 31))
        self.Button_Connect.setObjectName("Button_Connect")
        self.label = QtWidgets.QLabel(self.frame_2)
        self.label.setGeometry(QtCore.QRect(10, 10, 81, 31))
        self.label.setObjectName("label")
        self.TextBox_Login = QtWidgets.QTextEdit(self.frame_2)
        self.TextBox_Login.setGeometry(QtCore.QRect(90, 10, 301, 31))
        self.TextBox_Login.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.TextBox_Login.setLineWidth(1)
        self.TextBox_Login.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.TextBox_Login.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.TextBox_Login.setObjectName("TextBox_Login")
        self.Button_Send = QtWidgets.QPushButton(self.centralwidget)
        self.Button_Send.setGeometry(QtCore.QRect(10, 670, 501, 31))
        self.Button_Send.setObjectName("Button_Send")
        self.listWidget_Messages = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget_Messages.setGeometry(QtCore.QRect(10, 140, 501, 401))
        self.listWidget_Messages.setAlternatingRowColors(True)
        self.listWidget_Messages.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.listWidget_Messages.setResizeMode(QtWidgets.QListView.Fixed)
        self.listWidget_Messages.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.listWidget_Messages.setGridSize(QtCore.QSize(25, 25))
        self.listWidget_Messages.setViewMode(QtWidgets.QListView.ListMode)
        self.listWidget_Messages.setModelColumn(0)
        self.listWidget_Messages.setSelectionRectVisible(False)
        self.listWidget_Messages.setItemAlignment(QtCore.Qt.AlignVCenter)
        self.listWidget_Messages.setObjectName("listWidget_Messages")
        self.Label_FolderPath = QtWidgets.QLabel(self.centralwidget)
        self.Label_FolderPath.setGeometry(QtCore.QRect(10, 10, 501, 21))
        self.Label_FolderPath.setAlignment(QtCore.Qt.AlignCenter)
        self.Label_FolderPath.setObjectName("Label_FolderPath")
        Window_Main.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(Window_Main)
        self.statusbar.setObjectName("statusbar")
        Window_Main.setStatusBar(self.statusbar)

        self.retranslateUi(Window_Main)
        QtCore.QMetaObject.connectSlotsByName(Window_Main)

    def retranslateUi(self, Window_Main):
        _translate = QtCore.QCoreApplication.translate
        Window_Main.setWindowTitle(_translate("Window_Main", "chat-client-app"))
        self.Button_SetupFolder.setText(_translate("Window_Main", "Set folder for files"))
        self.label_3.setText(_translate("Window_Main", "Message"))
        self.Button_AddAttach.setText(_translate("Window_Main", "+"))
        self.label_4.setText(_translate("Window_Main", "Recipient"))
        self.Label_AttachedFile.setText(_translate("Window_Main", "..."))
        self.Label_AttachedFile_2.setText(_translate("Window_Main", "Attached file:"))
        self.Button_Connect.setText(_translate("Window_Main", "Connect"))
        self.label.setText(_translate("Window_Main", "Your login"))
        self.Button_Send.setText(_translate("Window_Main", "Send"))
        self.Label_FolderPath.setText(_translate("Window_Main", "here is gonna be folder\'s path for files..."))