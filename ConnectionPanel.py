import psutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QHBoxLayout, QLabel, \
    QLineEdit, QGroupBox, QCheckBox
from PyQt5.QtCore import QSettings, QProcess
from Start_VPN import startVPN
from styles import Button
from subprocess import Popen

VPN_SERVERS = ["Swindon", "Singapore", "Monterrey",
               "Plano", "Winston-salem"]


class ConnectionPanel(QWidget):
    def __init__(self, parent=None, settings=None):
        QWidget.__init__(self, parent)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # settings
        self.ini = QSettings(settings, QSettings.IniFormat)
        self.ini.setIniCodec("utf-8")

        self.last_login = ""
        self.ALIAS_DICT = {}
        self.VPN_SERVERS = {}
        self.load_settings()

        vpn_layout_1 = QHBoxLayout()
        vpn_layout_2 = QHBoxLayout()

        self.line_login = QLineEdit()
        if self.last_login != "":
            self.line_login.setText(self.last_login)
        else:
            self.line_login.setPlaceholderText("Login")
        self.line_login.setStyleSheet("""
                                                QLineEdit {
                                                    border: 0.5px solid grey;
                                                    border-radius: 2px;
                                                    background: #f3f3f3;                                        
                                                }
                                                QLineEdit:focus {
                                                    border: 0.5px solid grey;
                                                    border-radius: 2px;
                                                    background:white;

                                              }""")
        self.line_password = QLineEdit()
        self.line_password.setEchoMode(QLineEdit.Password)
        self.line_password.setPlaceholderText("Password")
        self.line_password.setStyleSheet("""
                                                QLineEdit {
                                                    border: 0.5px solid grey;
                                                    border-radius: 2px;
                                                    background: #f3f3f3;                                        
                                                }
                                                QLineEdit:focus {
                                                    border: 0.5px solid grey;
                                                    border-radius: 2px;
                                                    background:white;

                                              }""")
        self.line_password.returnPressed.connect(self.enable_vpn)
        vpn_layout_1.addWidget(self.line_login)
        vpn_layout_1.addWidget(self.line_password)
        checkbox_layout = QHBoxLayout()
        self.checkbox = QCheckBox("Remember login")
        self.checkbox.setChecked(True)
        checkbox_layout.addWidget(self.checkbox)
        self.vpn_button = Button("Enable VPN", self.enable_vpn)

        # check that vpn is not started
        proc = []
        for p in psutil.process_iter(attrs=['name']):
            proc.append(p.info['name'])
        if "dsSamProxy.exe" in proc:
            self.vpn_button.setDisabled(True)
        else:
            self.vpn_button.setDisabled(False)

        self.vpn_servers = QComboBox()
        self.vpn_servers.addItems(self.VPN_SERVERS.values())
        vpn_layout_2.addWidget(self.vpn_servers)
        vpn_layout_2.addWidget(self.vpn_button)

        # RDP conection line
        servers_layout = QHBoxLayout()
        self.servers_box = QComboBox()
        self.servers_box.addItems(self.ALIAS_DICT.keys())
        self.servers_box.currentIndexChanged.connect(self.server_property)
        self.servers_connect = Button("RDP connection", self.get_RDP_conn)

        servers_layout.addWidget(self.servers_box)
        servers_layout.addWidget(self.servers_connect)

        # Information group
        self.group_box = QGroupBox()
        self.group_box_layout = QVBoxLayout()
        self.label = QLabel(f"Server adress: {self.ALIAS_DICT[self.servers_box.currentText()]}")
        self.group_box.setLayout(self.group_box_layout)
        self.group_box_layout.addWidget(self.label)
        self.group_box.setTitle("Server information")

        self.main_layout.addLayout(vpn_layout_1)
        self.main_layout.addLayout(checkbox_layout)
        self.main_layout.addLayout(vpn_layout_2)
        self.main_layout.addSpacing(10)
        self.main_layout.addLayout(servers_layout)
        self.main_layout.addWidget(self.group_box)
        self.main_layout.addStretch(2)

        self.show()

    def load_settings(self):
        """
        load settings
        :return:
        """
        self.ini.beginGroup("Login")
        self.last_login = self.ini.value("last_login")
        self.ini.endGroup()

        self.ini.beginGroup("Servers")
        for key in self.ini.childKeys():
            self.ALIAS_DICT.update({key: self.ini.value(key)})
        self.ini.endGroup()

        self.ini.beginGroup('Extended_VPN')

        for key in self.ini.childKeys():
            self.VPN_SERVERS.update({key: self.ini.value(key)})
        self.ini.endGroup()

    def enable_vpn(self):
        """
        Activate VPN
        :return:
        """
        login = self.line_login.text()
        password = self.line_password.text()
        if self.checkbox.isChecked():
            self.ini.setValue("last_login", login)
        else:
            self.settings.setValue("last_login", "")
        response = startVPN(login, password, self.vpn_servers.currentText())
        if response:
            self.vpn_button.setDisabled(True)
        else:
            print("ERRROOOOORRRR!!!!!!")

    def reload_servers(self):

        """
        Update Combobox with servers names when you back from "Servers" tab
        :return:
        """
        old_keys = [self.servers_box.itemText(i) for i in range(0, self.servers_box.count())]
        self.ini.beginGroup("Servers")
        self.ALIAS_DICT = {}
        for key in self.ini.childKeys():
            self.ALIAS_DICT.update({key: self.ini.value(key)})
        for key in self.ALIAS_DICT.keys():
            if key not in old_keys:
                self.servers_box.addItem(key)
        for key in old_keys:
            if key not in self.ini.childKeys():
                self.servers_box.removeItem(self.servers_box.findText(key))
        self.ini.endGroup()


    def get_RDP_conn(self):
        """
        connect by RDP
        :return:
        """
        Popen(f"C:\Windows\System32\mstsc.exe /v {self.ALIAS_DICT[self.servers_box.currentText()]}", shell=True)

    def server_property(self):
        """
        Just show servers property
        :return:
        """
        self.label.setText(f"Server adress: {self.ALIAS_DICT[self.servers_box.currentText()]}")