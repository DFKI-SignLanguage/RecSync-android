# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'remote_control.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import sys
import argparse
import json
import re

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

import websocket

# The default remote URL to connect to
DEFAULT_CONNECTION_URL = "ws://192.168.5.2:7867/remotecon"

USER_PREFS_FILE = "user_prefs.json"

# Three levels of red
DIM_RED = "#5E1717"
MID_RED = "#992217"
BRIGHT_RED = "#cc2222"


class RemoteController(object):

    def __init__(self, MainWindow, websocket_url: str = DEFAULT_CONNECTION_URL, connect_at_start: bool = True) -> None:
        self._websocket_url = websocket_url

        self.setupUi(MainWindow)

        # Setup the WEB SOCKET
        self.ws = websocket.WebSocket()

        # The 4-hexdigit of the master device
        # Will be updated when remote devices send information.
        self.masterID = None

        if connect_at_start:
            print(f"Connecting to {self._websocket_url}...")
            self.ws.connect(self._websocket_url)
            # TODO -- setup the timer for the websocket ping
            #f_stop = threading.Event()
            #self.asyncTask(f_stop)
        else:
            print("Skipping connection")

    def save_user_prefs(self):

        prefs = {
            "session_id": self.download_prefix_text.text(),
            "download_dir": self.local_dir_path_edit.text(),
            "camera_exposure": self.camera_exposure_line.text(),
            "camera_sensitivity": self.camera_sensitivity_line.text()
        }

        with open(USER_PREFS_FILE, 'w') as file:
            print(f"Saving prefs to '{USER_PREFS_FILE}'...")
            json.dump(obj=prefs, fp=file, indent=2)

    def load_user_prefs(self):
        import os

        if not os.path.exists(USER_PREFS_FILE):
            return

        with open(USER_PREFS_FILE, 'r') as file:
            print(f"Reading prefs from '{USER_PREFS_FILE}'...")
            prefs = json.load(fp=file)

            if "session_id" in prefs:
                self.download_prefix_text.setText(prefs["session_id"])
            if "download_dir" in prefs:
                self.local_dir_path_edit.setText(prefs["download_dir"])
            if "camera_exposure" in prefs:
                self.camera_exposure_line.setText(prefs["camera_exposure"])
            if "camera_sensitivity" in prefs:
                self.camera_sensitivity_line.setText(prefs["camera_sensitivity"])

    def show_error_popup(self, text: str = ""):
        msg = QMessageBox()
        msg.setWindowTitle("Connection Error")
        msg.setText(text)
        msg.setIcon(QMessageBox.Critical)
        msg.exec_()

    def sendCameraSettings(self):
        try:
            exp_fraction = int(self.camera_exposure_line.text())
            exp_ns: int = int(1000000000 / exp_fraction)
            sens: int = int(self.camera_sensitivity_line.text())
            self.ws.send(f"CAMERA_SETTINGS@@{exp_ns},{sens}")
        except Exception as e:
            self.show_error_popup(f"Can't start recording: {e}")
            self.save_user_prefs()
            sys.exit()

    def startRec(self):
        session_prefix = self.download_prefix_text.text()
        if self.isPrefixValid(session_prefix) and self.start_btn.isEnabled():
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.record_label.setStyleSheet('QLabel {;background-color: ' + BRIGHT_RED + ';}')
            try:
                self.ws.send("START_REC@@"+session_prefix)
            except Exception as e:
                self.show_error_popup(f"Can't start recording: {e}")
                self.save_user_prefs()
                sys.exit()

    def stopRec(self):
        if self.stop_btn.isEnabled() and not self.start_btn.isEnabled():
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.record_label.setStyleSheet('QLabel {;background-color: ' + DIM_RED + ';}')
            try:
                self.ws.send("STOP_REC")
            except Exception as e:
                self.show_error_popup(f"Can't stop recording: {e}")
                self.save_user_prefs()
                sys.exit()

    def askStatus(self):
        try:
            self.ws.send("STATUS")
            message = self.ws.recv()

            self.status_textarea.setPlainText(message)
        except Exception as e:
            self.show_error_popup(f"Can't get clients status: {e}")
            self.save_user_prefs()
            sys.exit()

    def parseStatusInfo(self, status: str) -> None:
        # Extract the leader ID from the status text
        pass


    def deleteRemoteContent(self):
        msgBox = QMessageBox()
        msgBox.setText("Are you sure you want to delete all the recordings and related files ?")
        msgBox.setInformativeText("This action cannot be reversed !!!")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec()
        if ret == QMessageBox.Ok:
            try:
                self.ws.send("DELETE_ALL")
            except Exception as e:
                self.show_error_popup(f"Can't delete clients' files: {e}")
                self.save_user_prefs()
                sys.exit()

    def clearStatus(self):
        self.status_textarea.setPlainText("")

    def prefixList(self):
        try:
            self.ws.send("PREFIX_LIST")
        except Exception as e:
            self.show_error_popup(f"Can't ask for clients' prefixes: {e}")
            self.save_user_prefs()
            sys.exit()

    def requestDownload(self):
        endpoint = self.api_input.text()
        download_prefix = self.download_prefix_text.text()
        if self.isPrefixValid(download_prefix):
            try:
                self.ws.send("UPLOAD@@"+endpoint+","+download_prefix)
            except Exception as e:
                self.show_error_popup(f"Can't ask for clients' content: {e}")
                self.save_user_prefs()
                sys.exit()

    def isPrefixValid(self, prefix_text):
        if prefix_text is None or len(prefix_text) == 0:
            self.show_error_popup('Prefix Text Missing')
            return False
        return True

    def phaseAlign(self):
        try:
            self.ws.send("PHASE_ALIGN")
        except Exception as e:
            self.show_error_popup(f"Can't ask for phase alignment: {e}")
            self.save_user_prefs()
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
        # MainWindow.resize(800, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        font = QtGui.QFont()
        font.setPointSize(20)

        #
        # SESSION
        sess_label = QtWidgets.QLabel("Session ID:")
        sess_label.setFont(font)

        self.download_prefix_text = QtWidgets.QLineEdit()
        self.download_prefix_text.setFont(font)
        self.download_prefix_text.setObjectName("prefix_text")

        session_id_layout = QHBoxLayout()
        #session_id_layout.addStretch(1)
        session_id_layout.addWidget(sess_label)
        session_id_layout.addWidget(self.download_prefix_text, 2)
        # session_id_layout.addStretch(1)

        #
        # REC/STOP
        self.start_btn = QtWidgets.QPushButton()
        self.start_btn.setFont(font)
        self.start_btn.setObjectName("pushButton")
        self.start_btn.clicked.connect(self.startRec)

        self.record_label = QtWidgets.QLabel()
        self.record_label.setFont(font)
        self.record_label.setObjectName("record_label")

        self.stop_btn = QtWidgets.QPushButton()
        self.stop_btn.setFont(font)
        self.stop_btn.setObjectName("pushButton_2")
        self.stop_btn.clicked.connect(self.stopRec)
        self.stop_btn.setEnabled(False)

        record_layout = QHBoxLayout()
        record_layout.addStretch(1)
        record_layout.addWidget(self.start_btn, 1)
        record_layout.addWidget(self.record_label)
        # record_layout.addStretch(1)
        record_layout.addWidget(self.stop_btn, 1)
        record_layout.addStretch(1)

        #
        # CLIENTS STATUS
        self.status_clear_btn = QtWidgets.QPushButton()
        self.status_clear_btn.setFont(font)
        self.status_clear_btn.setObjectName("pushButton_5")
        self.status_clear_btn.clicked.connect(self.clearStatus)

        self.status_btn = QtWidgets.QPushButton()
        self.status_btn.setFont(font)
        self.status_btn.setObjectName("pushButton_3")
        self.status_btn.clicked.connect(self.askStatus)

        self.status_textarea = QtWidgets.QPlainTextEdit()
        self.status_textarea.setObjectName("plainTextEdit")
        self.status_textarea.setPlainText("Clients list goes here...")
        self.status_textarea.setReadOnly(True)

        status_layout = QtWidgets.QHBoxLayout()
        status_layout.addStretch(1)
        status_layout.addWidget(self.status_clear_btn)
        status_layout.addWidget(self.status_btn)
        status_layout.addStretch(1)

        #
        # CAMERA SETUP
        camera_exposure_label = QtWidgets.QLabel(text="Exposure: 1/")
        camera_exposure_label.setFont(font)
        self.camera_exposure_line = QtWidgets.QLineEdit("32")
        self.camera_exposure_line.setFont(font)
        camera_sensitivity_label = QtWidgets.QLabel(text="Sensitivity:")
        camera_sensitivity_label.setFont(font)
        self.camera_sensitivity_line = QtWidgets.QLineEdit("240")
        self.camera_sensitivity_line.setFont(font)
        camera_settings_broadcast_btn = QtWidgets.QPushButton(text="Send")
        camera_settings_broadcast_btn.setFont(font)
        camera_settings_broadcast_btn.clicked.connect(self.sendCameraSettings)

        camera_settings_layout = QHBoxLayout()
        camera_settings_layout.addWidget(camera_exposure_label)
        camera_settings_layout.addWidget(self.camera_exposure_line)
        camera_settings_layout.addWidget(camera_sensitivity_label)
        camera_settings_layout.addWidget(self.camera_sensitivity_line)
        camera_settings_layout.addWidget(camera_settings_broadcast_btn)

        #
        # Download control
        self.phase_align_btn = QtWidgets.QPushButton()
        self.phase_align_btn.setFont(font)
        self.phase_align_btn.setObjectName("pushButton_phase")
        self.phase_align_btn.clicked.connect(self.phaseAlign)

        self.prefix_list_btn = QtWidgets.QPushButton()
        self.prefix_list_btn.setFont(font)
        self.prefix_list_btn.setObjectName("prefix_list_button")
        self.prefix_list_btn.clicked.connect(self.prefixList)
        # TODO -- tmp until it is fixed
        self.prefix_list_btn.setEnabled(False)

        self.download_btn = QtWidgets.QPushButton()
        self.download_btn.setFont(font)
        self.download_btn.setObjectName("pushButton_4")
        self.download_btn.clicked.connect(self.requestDownload)

        download_control_layout = QHBoxLayout()
        download_control_layout.addStretch(1)
        download_control_layout.addWidget(self.phase_align_btn)
        # download_control_layout.addWidget(self.prefix_list_btn)
        download_control_layout.addWidget(self.download_btn)
        download_control_layout.addStretch(1)

        #
        # CLIENTS Info

        self.api_input = QtWidgets.QLineEdit()
        self.api_input.setObjectName("textEdit")

        self.delete_btn = QtWidgets.QPushButton()
        self.delete_btn.setFont(font)
        self.delete_btn.setObjectName("pushButton_6")
        self.delete_btn.clicked.connect(self.deleteRemoteContent)

        clients_info_layout = QtWidgets.QGridLayout()
        clients_info_layout.addWidget(self.api_input, 1, 1, 1, 2)
        clients_info_layout.addWidget(QtWidgets.QLabel(""), 2, 0)
        clients_info_layout.addWidget(self.delete_btn, 3, 2)

        #
        # Compose REMOTE CONTROL layout
        remote_control_layout = QVBoxLayout()
        remote_control_layout.addLayout(session_id_layout)
        remote_control_layout.addLayout(record_layout)
        remote_control_layout.addLayout(download_control_layout)
        remote_control_layout.addLayout(status_layout)
        remote_control_layout.addLayout(camera_settings_layout)
        remote_control_layout.addWidget(self.status_textarea)
        remote_control_layout.addLayout(clients_info_layout)

        #
        # Local Analysis layout
        local_dir_label = QtWidgets.QLabel("Local download dir:")
        local_dir_label.setFont(font)
        self.local_dir_path_edit = QtWidgets.QLineEdit()
        local_dir_layout = QHBoxLayout()
        local_dir_layout.addWidget(local_dir_label)
        local_dir_layout.addStretch(1)


        show_latest_video_btn = QtWidgets.QPushButton(text="Play Leader")
        show_latest_video_btn.setFont(font)
        show_latest_video_btn.clicked.connect(self.showLatestMasterVideo)

        local_analysis_layout = QVBoxLayout()
        local_analysis_layout.addLayout(local_dir_layout)
        local_analysis_layout.addWidget(self.local_dir_path_edit)
        local_analysis_layout.addWidget(show_latest_video_btn)
        local_analysis_layout.addStretch(1)

        #
        # Compose main layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(remote_control_layout)
        main_layout.addLayout(local_analysis_layout)
        self.centralwidget.setLayout(main_layout)

        #
        # SETUP MAIN WINDOW
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        #
        # Finalize
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Load user preferences: setting some text in the components.
        self.load_user_prefs()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RecSyncNG - Remote Controller"))

        self.record_label.setText(_translate("MainWindow", "on air"))

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
        self.phase_align_btn.setText(_translate("MainWindow", "Align Phases"))
        self.record_label.setStyleSheet('QLabel {;background-color: ' + DIM_RED + ';}')

    def showLatestMasterVideo(self):
        from dataframes import scan_session_dir
        from pathlib import Path
        import subprocess

        sessionID = self.download_prefix_text.text()
        download_dir = self.local_dir_path_edit.text()

        # We search in the download dir plus the session ID
        download_path = Path(download_dir)
        download_path = download_path / sessionID

        if not download_path.exists():
            self.show_error_popup(f"Path '{str(download_path)}' doesn't exist.")
            return

        try:
            client_ids, dataframes, videos = scan_session_dir(input_dir=download_path)
        except Exception as e:
            self.show_error_popup(f"Exception scanning local dir: {str(e)}")
            return

        if len(client_ids) == 0:
            self.show_error_popup("No clients found.")
            return

        # TODO -- temp test
        self.masterID = '8b50'  # self.masterID

        if self.masterID is None:
            self.show_error_popup("Master ID still unknown.")
            return

        # Scan the list of clients IDs until we find one matching the master ID
        leader_idx = None
        for i, cID in enumerate(client_ids):
            if cID.endswith(self.masterID):
                leader_idx = i
                break

        if leader_idx is None:
            self.show_error_popup(f"No client found for leader ID '{self.masterID}'.")
            return

        mp4_file = videos[leader_idx]
        mp4_path = Path(mp4_file)

        if not mp4_path.exists():
            self.show_error_popup(f"File '{str(mp4_path)}' doesn't exists.")
            return

        print(f"Playing  '{mp4_path}' ...")

        subprocess.run(["open", mp4_path])


#
#
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Graphical interface for remotely controlling the RecSyncNG Android application."
    )
    parser.add_argument(
        "--dont-connect", action="store_true", help="If set, just show the GUI, without connecting to the master device."
    )
    parser.add_argument(
        "--url", type=str, required=False, default=DEFAULT_CONNECTION_URL,
        help=f"Override the default URL websocket address (default: {DEFAULT_CONNECTION_URL})."
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

    # Blocking: shows the GUI
    ret_code = app.exec_()
    rc.save_user_prefs()

    sys.exit(ret_code)
