from PyQt5.QtCore import Qt as Qtt
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem, \
    QMessageBox, QFileDialog, QHeaderView
from PyQt5 import Qt, QtWidgets, QtCore, QtGui
from PyQt5.Qt import QIcon, QSize, QTimer
from PyQt5.QtGui import QPixmap
import sys
import psycopg2
import string
import shutil
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path


def one_query(col, tab, row_id):
    work_query = f'SELECT {col} FROM {tab} WHERE id = %s'
    cursor.execute(work_query, (row_id,))
    connection.commit()
    records = cursor.fetchall()
    return records[0][0]


class MainWindow(Qt.QWidget):

    def __init__(self):
        super().__init__()

        # Прорисовка окна приложения
        self.setGeometry(0, 0, 1500, 600)
        self.setWindowTitle('Заявки')

        self.table = Qt.QTableWidget()
        self.label = Qt.QLabel('Пользовательские заявки')
        self.label.setStyleSheet("color:black; font: bold 20pt 'Arial';")
        self.label.setAlignment(Qtt.AlignCenter)

        self.checkbox_process = Qt.QCheckBox('Необработанные заявки')
        self.refresh_btn = Qt.QPushButton('Обновить')
        self.edit_bld_btn = Qt.QPushButton('Список зданий')
        self.edit_clnt_btn = Qt.QPushButton('Список клиентов')

        self.notif = Qt.QLabel('*перейти в редактирование можно двойным нажатием '
                               'ЛКМ по нужной ячейке или специальными кнопками ниже')
        self.notif.setStyleSheet("color:grey; font: 9pt 'Arial';")

        self.check_layout = Qt.QHBoxLayout()
        self.check_layout.addWidget(self.checkbox_process)
        self.check_layout.addWidget(self.refresh_btn)
        self.check_layout.setAlignment(Qtt.AlignRight)
        self.v_layout = Qt.QVBoxLayout(self)
        self.table_layout = Qt.QHBoxLayout()
        self.table_layout.addWidget(self.table)
        self.button_layout = Qt.QHBoxLayout()
        self.button_layout.addWidget(self.edit_bld_btn)
        self.button_layout.addWidget(self.edit_clnt_btn)
        self.v_layout.addWidget(self.label)
        self.v_layout.addLayout(self.check_layout)
        self.v_layout.addLayout(self.table_layout)
        self.v_layout.addWidget(self.notif)
        self.v_layout.addLayout(self.button_layout)

        # Первое заполнение таблицы
        self.state_cb()

        # Проверка изменения состояния чекбокса
        self.checkbox_process.stateChanged.connect(self.state_cb)

        # Сигнал двойного нажатия по элементу таблицы
        self.table.doubleClicked.connect(self.item_doubleclick)

        # Нажатие кнопки обновления таблицы
        self.refresh_btn.clicked.connect(self.state_cb)

        self.edit_bld_btn.clicked.connect(self.editor)

        self.edit_clnt_btn.clicked.connect(self.editor)

    def editor(self):
        sender = self.sender()
        print(sender.text())
        if sender.text() == 'Список зданий':
            self.edit = ListEditor(1)
        else:
            self.edit = ListEditor(0)

        if self.edit.exec_():
            self.state_cb()

    # Обработка изменения чекбокса
    def state_cb(self):
        self.table_filling()
        self.table.resizeRowsToContents()

    def item_doubleclick(self):
        cur_id = self.table.item(self.table.currentRow(), 0).text()
        if self.table.currentColumn() in [1, 5, 6, 7, 8, 9]:
            cl_id = one_query('client', 'apps', cur_id)
            ec = EditClient(cl_id)
            ec.exec_()
            self.state_cb()

        elif self.table.currentColumn() == 2:
            hs_id = one_query('house', 'apps', cur_id)
            eh = EditBuild(hs_id)
            eh.exec_()
            self.state_cb()

    def checkbox_edit(self):
        ch = self.sender()
        ix = self.table.indexAt(ch.pos())
        cur_id = self.table.item(ix.row(), 0).text()
        work_query = f'UPDATE apps SET ready = \'{ch.isChecked()}\' WHERE id = {cur_id}'
        cursor.execute(work_query)
        connection.commit()

    # Заполнение таблицы значениями из БД
    def table_filling(self):

        state = self.checkbox_process.checkState()
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(
            ["ID", "ФИО", "Адрес помещения", "Дата заявки", "Выполнение", "Телефон", "Telegram", "WhatsApp", "Viber",
             "Email"])

        if state:
            display_query = 'SELECT * FROM apps WHERE ready = False ORDER BY id'
        else:
            display_query = 'SELECT * FROM apps ORDER BY ready, id'

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

            item = QTableWidgetItem(str(row[0]))
            item.setTextAlignment(Qtt.AlignCenter)
            self.table.setItem(row_count, 0, item)

            item = QTableWidgetItem(bytes(client_name, 'cp1251').decode('cp866'))
            item.setTextAlignment(Qtt.AlignCenter)
            self.table.setItem(row_count, 1, item)

            item = QTableWidgetItem(bytes(house_address, 'cp1251').decode('cp866'))
            item.setTextAlignment(Qtt.AlignCenter)
            self.table.setItem(row_count, 2, item)

            item = QTableWidgetItem(str(row[3]))
            item.setTextAlignment(Qtt.AlignCenter)
            self.table.setItem(row_count, 3, item)

            chk_bx = Qt.QCheckBox()
            chk_bx.setStyleSheet("text-align: center; margin-left:50%; margin-right:50%;")
            chk_bx.setCheckState(Qtt.Checked) if row[4] is True else chk_bx.setCheckState(Qtt.Unchecked)
            chk_bx.clicked.connect(self.checkbox_edit)
            self.table.setCellWidget(row_count, 4, chk_bx)

            item = QTableWidgetItem('+7' + str(phone))
            item.setTextAlignment(Qtt.AlignCenter)
            self.table.setItem(row_count, 5, item)

            item = Qt.QLabel(f"<a href='https://t.me/{telegram}'>Перейти</a>", openExternalLinks=True)
            item.setAlignment(Qtt.AlignCenter)
            item.setMinimumHeight(15)
            self.table.setCellWidget(row_count, 6, item)

            item = Qt.QLabel(f"<a href='https://wa.me/7{phone}'>Перейти</a>", openExternalLinks=True)
            item.setAlignment(Qtt.AlignCenter)
            self.table.setCellWidget(row_count, 7, item)

            item = Qt.QLabel(f"<a href='viber://chat?number=%2B7{phone}'>Перейти</a>", openExternalLinks=True)
            item.setAlignment(Qtt.AlignCenter)
            self.table.setCellWidget(row_count, 8, item)

            item = QTableWidgetItem(str(mail))
            item.setTextAlignment(Qtt.AlignCenter)
            self.table.setItem(row_count, 9, item)

        #delegate = AlignDelegate(self.table)
        #self.tableWidget.setItemDelegateForColumn(4, delegate)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.table.horizontalHeader().setDefaultAlignment(Qtt.AlignCenter)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)


            # self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)


            # table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
            # table.horizontalHeader().setStretchLastSection(True)
        #self.table.setWordWrap(True)
            # table.horizontalHeader().setStretchLastSection(True)
            # table.horizontalHeader().setSectionResizeMode(
            #    QtWidgets.QHeaderView.Stretch)


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
        self.fio_cl = one_query('fio', 'clients', self.id_cl)
        self.FIO.setText(bytes(self.fio_cl, 'cp1251').decode('cp866'))

        self.Phone_label = Qt.QLabel('Номер телефона:')
        self.Phone_label.setStyleSheet("font: 10pt 'Tahoma'")
        self.Phone = Qt.QTextEdit()
        self.Phone.setFontPointSize(10)
        self.Phone.setPlaceholderText('Номер телефона в формате +7XXXXXXXXXX')
        self.phone_cl = one_query('phone', 'clients', self.id_cl)
        self.Phone.setText('+7' + self.phone_cl)

        self.Telegram_label = Qt.QLabel('Telegram:')
        self.Telegram_label.setStyleSheet("font: 10pt 'Tahoma'")
        self.Telegram = Qt.QTextEdit()
        self.Telegram.setFontPointSize(10)
        self.Telegram.setPlaceholderText('Пример: @user_name')
        self.tg_cl = one_query('telegram', 'clients', self.id_cl)
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
            cursor.execute(work_query)
            connection.commit()
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
            cursor.execute(work_query)
            connection.commit()
            work_query = f'DELETE FROM clients WHERE id = \'{self.id_cl}\''
            cursor.execute(work_query)
            connection.commit()
            self.accept()


