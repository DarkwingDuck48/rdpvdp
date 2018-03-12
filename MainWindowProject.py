import sys
import os
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, \
    QVBoxLayout, QPushButton, QComboBox, QHBoxLayout, QLabel, QLineEdit, QGroupBox, QCheckBox, QMenu, QTabWidget
from PyQt5.QtCore import QSize, QSettings, QObject, pyqtSignal
from ServersTable import ServersTable
from ConnectionPanel import ConnectionPanel

SETTINGS_PATH = os.path.join(os.getcwd(), "settings.ini")


class ChangeTab(QObject):
    tabChanged = pyqtSignal()


class MainWindowProject(QMainWindow):
    def __init__(self, first_time):
        super().__init__()
        # Window settings
        self.setFixedSize(QSize(480, 360))
        self.setWindowTitle("RDP/VDP")
        if first_time:
            with open(SETTINGS_PATH, 'w') as first_settings:
                first_settings.write('[General]\nlast_login = \n')
                first_settings.write('\n')
                first_settings.write('[Login]\nlast_login=\n')
                first_settings.write('[Servers]\ntest_server=add.your.server')
        self.mainWidget = MainWidget(self)
        self.setCentralWidget(self.mainWidget)

        self.show()


class MainWidget(QWidget):
    def __init__(self, parent,):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.ini = QSettings(SETTINGS_PATH, QSettings.IniFormat)
        self.ini.setIniCodec("utf-8")
        # tabs for application
        self.tabs = QTabWidget()
        self.mainTab = ConnectionPanel(settings=SETTINGS_PATH)
        self.serversTab = ServersTable(settings=SETTINGS_PATH)
        self.tabs.resize(300, 200)
        # Add tabs
        self.tabs.addTab(self.mainTab, "Main")
        self.tabs.addTab(self.serversTab, "Servers")
        self.tabs.currentChanged.connect(self.tab_changed)
        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def tab_changed(self):
        if self.tabs.currentWidget() == self.mainTab:
            if self.serversTab.save_settings_change_tab() == "Value Error":
                self.tabs.setCurrentIndex(2)
            self.mainTab.reload_servers()


if __name__ == '__main__':
    if not os.path.exists(SETTINGS_PATH):
        first_time = True
    else:
        first_time = False
    app = QApplication(sys.argv)
    window = MainWindowProject(first_time)
    sys.exit(app.exec_())