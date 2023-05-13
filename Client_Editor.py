from PyQt5.QtCore import Qt as Qtt
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import Qt
import string
import Var


class EditClient(Qt.QDialog):

    def __init__(self, id_cl):
        super().__init__()

        # Прорисовка окна приложения
        self.setGeometry(0, 0, 600, 600)
        self.setWindowTitle('Редактирование данных клиента')
        self.setFixedSize(600, 600)
        self.setWindowFlags(Qtt.CustomizeWindowHint | Qtt.WindowCloseButtonHint)

        self.id_cl = id_cl

        self.ID_label = Qt.QLabel(f'ID: {self.id_cl}')
        self.ID_label.setStyleSheet("font: 10pt 'Tahoma'")

        self.FIO_label = Qt.QLabel('ФИО:')
        self.FIO_label.setStyleSheet("font: 10pt 'Tahoma'")
        self.FIO = Qt.QTextEdit()
        self.FIO.setFontPointSize(10)
        self.FIO.setPlaceholderText('Пример: Иванов Иван Иванович')
        self.fio_cl = Var.one_query('fio', 'clients', self.id_cl)
        self.FIO.setText(bytes(self.fio_cl, 'cp1251').decode('cp866'))

        self.Phone_label = Qt.QLabel('Номер телефона:')
        self.Phone_label.setStyleSheet("font: 10pt 'Tahoma'")
        self.Phone = Qt.QTextEdit()
        self.Phone.setFontPointSize(10)
        self.Phone.setPlaceholderText('Номер телефона в формате +7XXXXXXXXXX')
        self.phone_cl = Var.one_query('phone', 'clients', self.id_cl)
        self.Phone.setText('+7' + self.phone_cl)

        self.Telegram_label = Qt.QLabel('Telegram:')
        self.Telegram_label.setStyleSheet("font: 10pt 'Tahoma'")
        self.Telegram = Qt.QTextEdit()
        self.Telegram.setFontPointSize(10)
        self.Telegram.setPlaceholderText('Пример: @user_name')
        self.tg_cl = Var.one_query('telegram', 'clients', self.id_cl)
        self.Telegram.setText('@' + self.tg_cl)

        self.confirm = Qt.QPushButton('Подтвердить')
        self.cancel = Qt.QPushButton('Отмена')
        self.delete = Qt.QPushButton('Удалить')
        self.delete.setStyleSheet('background-color: #DB4139; border-radius: 6px; color: white;'
                                  'min-width: 10em; padding: 4px')
        self.confirm.clicked.connect(self.cnf_cl)
        self.cancel.clicked.connect(self.cancel_cl)
        self.delete.clicked.connect(self.delete_cl)

        v_layout = Qt.QVBoxLayout()
        v_layout.addWidget(self.ID_label)
        v_layout.addWidget(self.FIO_label)
        v_layout.addWidget(self.FIO)
        v_layout.addWidget(self.Phone_label)
        v_layout.addWidget(self.Phone)
        v_layout.addWidget(self.Telegram_label)
        v_layout.addWidget(self.Telegram)
        btn_layout = Qt.QHBoxLayout()
        btn_layout.addWidget(self.confirm)
        btn_layout.addWidget(self.cancel)
        v_layout.addLayout(btn_layout)
        v_layout.addWidget(self.delete)
        self.setLayout(v_layout)

    def cnf_cl(self):
        name = self.FIO.toPlainText().encode('cp866').decode('cp1251').strip()
        number = self.Phone.toPlainText().strip()
        line = self.Telegram.toPlainText().strip()
        if line:
            if line[0] == '@':
                line = line[1:]
                tg = line
                line = line.replace('_', '')
        if not (name and number and line):
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Заполните все поля!')
        elif not (number[0:2] == '+7' and len(number[2:]) == 10 and number[2:].isdigit()):
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Введите номер в формате: \n +7ХХХХХХХХХХ')
        elif not all([c in string.ascii_lowercase for c in line]):
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Telegram может содержать только \n латинские символы и символ _')
        elif len(name) > 255:
            Qt.QMessageBox.critical(self, 'Ошибка!', 'ФИО не может быть длиннее 255 знаков!')
        elif len(tg) > 255:
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Telegram не может быть длиннее 255 знаков!')
        else:
            number = number[2:]
            work_query = f'UPDATE clients SET fio = \'{name}\', phone = \'{number}\', telegram = \'{tg}\' ' \
                         f'WHERE id = {self.id_cl}'
            Var.cursor.execute(work_query)
            Var.connection.commit()
            self.accept()

    def cancel_cl(self):
        self.reject()

    def delete_cl(self):
        msg = QMessageBox()
        msg.setWindowTitle("Удаление")
        msg.setText("Удалить данного пользователя?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.setInformativeText("Также будут удалены все заявки этого пользователя")
        if msg.exec_() == QMessageBox.Yes:
            work_query = f'DELETE FROM apps WHERE client = \'{self.id_cl}\''
            Var.cursor.execute(work_query)
            Var.connection.commit()
            work_query = f'DELETE FROM clients WHERE id = \'{self.id_cl}\''
            Var.cursor.execute(work_query)
            Var.connection.commit()
            self.accept()
