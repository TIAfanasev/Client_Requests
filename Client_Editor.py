from PyQt5.QtCore import Qt as Qtt
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import Qt
from PyQt5.QtGui import QIcon
import string
import re

import Var


class EditClient(Qt.QDialog):

    def __init__(self, id_cl):
        super().__init__()

        # Прорисовка окна приложения
        self.setGeometry(0, 0, 600, 400)
        self.setWindowTitle('Редактирование данных клиента')
        self.setWindowIcon(QIcon("Icon.png"))
        self.setFixedSize(600, 400)
        self.setWindowFlags(Qtt.CustomizeWindowHint | Qtt.WindowCloseButtonHint)

        self.id_cl = id_cl

        if self.id_cl != -1:
            self.ID_label = Qt.QLabel(f'ID: {self.id_cl}')
        else:
            self.ID_label = Qt.QLabel(f'ID будет установлен автоматически')
        self.ID_label.setFont(Var.font)

        self.FIO_label = Qt.QLabel('ФИО:')
        self.FIO_label.setFont(Var.font)
        self.FIO = Qt.QTextEdit()
        self.FIO.setFont(Var.font)
        self.FIO.setPlaceholderText('Пример: Иванов Иван Иванович')
        if self.id_cl != -1:
            self.fio_cl = Var.one_query('fio', 'clients', self.id_cl)
            self.FIO.setText(bytes(self.fio_cl, 'cp1251').decode('cp866'))

        self.Phone_label = Qt.QLabel('Номер телефона:')
        self.Phone_label.setFont(Var.font)
        self.Phone = Qt.QLineEdit()
        self.Phone.setFont(Var.font)
        self.Phone.setInputMask('+7(999)999-99-99;_')
        if self.id_cl != -1:
            self.phone_cl = Var.one_query('phone', 'clients', self.id_cl)
            self.Phone.setText('+7' + self.phone_cl)

        self.Telegram_label = Qt.QLabel('Telegram:')
        self.Telegram_label.setFont(Var.font)
        self.Telegram = Qt.QTextEdit()
        self.Telegram.setFont(Var.font)
        self.Telegram.setPlaceholderText('Пример: @user_name')
        if self.id_cl != -1:
            self.tg_cl = Var.one_query('telegram', 'clients', self.id_cl)
            if self.tg_cl:
                self.Telegram.setText('@' + self.tg_cl)

        self.email_label = Qt.QLabel('Email:')
        self.email_label.setFont(Var.font)
        self.email = Qt.QTextEdit()
        self.email.setFont(Var.font)
        self.email.setPlaceholderText('Пример: example@gmail.com')
        if self.id_cl != -1:
            self.email_cl = Var.one_query('email', 'clients', self.id_cl)
            self.email.setText(self.email_cl)

        self.confirm = Qt.QPushButton('Подтвердить')
        self.confirm.setFont(Var.font)
        self.cancel = Qt.QPushButton('Отмена')
        self.cancel.setFont(Var.font)
        self.delete = Qt.QPushButton('Удалить')
        self.delete.setFont(Var.font)
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
        v_layout.addWidget(self.email_label)
        v_layout.addWidget(self.email)
        btn_layout = Qt.QHBoxLayout()
        btn_layout.addWidget(self.confirm)
        btn_layout.addWidget(self.cancel)
        v_layout.addLayout(btn_layout)
        v_layout.addWidget(self.delete)
        self.setLayout(v_layout)

    def cnf_cl(self):
        name = self.FIO.toPlainText().encode('cp866').decode('cp1251').strip()
        number = self.Phone.text()[2:]
        number = int(''.join(filter(str.isdigit, number)))
        line = self.Telegram.toPlainText().strip()
        mail = self.email.toPlainText().strip()
        pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")

        phone_unique = Var.simple_query('phone', 'clients', number, self.id_cl)
        mail_uniques = Var.simple_query('email', 'clients', mail, self.id_cl)

        if not (name and number and mail):
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Заполните все поля!')
        elif number < 1000000000:
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Проверьте правильность ввода номера!')
        elif not pattern.match(mail):
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Проверьте правильность ввода почты!')
        elif not phone_unique:
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Номер телефона уже используется!')
        elif not mail_uniques:
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Почта уже используется!')
        elif len(name) > 255:
            Qt.QMessageBox.critical(self, 'Ошибка!', 'ФИО не может быть длиннее 255 знаков!')
        elif line:
            if line[0] == '@':
                line = line[1:]
            tg = line
            line = line.replace('_', '')
            tg_unique = Var.simple_query('telegram', 'clients', tg, self.id_cl)
            if not re.match(r'^[a-zA-Z0-9]+$', line):
                Qt.QMessageBox.critical(self, 'Ошибка!', 'Telegram может содержать только \n латинские символы, '
                                                         'цифры и символ _')
            elif len(tg) > 32 or len(tg) < 5:
                Qt.QMessageBox.critical(self, 'Ошибка!', 'Telegram не может быть длиннее 32 и короче 5 знаков !')
            elif not tg_unique:
                Qt.QMessageBox.critical(self, 'Ошибка!', 'Ник Telegram уже используется!')
            else:
                if self.id_cl != -1:
                    work_query = f'UPDATE clients SET fio = \'{name}\', phone = \'{number}\', telegram = \'{tg}\', ' \
                                    f'email = \'{mail}\' WHERE id = {self.id_cl}'
                else:
                    work_query = f"INSERT INTO clients (fio, phone, telegram, email, password)" \
                                 f" VALUES ('{name}', '{number}', '{tg}', '{mail}', 'default_password')"
                Var.cursor.execute(work_query)
                Var.connection.commit()
                self.accept()
        else:
            if self.id_cl != -1:
                work_query = f'UPDATE clients SET fio = \'{name}\', phone = \'{number}\', telegram = \'{line}\', ' \
                             f'email = \'{mail}\' WHERE id = {self.id_cl}'
            else:
                work_query = f"INSERT INTO clients (fio, phone, email, password) " \
                             f"VALUES (\'{name}\', \'{number}\', \'{mail}\', \'{'default_password'}\')"
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
