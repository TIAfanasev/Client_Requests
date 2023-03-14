from PyQt5.QtCore import Qt as Qtt
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem
from PyQt5 import Qt, QtWidgets
import sys
import psycopg2


class App(Qt.QWidget):

    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 1000, 600)
        self.table = Qt.QTableWidget()
        self.label = Qt.QLabel('Пользовательские заявки')
        self.label.setStyleSheet("color:black;"
                                 "font: bold 20pt 'Arial'")
        self.checkbox_process = Qt.QCheckBox('Необработанные заявки')
        self.label.setAlignment(Qtt.AlignCenter)

        check_layout = Qt.QHBoxLayout()
        check_layout.addWidget(self.checkbox_process)
        check_layout.setAlignment(Qtt.AlignRight)
        v_layout = Qt.QVBoxLayout(self)
        table_layout = Qt.QHBoxLayout()
        table_layout.addWidget(self.table)
        v_layout.addWidget(self.label)
        v_layout.addLayout(check_layout)
        v_layout.addLayout(table_layout)

        self.table_filling()

    def table_filling(self):
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(
            ["ID", "ФИО", "Адрес помещения", "Дата заявки", "Выполнение", "Телефон", "Telegram", "WhatsApp", "Viber",
             "Email"])
        state = self.checkbox_process.checkState()
        if state:
            display_query = 'SELECT * FROM apps WHERE ready = False'
        else:
            display_query = 'SELECT * FROM apps'

        cursor.execute(display_query)

        connection.commit()
        records = cursor.fetchall()

        for row in records:
            work_query = 'SELECT fio FROM clients WHERE id = %s'
            cursor.execute(work_query, (row[1],))
            connection.commit()
            records = cursor.fetchall()
            client_name = records[0][0]

            work_query = 'SELECT address FROM houses WHERE id = %s'
            cursor.execute(work_query, (row[2],))
            connection.commit()
            records = cursor.fetchall()
            house_address = records[0][0]

            work_query = 'SELECT phone FROM clients WHERE id = %s'
            cursor.execute(work_query, (row[1],))
            connection.commit()
            records = cursor.fetchall()
            phone = records[0][0]

            work_query = 'SELECT email FROM clients WHERE id = %s'
            cursor.execute(work_query, (row[1],))
            connection.commit()
            records = cursor.fetchall()
            mail = records[0][0]

            row_count = self.table.rowCount()
            self.table.insertRow(row_count)
            self.table.setItem(row_count, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(row_count, 1, QTableWidgetItem(str(client_name)))
            self.table.setItem(row_count, 2, QTableWidgetItem(house_address))
            self.table.setItem(row_count, 3, QTableWidgetItem(str(row[3])))
            self.table.setItem(row_count, 4, QTableWidgetItem("Yes" if row[4] is True else "No"))
            self.table.setItem(row_count, 5, QTableWidgetItem(str('+7') + str(phone)))
            self.table.setCellWidget(row_count, 7,
                                     QtWidgets.QLabel(f"<a href='https://wa.me/7{phone}'>Тык</a>", openExternalLinks=True))
            self.table.setCellWidget(row_count, 8,
                                     QtWidgets.QLabel(f"<a href='viber://chat?number=%2B7{phone}'>Тык</a>", openExternalLinks=True))
            self.table.setItem(row_count, 9, QTableWidgetItem(str(mail)))
            self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            # table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
            # table.horizontalHeader().setStretchLastSection(True)
            # table.setWordWrap(True)
            # table.horizontalHeader().setStretchLastSection(True)
            # table.horizontalHeader().setSectionResizeMode(
            #    QtWidgets.QHeaderView.Stretch)


if __name__ == '__main__':
    connection = psycopg2.connect(
        database="clapdb",
        user="postgres",
        password="12345",
        host="127.0.0.1",
        port="5432"
    )
    cursor = connection.cursor()

    app = Qt.QApplication(sys.argv)
    w = App()
    w.showMaximized()
    app.exec()
