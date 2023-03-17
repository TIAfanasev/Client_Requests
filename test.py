from PyQt5.QtCore import Qt as Qtt
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5 import Qt, QtWidgets
import sys
import psycopg2
import string


def one_query(col, tab, row_id):
    work_query = f'SELECT {col} FROM {tab} WHERE id = %s'
    cursor.execute(work_query, (row_id,))
    connection.commit()
    records = cursor.fetchall()
    return records[0][0]


class MainApp(Qt.QWidget):

    def __init__(self):
        super().__init__()

        # Прорисовка окна приложения
        self.setGeometry(0, 0, 1000, 600)
        self.table = Qt.QTableWidget()
        self.label = Qt.QLabel('Пользовательские заявки')
        self.label.setStyleSheet("color:black;"
                                 "font: bold 20pt 'Arial'")
        self.label.setAlignment(Qtt.AlignCenter)
        self.checkbox_process = Qt.QCheckBox('Необработанные заявки')
        self.refresh_btn = Qt.QPushButton('Обновить')
        check_layout = Qt.QHBoxLayout()
        check_layout.addWidget(self.checkbox_process)
        check_layout.addWidget(self.refresh_btn)
        check_layout.setAlignment(Qtt.AlignRight)
        v_layout = Qt.QVBoxLayout(self)
        table_layout = Qt.QHBoxLayout()
        table_layout.addWidget(self.table)
        v_layout.addWidget(self.label)
        v_layout.addLayout(check_layout)
        v_layout.addLayout(table_layout)

        # Проверка изменения состояния чекбокса
        self.checkbox_process.stateChanged.connect(self.state_cb)

        # Сигнал двойного нажатия по элементу таблицы
        self.table.doubleClicked.connect(self.item_doubleclick)

        # Первое заполнение таблицы
        self.table_filling(state=self.checkbox_process.checkState())

        # Нажатие кнопки обновления таблицы
        self.refresh_btn.clicked.connect(self.state_cb)

    # Обработка изменения чекбокса
    def state_cb(self, state):
        self.table_filling(state)

    def item_doubleclick(self):
        self.cur_id = self.table.item(self.table.currentRow(), 0).text()
        if self.table.currentColumn() in [0, 1, 5, 6, 7, 8, 9]:
            self.cur_fio = self.table.item(self.table.currentRow(), 1).text()
            self.cl_id = one_query('client', 'apps', self.cur_id)
            self.cur_phone = self.table.item(self.table.currentRow(), 5).text()
            self.ec = EditClient(self.cl_id, self.cur_fio, self.cur_phone)
            self.ec.show()
        else:
            self.hs_id = one_query('house', 'apps', self.cur_id)
            self.eh = EditHouse(self.hs_id)
            self.eh.show()

    # Заполнение таблицы значениями из БД
    def table_filling(self, state):
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(
            ["ID", "ФИО", "Адрес помещения", "Дата заявки", "Выполнение", "Телефон", "Telegram", "WhatsApp", "Viber",
             "Email"])

        if state:
            display_query = 'SELECT * FROM apps WHERE ready = False'
        else:
            display_query = 'SELECT * FROM apps'

        cursor.execute(display_query)

        connection.commit()
        records = cursor.fetchall()

        for row in records:
            client_name = one_query('fio', 'clients', row[1])

            house_address = one_query('address', 'houses', row[2])

            phone = one_query('phone', 'clients', row[1])

            mail = one_query('email', 'clients', row[1])

            telegram = one_query('telegram', 'clients', row[1])

            row_count = self.table.rowCount()
            self.table.insertRow(row_count)
            self.table.setItem(row_count, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(row_count, 1, QTableWidgetItem(bytes(client_name, 'cp1251').decode('cp866')))
            self.table.setItem(row_count, 2, QTableWidgetItem(bytes(house_address, 'cp1251').decode('cp866')))
            self.table.setItem(row_count, 3, QTableWidgetItem(str(row[3])))
            self.table.setItem(row_count, 4, QTableWidgetItem("Yes" if row[4] is True else "No"))
            self.table.setItem(row_count, 5, QTableWidgetItem('+7' + str(phone)))
            self.table.setCellWidget(row_count, 6,
                                     QtWidgets.QLabel(f"<a href='https://t.me/{telegram}'>Тык</a>", openExternalLinks=True))
            self.table.setCellWidget(row_count, 7,
                                     QtWidgets.QLabel(f"<a href='https://wa.me/7{phone}'>Тык</a>", openExternalLinks=True))
            self.table.setCellWidget(row_count, 8,
                                     QtWidgets.QLabel(f"<a href='viber://chat?number=%2B7{phone}'>Тык</a>", openExternalLinks=True))
            self.table.setItem(row_count, 9, QTableWidgetItem(str(mail)))
            self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            self.table.resizeRowsToContents()

            
            # table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
            # table.horizontalHeader().setStretchLastSection(True)
            # table.setWordWrap(True)
            # table.horizontalHeader().setStretchLastSection(True)
            # table.horizontalHeader().setSectionResizeMode(
            #    QtWidgets.QHeaderView.Stretch)

class EditClient(Qt.QWidget):

    def __init__(self, id_cl, fio_cl, phone_cl):
        super().__init__()

        # Прорисовка окна приложения
        self.setGeometry(0, 0, 600, 600)
        self.setFixedSize(600, 600)

        self.ID_label = Qt.QLabel('ID:')
        self.ID = Qt.QTextEdit()
        self.ID.setText(str(id_cl))
        self.ID.setReadOnly(True)

        self.FIO_label = Qt.QLabel('ФИО:')
        self.FIO = Qt.QTextEdit()
        self.FIO.setText(fio_cl)

        self.Phone_label = Qt.QLabel('Номер телефона:')
        self.Phone = Qt.QTextEdit()
        self.Phone.setText(phone_cl)

        self.tg_cl = one_query('telegram', 'clients', id_cl)
        self.Telegram_label = Qt.QLabel('Telegram:')
        self.Telegram = Qt.QTextEdit()
        self.Telegram.setText(self.tg_cl)

        confirm = Qt.QPushButton('Подтвердить')
        cancel = Qt.QPushButton('Отмена')
        confirm.clicked.connect(self.cnf_cl)
        cancel.clicked.connect(self.cancel_cl)

        v_layout = Qt.QVBoxLayout()
        v_layout.addWidget(self.ID_label)
        v_layout.addWidget(self.ID)
        v_layout.addWidget(self.FIO_label)
        v_layout.addWidget(self.FIO)
        v_layout.addWidget(self.Phone_label)
        v_layout.addWidget(self.Phone)
        v_layout.addWidget(self.Telegram_label)
        v_layout.addWidget(self.Telegram)
        btn_layout = Qt.QHBoxLayout()
        btn_layout.addWidget(confirm)
        btn_layout.addWidget(cancel)
        v_layout.addLayout(btn_layout)
        self.setLayout(v_layout)

    def cnf_cl(self):
        id_cl = self.ID.toPlainText()
        name = self.FIO.toPlainText().encode('cp866').decode('cp1251')
        number = self.Phone.toPlainText()
        tg = self.Telegram.toPlainText()
        line = tg.replace('_', '')
        print(line)
        if not(number[0:2] == '+7' and len(number[2:]) == 10 and number[2:].isdigit()):
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Введите номер в формате: \n +7ХХХХХХХХХХ')
        elif not all([c in string.ascii_lowercase for c in line]):
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Telegram может содержать только \n латинские символы и символ _')
        else:
            number = number[2:]
            work_query = f'UPDATE clients SET fio = \'{name}\', phone = \'{number}\', telegram = \'{tg}\' WHERE id = {id_cl}'
            cursor.execute(work_query)
            connection.commit()
            self.close()

    def cancel_cl(self):
        self.close()


class EditHouse(Qt.QWidget):

    def __init__(self, id_hs):
        super().__init__()

        # Прорисовка окна приложения
        self.setGeometry(0, 0, 600, 600)
        self.setFixedSize(600, 600)

        self.ID_label = Qt.QLabel('ID:')
        self.ID = Qt.QTextEdit()
        self.ID.setText(str(id_hs))
        self.ID.setReadOnly(True)

        self.Address_label = Qt.QLabel('Адрес:')
        self.Address = Qt.QTextEdit()
        self.adr = one_query('address', 'houses', id_hs)
        self.Address.setText(str(bytes(self.adr, 'cp1251').decode('cp866')))

        self.Square_label = Qt.QLabel('Площадь:')
        self.Square = Qt.QTextEdit()
        self.sq = one_query('square', 'houses', id_hs)
        self.Square.setText(str(self.sq))

        self.PicsTable = Qt.QTableWidget()
        self.PicsTable.setRowCount(0)
        self.PicsTable.setColumnCount(2)
        self.PicsTable.setHorizontalHeaderLabels(["ID", "Название файла"])
        self.PicsTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.PicsTable.resizeRowsToContents()

        self.ConfirmButton = Qt.QPushButton('Подтвердить')
        self.CancelButton = Qt.QPushButton('Отмена')
        self.AddButton = Qt.QPushButton('+')

        btn_layout = Qt.QHBoxLayout()
        btn_layout.addWidget(self.ConfirmButton)
        btn_layout.addWidget(self.CancelButton)

        vh_layout = Qt.QVBoxLayout()
        vh_layout.addWidget(self.ID_label)
        vh_layout.addWidget(self.ID)
        vh_layout.addWidget(self.Address_label)
        vh_layout.addWidget(self.Address)
        vh_layout.addWidget(self.Square_label)
        vh_layout.addWidget(self.Square)
        vh_layout.addWidget(self.PicsTable)
        vh_layout.addWidget(self.AddButton)
        vh_layout.addLayout(btn_layout)

        self.setLayout(vh_layout)


if __name__ == '__main__':
    # Подключение к БД
    connection = psycopg2.connect(
        database="clapdb",
        user="postgres",
        password="12345",
        host="127.0.0.1",
        port="5432"
    )
    cursor = connection.cursor()

    app = Qt.QApplication(sys.argv)
    w = MainApp()
    w.show()
    #w.showMaximized()
    try:
        sys.exit(app.exec_())
    finally:
        connection.close()
