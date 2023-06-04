from PyQt5.QtCore import Qt as Qtt
from PyQt5 import Qt
from PyQt5.QtGui import QIcon
import datetime

import Var


class NewReq(Qt.QDialog):

    def __init__(self):
        super().__init__()

        # Прорисовка окна приложения
        self.setGeometry(600, 400, 600, 200)
        self.setWindowTitle('Создать заявку')
        self.setWindowIcon(QIcon("Icon.png"))
        self.setFixedSize(600, 200)
        self.setWindowFlags(Qtt.CustomizeWindowHint | Qtt.WindowCloseButtonHint)

        self.label = Qt.QLabel('Добавление клиентской заявки')
        self.label.setStyleSheet("color:black; font: bold 18pt 'MS Shell Dlg 2'")
        self.label.setAlignment(Qtt.AlignCenter)

        work_query = f'SELECT fio FROM clients'
        Var.cursor.execute(work_query)
        Var.connection.commit()
        records = Var.cursor.fetchall()
        translate_names = []
        for rec in records:
            translate_names.append(rec[0])

        self.select_user = Qt.QComboBox(self)
        self.select_user.addItems(translate_names)
        self.select_user.setFont(Var.font)
        self.select_user.setCurrentText('Роль не выбрана')

        work_query = f'SELECT descript FROM buildings'
        Var.cursor.execute(work_query)
        Var.connection.commit()
        records = Var.cursor.fetchall()
        translate_address = []
        for rec in records:
            translate_address.append(rec[0])

        self.select_bld = Qt.QComboBox(self)
        self.select_bld.addItems(translate_address)
        self.select_bld.setFont(Var.font)
        self.select_bld.setCurrentText('Роль не выбрана')

        self.add_btn = Qt.QPushButton("Выполнить")
        self.cancel_btn = Qt.QPushButton("Отмена")

        self.btn_layout = Qt.QHBoxLayout()
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.cancel_btn)

        self.v_layout = Qt.QVBoxLayout(self)
        self.v_layout.addWidget(self.select_user)
        self.v_layout.addWidget(self.select_bld)
        self.v_layout.addLayout(self.btn_layout)

        self.add_btn.clicked.connect(self.add_req)
        self.cancel_btn.clicked.connect(self.cancel)

    def add_req(self):

        work_query = f'SELECT id FROM clients WHERE fio = %s'
        Var.cursor.execute(work_query, (self.select_user.currentText(),))
        Var.connection.commit()
        records = Var.cursor.fetchall()
        user_id = records[0][0]

        work_query = f'SELECT id FROM buildings WHERE descript = %s'
        Var.cursor.execute(work_query, (self.select_bld.currentText(),))
        Var.connection.commit()
        records = Var.cursor.fetchall()
        bld_id = records[0][0]

        dt = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")

        work_query = f'INSERT INTO apps (client, building, date, ready) ' \
                     f'VALUES (\'{user_id}\', \'{bld_id}\', \'{dt}\', \'{False}\')'
        Var.cursor.execute(work_query)
        Var.connection.commit()
        work_query = f'UPDATE buildings SET buildings_used = buildings.buildings_used || {user_id} WHERE id = {bld_id}'
        Var.cursor.execute(work_query)
        Var.connection.commit()
        self.accept()

    def cancel(self):
        self.reject()






