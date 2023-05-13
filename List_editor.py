from PyQt5.QtCore import Qt as Qtt
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from PyQt5 import Qt, QtWidgets
import Var
import Build_Editor
import Client_Editor


class ListEditor(Qt.QDialog):

    def __init__(self, flag):
        super().__init__()

        # Прорисовка окна приложения
        self.setGeometry(0, 0, 600, 600)
        self.setFixedSize(600, 600)
        self.setWindowFlags(Qtt.CustomizeWindowHint | Qtt.WindowCloseButtonHint)
        self.sender = flag
        if self.sender:
            self.setWindowTitle('Список зданий')
            self.label = Qt.QLabel('Редактирование списка зданий')
            self.query = 'SELECT * FROM buildings ORDER BY id'
        else:
            self.setWindowTitle('Список клиентов')
            self.label = Qt.QLabel('Редактирование списка клиентов')
            self.query = 'SELECT * FROM clients ORDER BY id'

        self.label.setStyleSheet("color:black;"
                                 "font: bold 18pt 'Arial'")
        self.label.setAlignment(Qtt.AlignCenter)

        self.list_table = Qt.QTableWidget()
        self.list_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        if self.sender:
            self.add_button = Qt.QPushButton('Добавить')

        self.layout = Qt.QVBoxLayout(self)
        self.table_layout = Qt.QHBoxLayout()
        self.table_layout.addWidget(self.list_table)
        self.layout.addWidget(self.label)
        self.layout.addLayout(self.table_layout)
        if self.sender:
            self.layout.addWidget(self.add_button)

        self.fil_table()

        if self.sender:
            self.add_button.clicked.connect(self.add)

    def fil_table(self):
        self.list_table.clear()
        self.list_table.setRowCount(0)
        self.list_table.setColumnCount(4)
        if self.sender:
            self.list_table.setHorizontalHeaderLabels(["ID", "Адрес", "Площадь", "Изменить"])
        else:
            self.list_table.setHorizontalHeaderLabels(["ID", "ФИО", "Телефон", "Изменить"])

        Var.cursor.execute(self.query)

        Var.connection.commit()
        rec = Var.cursor.fetchall()

        for row in rec:
            row_count = self.list_table.rowCount()
            self.list_table.insertRow(row_count)

            item = QTableWidgetItem(str(row[0]))
            item.setTextAlignment(Qtt.AlignCenter)
            self.list_table.setItem(row_count, 0, item)

            item = QTableWidgetItem(bytes(str(row[1]), 'cp1251').decode('cp866'))
            self.list_table.setItem(row_count, 1, item)

            if self.sender:
                item = QTableWidgetItem(str(row[2]))
            else:
                item = QTableWidgetItem('+7' + str(row[2]))
            item.setTextAlignment(Qtt.AlignCenter)
            self.list_table.setItem(row_count, 2, item)

            item = Qt.QPushButton('✍')
            item.clicked.connect(self.edit_btn)
            self.list_table.setCellWidget(row_count, 3, item)

            self.list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.list_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            if self.sender:
                self.list_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.list_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            self.list_table.resizeRowsToContents()

    def edit_btn(self):
        self.cur_id = self.list_table.item(self.list_table.currentRow(), 0).text()
        if self.sender:
            self.edit = Build_Editor.EditBuild(self.cur_id)
        else:
            self.edit = Client_Editor.EditClient(self.cur_id)
        self.edit.exec_()
        self.fil_table()

    def add(self):
        self.edit = Build_Editor.EditBuild(0)

        self.edit.exec_()
        self.fil_table()

