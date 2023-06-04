from PyQt5.QtCore import Qt as Qtt
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView
from PyQt5 import Qt, QtWidgets
from PyQt5.QtGui import QIcon
import shutil
import os

import Var
import Picture_window


class EditBuild(Qt.QDialog):

    def __init__(self, id_bd):
        super().__init__()

        # Прорисовка окна приложения
        self.setGeometry(0, 0, 600, 610)
        self.setFixedSize(600, 610)
        self.setWindowTitle('Редактирование помещения')
        self.setWindowIcon(QIcon("Icon.png"))
        self.setWindowFlags(Qtt.CustomizeWindowHint | Qtt.WindowCloseButtonHint)

        self.id_build = id_bd

        if self.id_build != -1:
            self.ID_label = Qt.QLabel(f'ID: {self.id_build}')
        else:
            self.ID_label = Qt.QLabel(f'ID будет установлен автоматически')
        self.ID_label.setFont(Var.font)

        self.Address_label = Qt.QLabel('Город:')
        self.Address_label.setFont(Var.font)
        self.Address = Qt.QTextEdit()
        self.Address.setFont(Var.font)
        self.Address.setFixedHeight(37)
        if self.id_build != -1:
            self.adr = Var.one_query('address', 'buildings', id_bd)
            self.Address.setText(self.adr)
        self.Address.setPlaceholderText('Пример: Москва')

        self.Square_label = Qt.QLabel('Площадь (м²):')
        self.Square_label.setFont(Var.font)
        self.Square = Qt.QTextEdit()
        self.Square.setFont(Var.font)
        self.Square.setFixedHeight(37)
        if self.id_build != -1:
            self.sq = Var.one_query('square', 'buildings', id_bd)
            self.Square.setText(str(self.sq))
        self.Square.setPlaceholderText('Пример: 66')

        self.Price_label = Qt.QLabel('Цена от (млн. ₽):')
        self.Price_label.setFont(Var.font)
        self.Price = Qt.QTextEdit()
        self.Price.setFont(Var.font)
        self.Price.setFixedHeight(37)
        if self.id_build != -1:
            self.pr = Var.one_query('price', 'buildings', id_bd)
            self.Price.setText(str(self.pr))
        self.Price.setPlaceholderText('Пример: 11.5')

        self.Descript_label = Qt.QLabel('Описание:')
        self.Descript_label.setFont(Var.font)
        self.Descript = Qt.QTextEdit()
        self.Descript.setFont(Var.font)
        self.Descript.setFixedHeight(80)
        if self.id_build != -1:
            self.dsc = Var.one_query('descript', 'buildings', id_bd)
            print(self.dsc)
            if self.dsc is not None:
                self.Descript.setText(str(self.dsc))
        self.Descript.setPlaceholderText('Пример: Кирпичный дом с живописным видом из окна')

        self.PicsTable = Qt.QTableWidget()
        self.PicsTable.setFixedHeight(100)

        self.ConfirmButton = Qt.QPushButton('Подтвердить')
        self.ConfirmButton.setFont(Var.font)
        self.SaveButton = Qt.QPushButton('Сохранить')
        self.SaveButton.setFont(Var.font)
        self.CancelButton = Qt.QPushButton('Отмена')
        self.CancelButton.setFont(Var.font)
        self.AddButton = Qt.QPushButton('Добавить фото')
        self.AddButton.setFont(Var.font)
        self.DelButton = Qt.QPushButton('Удалить')
        self.DelButton.setFont(Var.font)
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
        self.vh_layout.addWidget(self.Descript_label)
        self.vh_layout.addWidget(self.Descript)
        self.vh_layout.addWidget(self.PicsTable)
        if not self.id_build != -1:
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

        if not os.path.exists(f'Images/{id_bd}') and self.id_build != -1:
            os.mkdir(f'Images/{id_bd}')

        self.table_image()

    def cnf_bld(self):
        self.save_bld()
        self.accept()

    def save_bld(self):
        adr = self.Address.toPlainText()
        sqr = self.Square.toPlainText()
        pr = self.Price.toPlainText()
        dscr = self.Descript.toPlainText()
        if not (adr and sqr and pr and dscr):
            Qt.QMessageBox.critical(self, 'Ошибка!', 'Заполните все поля!')
        else:
            try:
                pr = float(pr)
            except ValueError:
                Qt.QMessageBox.critical(self, 'Ошибка!', 'Проверьте правильность ввода цены!')
            else:
                if len(adr) > 255:
                    Qt.QMessageBox.critical(self, 'Ошибка!', 'Город не может быть длиннее 255 знаков!')
                elif pr <= 0:
                    Qt.QMessageBox.critical(self, 'Ошибка!', 'Цена не может быть меньше или равна 0!')
                elif pr > 100000:
                    Qt.QMessageBox.critical(self, 'Ошибка!', 'Слишком больше значение цены!')
                elif self.id_build != -1:
                    work_query = f'UPDATE buildings SET address = \'{adr}\', square = \'{sqr}\', price = \'{pr}\', ' \
                                 f'descript = \'{dscr}\' WHERE id = {self.id_build}'
                    Var.cursor.execute(work_query)
                    Var.connection.commit()
                else:
                    work_query = f'INSERT INTO buildings (address, square, price, descript) ' \
                                 f'VALUES (\'{adr}\', \'{sqr}\', \'{pr}\', \'{dscr}\')'
                    Var.cursor.execute(work_query)
                    Var.connection.commit()
                    work_query = f'SELECT id FROM buildings WHERE address = %s AND square = %s AND price = %s'
                    Var.cursor.execute(work_query, (adr, sqr, pr))
                    Var.connection.commit()
                    records = Var.cursor.fetchall()
                    self.id_build = records[0][0]
                    self.ID_label.setText(f'ID: {self.id_build}')
                    self.AddButton.setEnabled(True)
                    self.notif.setHidden(True)
                    if not os.path.exists(f'Images/{self.id_build}') and self.id_build != -1:
                        os.mkdir(f'Images/{self.id_build}')

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
            work_query = f'DELETE FROM apps WHERE building = \'{self.id_build}\''
            Var.cursor.execute(work_query)
            Var.connection.commit()
            work_query = f'DELETE FROM buildings WHERE id = \'{self.id_build}\''
            Var.cursor.execute(work_query)
            Var.connection.commit()
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
        if self.id_build != -1:
            allimages = [f for f in os.listdir(f'Images/{self.id_build}') if os.path.isfile(os.path.join(f'Images/{self.id_build}', f))]
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
            os.remove(os.path.join(f'Images/{self.id_build}', self.PicsTable.item(self.PicsTable.currentRow(), 0).text()))
            self.table_image()
        else:
            self.open_img = Picture_window.Picture(
                os.path.join(f'Images/{self.id_build}', self.PicsTable.item(self.PicsTable.currentRow(), 0).text()))
            self.open_img.exec_()
