# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'remote_control.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import sys
import argparse

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import websocket
import threading

# The default remote URL to connect to
CONNECTION_URL = "ws://192.168.5.2:7867/remotecon"

# Three levels of red
DIM_RED = "#5E1717"
MID_RED = "#992217"
BRIGHT_RED = "#cc2222"


class RemoteController(object):

    def __init__(self, MainWindow, websocket_url: str = CONNECTION_URL, connect_at_start: bool = True) -> None:
        self._websocket_url = websocket_url

        self.setupUi(MainWindow)

        # Setup the WEB SOCKET
        self.ws = websocket.WebSocket()

        if connect_at_start:
            print(f"Connecting to {self._websocket_url}...")
            self.ws.connect(self._websocket_url)
            # TODO -- setup the timer for the websocket ping
            #f_stop = threading.Event()
            #self.asyncTask(f_stop)
        else:
            print("Skipping connection")

    def save_last_prefix_text(self):
        with open('last_prefix.txt', 'w+') as file:
            file.writelines(self.download_prefix_text.toPlainText())

    def show_error_popup(self, text: str = ""):
        msg = QMessageBox()
        msg.setWindowTitle("Connection Error")
        msg.setText(text)
        msg.setIcon(QMessageBox.Critical)
        msg.exec_()

    def startBtn(self):
        session_prefix = self.download_prefix_text.toPlainText()
        self.save_last_prefix_text()
        if self.isPrefix(session_prefix) and self.start_btn.isEnabled():
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.record_icon_btn.setStyleSheet('QPushButton {;background-color: #EE1818;}')
            try:
                self.ws.send("START_REC@@"+session_prefix)
            except Exception as e:
                self.show_error_popup(f"Can't start recording: {e}")
                self.save_last_prefix_text()
                sys.exit()

    def stopBtn(self):
        self.save_last_prefix_text()
        if self.stop_btn.isEnabled() and not self.start_btn.isEnabled():
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.record_icon_btn.setStyleSheet('QPushButton {;background-color: ' + DIM_RED + ';}')
            try:
                self.ws.send("STOP_REC")
            except Exception as e:
                self.show_error_popup(f"Can't stop recording: {e}")
                self.save_last_prefix_text()
                sys.exit()

    def statusBtn(self):
        self.save_last_prefix_text()
        try:
            self.ws.send("STATUS")
            message = self.ws.recv()
            self.status_label.setPlainText(message)
        except Exception as e:
            self.show_error_popup(f"Can't get clients status: {e}")
            self.save_last_prefix_text()
            sys.exit()

    def delete_all_btn(self):
        msgBox = QMessageBox()
        msgBox.setText("Are you sure you want to delete all the recordings and related files ?")
        msgBox.setInformativeText("This action cannot be reversed !!!")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec()
        self.save_last_prefix_text()
        if ret == QMessageBox.Ok:
            try:
                self.ws.send("DELETE_ALL")
            except Exception as e:
                self.show_error_popup(f"Can't delete clients' files: {e}")
                self.save_last_prefix_text()
                sys.exit()

    def clearStatusBtn(self):
        self.status_label.setPlainText("")

    def prefixList(self):
        self.save_last_prefix_text()
        try:
            self.ws.send("PREFIX_LIST")
        except Exception as e:
            self.show_error_popup(f"Can't ask for clients' prefixes: {e}")
            self.save_last_prefix_text()
            sys.exit()

    def downloadBtn(self):
        endpoint = self.api_input.toPlainText()
        download_prefix = self.download_prefix_text.toPlainText()
        self.save_last_prefix_text()
        if self.isPrefix(download_prefix):
            try:
                self.ws.send("UPLOAD@@"+endpoint+","+download_prefix)
            except Exception as e:
                self.show_error_popup(f"Can't ask for clients' content: {e}")
                self.save_last_prefix_text()
                sys.exit()

    def isPrefix(self, prefix_text):
        if prefix_text is None or len(prefix_text) == 0:
            self.show_error_popup('Prefix Text Missing')
            return False
        return True

    def phaseAlign(self):
        self.save_last_prefix_text()
        try:
            self.ws.send("PHASE_ALIGN")
        except Exception as e:
            self.show_error_popup(f"Can't ask for phase alignment: {e}")
            self.save_last_prefix_text()
            sys.exit()