class EditBuild(Qt.QDialog):

    def __init__(self, id_bd):
        super().__init__()

        # Прорисовка окна приложения
        self.setGeometry(0, 0, 600, 650)
        self.setFixedSize(600, 650)
        self.setWindowTitle('Редактирование помещения')
        self.setWindowFlags(Qtt.CustomizeWindowHint | Qtt.WindowCloseButtonHint)

        self.id_build = id_bd

        if self.id_build:
            self.ID_label = Qt.QLabel(f'ID: {self.id_build}')
        else:
            self.ID_label = Qt.QLabel(f'ID будет установлен автоматически')
        self.ID_label.setStyleSheet("font: 10pt 'Tahoma'")

        self.Address_label = Qt.QLabel('Адрес:')
        self.Address_label.setStyleSheet("font: 10pt 'Tahoma'")
        self.Address = Qt.QTextEdit()
        self.Address.setFontPointSize(10)
        self.Address.setFixedHeight(80)
        if self.id_build:
            self.adr = one_query('address', 'houses', id_bd)
            self.Address.setText(str(bytes(self.adr, 'cp1251').decode('cp866')))
        else:
            self.Address.setPlaceholderText('Пример: г. Москва, ул. Первомайская, д. 1')

        self.Square_label = Qt.QLabel('Площадь (м²):')
        self.Square_label.setStyleSheet("font: 10pt 'Tahoma'")
        self.Square = Qt.QTextEdit()
        self.Square.setFontPointSize(10)
        self.Square.setFixedHeight(50)
        if self.id_build:
            self.sq = one_query('square', 'houses', id_bd)
            self.Square.setText(str(self.sq))
        else:
            self.Square.setPlaceholderText('Пример: 66')

        self.Price_label = Qt.QLabel('Цена от (₽):')
        self.Price_label.setStyleSheet("font: 10pt 'Tahoma'")
        self.Price = Qt.QTextEdit()
        self.Price.setFontPointSize(10)
        self.Price.setFixedHeight(50)
        if self.id_build:
            self.pr = one_query('price', 'houses', id_bd)
            self.Price.setText(str(self.pr))
        else:
            self.Price.setPlaceholderText('Пример: 1000000')

        self.PicsTable = Qt.QTableWidget()
        self.PicsTable.setFixedHeight(160)
        print(self.Address.height())

        self.ConfirmButton = Qt.QPushButton('Подтвердить')
        self.SaveButton = Qt.QPushButton('Сохранить')
        self.CancelButton = Qt.QPushButton('Отмена')
        self.AddButton = Qt.QPushButton('Добавить фото')
        self.DelButton = Qt.QPushButton('Удалить')
        self.DelButton.setStyleSheet('background-color: #DB4139; border-radius: 6px; color: white; '
                                     'min-width: 10em; padding: 4px')

        self.ConfirmButton.clicked.connect(self.cnf_bld)
        self.SaveButton.clicked.connect(self.save_bld)
        self.CancelButton.clicked.connect(self.cancel_bld)
        self.AddButton.clicked.connect(self.image_bld)
        self.DelButton.clicked.connect(self.delete_bld)

        self.btn_layout = Qt.QHBoxLayout()
        self.btn_layout.addWidget(self.ConfirmButton)
        self.btn_layout.addWidget(self.SaveButton)
        self.btn_layout.addWidget(self.CancelButton)

        self.vh_layout = Qt.QVBoxLayout()
        self.vh_layout.addWidget(self.ID_label)
        self.vh_layout.addWidget(self.Address_label)
        self.vh_layout.addWidget(self.Address)
        self.vh_layout.addWidget(self.Square_label)
        self.vh_layout.addWidget(self.Square)
        self.vh_layout.addWidget(self.Price_label)
        self.vh_layout.addWidget(self.Price)
        self.vh_layout.addWidget(self.PicsTable)
        if not self.id_build:
            self.AddButton.setEnabled(False)
            self.notif = Qt.QLabel('*чтобы добавить фото сохраните здание')
            self.notif.setStyleSheet("color:red; font: 7pt 'Arial';")
            self.vh_layout.addWidget(self.notif)
        else:
            self.notif = Qt.QLabel('*чтобы открыть фото дважды нажмите ЛКМ на название, для удаления - на крестик')
            self.notif.setStyleSheet("color:grey; font: 7pt 'Arial';")
            self.vh_layout.addWidget(self.notif)
        self.vh_layout.addWidget(self.AddButton)
        self.vh_layout.addLayout(self.btn_layout)
        self.vh_layout.addWidget(self.DelButton)

        self.setLayout(self.vh_layout)

        if not os.path.exists(f'Images/{id_bd}') and self.id_build:
            os.mkdir(f'Images/{id_bd}')

        self.table_image()

    def cnf_bld(self):
        self.save_bld()
        self.accept()

    def save_bld(self):
        adr = self.Address.toPlainText().encode('cp866').decode('cp1251')
        sqr = self.Square.toPlainText()
        pr = self.Price.toPlainText()
        if not (adr and sqr and pr):
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Заполните все поля!')
        else:
            try:
                pr = int(pr)
                sqr = int(sqr)
            except ValueError:
                Qt.QMessageBox.critical(self, 'Ошибка!', 'Проверьте правильность ввода площади и цены!')
            else:
                if len(adr) > 255:
                    Qt.QMessageBox.critical(self, 'Ошибка!', 'Адрес не может быть длиннее 255 знаков!')
                elif sqr < 1:
                    Qt.QMessageBox.critical(self, 'Ошибка!', 'Площадь не может быть меньше 1!')
                elif sqr > 2147483647:
                    Qt.QMessageBox.critical(self, 'Ошибка!', 'Слишком больше значение площади!')
                elif pr < 1:
                    Qt.QMessageBox.critical(self, 'Ошибка!', 'Цена не может быть меньше 1!')
                elif pr > 9223372036854775807:
                    Qt.QMessageBox.critical(self, 'Ошибка!', 'Слишком больше значение цены!')
                elif self.id_build:
                    work_query = f'UPDATE houses SET address = \'{adr}\', square = \'{sqr}\', price = \'{pr}\' ' \
                                 f'WHERE id = {self.id_build}'
                    cursor.execute(work_query)
                    connection.commit()
                else:
                    work_query = f'INSERT INTO houses (address, square, price) ' \
                                 f'VALUES (\'{adr}\', \'{sqr}\', \'{pr}\')'
                    cursor.execute(work_query)
                    connection.commit()
                    work_query = f'SELECT id FROM houses WHERE address = %s AND square = %s AND price = %s'
                    cursor.execute(work_query, (adr, sqr, pr))
                    connection.commit()
                    records = cursor.fetchall()
                    self.id_build = records[0][0]
                    self.ID_label.setText(f'ID: {self.id_build}')
                    self.AddButton.setEnabled(True)
                    self.notif.setHidden(True)


    def cancel_bld(self):
        self.reject()

    def delete_bld(self):
        msg = QMessageBox()
        msg.setWindowTitle("Удаление")
        msg.setText("Удалить данное здание?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.setInformativeText("Также будут удалены все заявки с данным зданием")
        if msg.exec_() == QMessageBox.Yes:
            work_query = f'DELETE FROM apps WHERE house = \'{self.id_build}\''
            cursor.execute(work_query)
            connection.commit()
            work_query = f'DELETE FROM houses WHERE id = \'{self.id_build}\''
            cursor.execute(work_query)
            connection.commit()
            self.accept()

    def image_bld(self):

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("Images (*.png *.jpg)")
        dialog.setDirectory('C:/')
        dialog.setViewMode(QFileDialog.List)

        if dialog.exec_():
            file_names = dialog.selectedFiles()
            for file in file_names:
                shutil.copy(file, f'Images/{self.id_build}')

        self.table_image()

    def table_image(self):
        self.PicsTable.clear()
        self.PicsTable.setRowCount(0)
        self.PicsTable.setColumnCount(2)
        self.PicsTable.setHorizontalHeaderLabels(["Названия файлов", "Удаление"])
        if self.id_build:
            allimages = [f for f in listdir(f'Images/{self.id_build}') if isfile(join(f'Images/{self.id_build}', f))]
            count = 0
            for i in allimages:
                self.PicsTable.insertRow(count)
                self.PicsTable.setItem(count, 0, QTableWidgetItem(str(i)))
                self.del_item = QTableWidgetItem("❌")
                self.del_item.setTextAlignment(Qtt.AlignCenter)
                self.PicsTable.setItem(count, 1, self.del_item)
                count += 1

        self.PicsTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.PicsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.PicsTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.PicsTable.doubleClicked.connect(self.pic_double)

    def pic_double(self):
        if self.PicsTable.currentColumn() == 1:
            os.remove(join(f'Images/{self.id_build}', self.PicsTable.item(self.PicsTable.currentRow(), 0).text()))
            self.table_image()
        else:
            self.open_img = Picture(
                join(f'Images/{self.id_build}', self.PicsTable.item(self.PicsTable.currentRow(), 0).text()))
            self.open_img.exec_()


class Picture(Qt.QDialog):

    def __init__(self, img_path):
        super().__init__()

        self.label = Qt.QLabel(self)

        self.setWindowTitle('Просмотр изображения')
        self.setWindowFlags(Qtt.CustomizeWindowHint | Qtt.WindowCloseButtonHint)

        # loading image
        self.pixmap = QPixmap(img_path)
        self.pixmap2 = self.pixmap.scaledToHeight(512)

        # adding image to label
        self.label.setPixmap(self.pixmap2)

        # Optional, resize label to image size
        self.label.resize(self.pixmap2.width(),
                          self.pixmap2.height())

        self.setGeometry(610, 37, self.pixmap2.width(), self.pixmap2.height())


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
            self.query = 'SELECT * FROM houses ORDER BY id'
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

        cursor.execute(self.query)

        connection.commit()
        rec = cursor.fetchall()

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
            #item.setStyleSheet("text-align: center; margin-left:50%; margin-right:50%;")
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
            self.edit = EditBuild(self.cur_id)
        else:
            self.edit = EditClient(self.cur_id)
        self.edit.exec_()
        self.fil_table()

    def add(self):
        self.edit = EditBuild(0)

        self.edit.exec_()
        self.fil_table()

    def closeEvent(self, event):
        event.accept()
        MainWindow.state_cb(w)


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
    w = MainWindow()
    #w.show()
    w.showMaximized()
    QTimer.singleShot(1, w.table.resizeRowsToContents)
    try:
        sys.exit(app.exec_())
    finally:
        connection.close()
