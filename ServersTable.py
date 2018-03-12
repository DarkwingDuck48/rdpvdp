from PyQt5.QtWidgets import QWidget, QMessageBox, QVBoxLayout, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QSettings


class Button(QPushButton):
    """
    Base class for button creation
    """

    def __init__(self, text, connect, parent=None, fixed=False):
        """
        :param text: Button name
        :param connect: database_path name
        :param parent: parent name
        :param fixed: if true => fixed size is (40,35)
        """
        super().__init__(text, parent)
        self.clicked.connect(connect)
        if fixed:
            self.setFixedSize(24, 20)


class ServersTable(QWidget):
    def __init__(self, parent=None, settings= None):
        QWidget.__init__(self, parent)
        self.table_layout = QVBoxLayout()
        self.setLayout(self.table_layout)
        self.temp_cell = ""
        self.ini = QSettings(settings, QSettings.IniFormat)
        self.ini.setIniCodec("utf-8")

        self.servers_table = QTableWidget()
        self.servers_table.setColumnCount(2)
        self.servers_table.setHorizontalHeaderLabels(["Server Alias", "Server Name"])
        self.servers_table.setSortingEnabled(True)
        self.load_settings()
        self.table_layout.addWidget(self.servers_table)

        self.button_add = Button("Add", self.add_row)
        self.button_save = Button("Save", self.save_settings_change_tab)
        self.button_delete = Button("Delete", self.del_row)
        butt_layout = QHBoxLayout()
        butt_layout.addStretch(1)
        butt_layout.addWidget(self.button_add)
        butt_layout.addWidget(self.button_delete)
        butt_layout.addWidget(self.button_save)
        self.table_layout.addLayout(butt_layout)

        self.show()

    def clicked_cell(self):
        """
        Get cell text from current cell
        :return:
        """
        x = self.servers_table.currentRow()
        y = self.servers_table.currentColumn()
        self.temp_cell = self.servers_table.item(x, y).text()

    def load_settings(self):
        """
        load settings from file
        :return:
        """
        self.ini.beginGroup("Servers")
        temp_dict = {}
        for key in self.ini.childKeys():
            temp_dict.update({key: self.ini.value(key)})
        self.ini.endGroup()
        i = 0
        while temp_dict:
            if not i:
                self.servers_table.setRowCount(1)
            else:
                self.servers_table.setRowCount(i+1)
            item = temp_dict.popitem()
            self.servers_table.setItem(i, 0, QTableWidgetItem(item[0]))
            self.servers_table.setItem(i, 1, QTableWidgetItem(item[1]))
            i += 1
        self.servers_table.resizeColumnsToContents()

    def save_changes(self):
        """
        Save changes, which done in table without changing rows count
        :return:
        """
        x = self.servers_table.currentRow()
        y = self.servers_table.currentColumn()
        if self.temp_cell != self.servers_table.item(x, y).text():
            self.ini.beginGroup("Servers")
            if y == 0:
                self.ini.remove(self.temp_cell)
                self.ini.setValue(self.servers_table.item(x, y).text(), self.servers_table.item(x, y+1).text())
            elif y == 1:
                self.ini.setValue(self.servers_table.item(x, y-1).text(), self.servers_table.item(x, y).text())
            self.ini.endGroup()

    def add_row(self):
        """
        Add new row to the table
        :return:
        """
        curr_count = self.servers_table.rowCount()
        self.servers_table.insertRow(curr_count)


    def del_row(self):
        """
        delete selected row
        :return:
        """
        self.servers_table.removeRow(self.servers_table.currentRow())
        print("Row was deleted!")

    def save_settings_change_tab(self):

        """
        Save changes, when tab has changed
        :return:
        """
        all_rows = self.servers_table.rowCount()
        self.ini.beginGroup("Servers")
        total_rows = len(self.ini.childKeys())
        total_keys = self.ini.childKeys()
        self.ini.endGroup()
        if all_rows:
            curr_keys = []
            self.ini.beginGroup("Servers")
            for i in range(0, all_rows):
                try:
                    key = self.servers_table.item(i, 0).text()
                    curr_keys.append(key)
                    value = self.servers_table.item(i, 1).text()
                    self.ini.setValue(key, value)
                except Exception:
                    # todo Add message for this error + paint cells red
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Error!")
                    msg.setWindowTitle("Value Error!")
                    msg.setInformativeText(f"You try to save None value in row {i}")
                    x = msg.exec_()

            # remove deleted lines from settings
            for key in total_keys:
                if key not in curr_keys:
                    self.ini.remove(key)
            self.ini.endGroup()
            self.ini.sync()
