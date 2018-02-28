#!/usr/bin/env python3

# Copyright (C) 2017 Adam Smith

# This file is part of Reaper

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os

import qdarkstyle
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.Qt import QDesktopServices
from PyQt5.QtCore import QUrl
from appdirs import user_data_dir
import traceback

from components.job_queue import Queue
from components.keys import KeyPage
from components.sources import SourceTabs
from components.windows import *
from components.widgets.nodes import PrimaryInputWindow
from components.widgets.progress import ProgressWidget
from components.widgets.queue import QueueTable
from mainwindow import Ui_MainWindow


class Reaper(Ui_MainWindow):
    def __init__(self, window, app, show=True):
        super().__init__()

        self.version = "v2.1"
        self.source_file = 'sources.xml'

        self.window = window

        self.app = app

        if show:
            window.show()

        self.setupUi(window)

        self.window.setWindowIcon(QIcon('ui/icon.png'))
        self.window.setWindowTitle(f"Reaper {self.version}")

        self.advanced_mode = False
        self.dark_mode = False

        self.add_actions()

        if getattr(sys, 'frozen', False):
            self.bundle_dir = sys._MEIPASS
        else:
            self.bundle_dir = os.path.dirname(os.path.abspath(__file__))

        self.data_dir = user_data_dir("Reaper", "UQ")

        # Add windows
        self.add_windows()

        # Create queue page
        self.queue = Queue(self)
        self.queue.job_error.connect(self.error_window.job_error)
        self.queue.job_error_log.connect(self.error_window.log_error)

        self.set_icons()

        # Create queue table
        self.queue_table = QueueTable()
        self.queueLayout.addWidget(self.queue_table)

        # Create window for primary key input
        self.primaryInputWindow = PrimaryInputWindow(window)

        # Create api key page
        self.key_page = KeyPage(self.scrollAreaWidgetContents, self.data_dir)

        # Create sources page
        self.source_tabs = SourceTabs(self, self.key_page, self.source_file, self.primaryInputWindow)

        # Create progress page
        self.progress_page = ProgressWidget(self.queue.job_update, self.tabWidget)
        self.progressLayout.addWidget(self.progress_page)

    def enable_advanced_mode(self, bool):
        self.advanced_mode = bool

    def enable_dark_mode(self, bool):
        if bool:
            self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            self.app.setStyleSheet("")

    def add_actions(self):
        self.actionErrorManager.triggered.connect(self.show_error_manager)
        self.actionAdvanced_mode.toggled.connect(self.enable_advanced_mode)
        self.actionDark_mode.toggled.connect(self.enable_dark_mode)
        self.actionQuit.triggered.connect(self.quit)
        self.actionHelp.triggered.connect(self.open_website)
        self.actionAbout.triggered.connect(self.open_website)
        self.actionWebsite.triggered.connect(self.open_website)

    def add_windows(self):
        self.license_window = LicenseWindow(self.bundle_dir, self.window)
        self.actionLicenses.triggered.connect(self.license_window.pop)

        self.error_window = ErrorWindow(self.window)

        self.settings_window = SettingsWindow(self)
        self.actionSettings.triggered.connect(self.settings_window.show)

    def set_icons(self):
        self.queueUp.setIcon(QIcon(f"{self.bundle_dir}{sep}ui/up.png"))
        self.queueDown.setIcon(QIcon(f"{self.bundle_dir}{sep}ui/down.png"))
        self.queueRemove.setIcon(QIcon(f"{self.bundle_dir}{sep}ui/remove.png"))
        self.window.setWindowIcon(QIcon(f"{self.bundle_dir}{sep}ui/icon.ico"))

    def show_error_manager(self, _):
        self.error_window.show()

    def open_website(self, _):
        QDesktopServices.openUrl(QUrl("http://reaper.social"))

    def quit(self, _):
        self.app.quit()


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        main_window = QtWidgets.QMainWindow()
        ui = Reaper(main_window, app)
        sys.exit(app.exec_())
    except Exception as e:
        with open('log.log', 'a') as f:
            f.write(str(e))
            f.write(traceback.format_exc())