#     def asyncTask(self, f_stop):
#         self.ws.send("PING")
#         self.ws.recv()
#         if not f_stop.is_set():
#                 # call f() again in 60 seconds
#                 threading.Timer(5, self.asyncTask, [f_stop]).start()

    def setupUi(self, MainWindow):

        # Setup the GUI
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        font = QtGui.QFont()
        font.setPointSize(19)


        self.record_icon_btn = QtWidgets.QPushButton(self.centralwidget)
        self.record_icon_btn.setGeometry(QtCore.QRect(350, 140, 40, 30))
        self.record_icon_btn.setFont(font)
        self.record_icon_btn.setObjectName("record_icon_btn")

        self.start_btn = QtWidgets.QPushButton(self.centralwidget)
        self.start_btn.setGeometry(QtCore.QRect(130, 120, 161, 61))
        self.start_btn.setFont(font)
        self.start_btn.setObjectName("pushButton")
        self.start_btn.clicked.connect(self.startBtn)

        self.stop_btn = QtWidgets.QPushButton(self.centralwidget)
        self.stop_btn.setGeometry(QtCore.QRect(430, 120, 161, 61))
        self.stop_btn.setFont(font)
        self.stop_btn.setObjectName("pushButton_2")
        self.stop_btn.clicked.connect(self.stopBtn)
        self.stop_btn.setEnabled(False)

        self.status_btn = QtWidgets.QPushButton(self.centralwidget)
        self.status_btn.setGeometry(QtCore.QRect(280, 200,  161, 61))
        self.status_btn.setFont(font)
        self.status_btn.setObjectName("pushButton_3")
        self.status_btn.clicked.connect(self.statusBtn)

        self.api_input = QtWidgets.QTextEdit(self.centralwidget)
        self.api_input.setGeometry(QtCore.QRect(143, 450, 451, 31))
        self.api_input.setObjectName("textEdit")
        self.download_prefix_text = QtWidgets.QTextEdit(self.centralwidget)
        self.download_prefix_text.setGeometry(QtCore.QRect(180, 80, 380, 31))
        self.download_prefix_text.setObjectName("prefix_text")
        try:
            with open('last_prefix.txt','r+') as file:
                data = file.readlines()
            if len(data) > 0:
                self.download_prefix_text.setText(data[0])
        except:
            pass

        self.prefix_list_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prefix_list_btn.setGeometry(QtCore.QRect(120, 380, 241, 61))
        self.prefix_list_btn.setFont(font)
        self.prefix_list_btn.setObjectName("prefix_list_button")
        self.prefix_list_btn.clicked.connect(self.prefixList)
        # TODO -- tmp until it is fixed
        self.prefix_list_btn.setEnabled(False)

        self.download_btn = QtWidgets.QPushButton(self.centralwidget)
        self.download_btn.setGeometry(QtCore.QRect(380, 380, 241, 61))
        self.download_btn.setFont(font)
        self.download_btn.setObjectName("pushButton_4")
        self.download_btn.clicked.connect(self.downloadBtn)

        self.delete_btn = QtWidgets.QPushButton(self.centralwidget)
        self.delete_btn.setGeometry(QtCore.QRect(450, 520, 161, 50))
        self.delete_btn.setFont(font)
        self.delete_btn.setObjectName("pushButton_6")
        self.delete_btn.clicked.connect(self.delete_all_btn)

        self.phase_align_btn = QtWidgets.QPushButton(self.centralwidget)
        self.phase_align_btn.setGeometry(QtCore.QRect(120,520, 161, 50))
        self.phase_align_btn.setFont(font)
        self.phase_align_btn.setObjectName("pushButton_phase")
        self.phase_align_btn.clicked.connect(self.phaseAlign)

        self.status_label = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.status_label.setGeometry(QtCore.QRect(173, 280, 381, 91))
        self.status_label.setObjectName("plainTextEdit")

        self.status_clear_btn = QtWidgets.QPushButton(self.centralwidget)
        self.status_clear_btn.setGeometry(QtCore.QRect(560, 341, 31, 31))
        self.status_clear_btn.setFont(font)
        self.status_clear_btn.setObjectName("pushButton_5")
        self.status_clear_btn.clicked.connect(self.clearStatusBtn)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RecSyncNG - Remote Controller"))

        self.record_icon_btn.setText(_translate("MainWindow", ""))

        self.start_btn.setText(_translate("MainWindow", "Record"))

        self.stop_btn.setText(_translate("MainWindow", "Stop"))

        self.status_btn.setText(_translate("MainWindow", "Status"))

        self.status_clear_btn.setText(_translate("MainWindow", "X"))
        self.status_clear_btn.setStyleSheet('QPushButton {;color: ' + MID_RED + ';}')

        self.delete_btn.setText(_translate("MainWindow", "Empty Devices"))
        self.delete_btn.setStyleSheet('QPushButton {;background-color: ' + MID_RED + ';}')

        self.api_input.setPlaceholderText(_translate("MainWindow", "Please enter the api endpoint where you want the files to be uploaded."))

        self.download_prefix_text.setPlaceholderText(_translate("MainWindow", " Enter Session Prefix"))
        self.download_btn.setText(_translate("MainWindow", "Download"))

        self.prefix_list_btn.setText(_translate("MainWindow", "Prefix List"))
        self.phase_align_btn.setText(_translate("MainWindow", "Phase Align"))
        self.record_icon_btn.setStyleSheet('QPushButton {;background-color: ' + DIM_RED + ';}')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Graphical interface for remotely controlling the RecSyncNG Android application."
    )
    parser.add_argument(
        "--dont-connect", action="store_true", help="If set, just show the GUI, without connecting to the master device."
    )
    parser.add_argument(
        "--url", type=str, required=False, default=CONNECTION_URL,
        help=f"Override the default URL websocket address (default: {CONNECTION_URL})."
    )

    args = parser.parse_args()
    dont_connect = args.dont_connect
    app_url = args.url
    print(f"don't connect={dont_connect}, app_url={app_url}")

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    print("Instance...")
    rc = RemoteController(MainWindow, websocket_url=app_url, connect_at_start=not dont_connect)

    print("Showing...")
    MainWindow.show()

    sys.exit(app.exec_())
