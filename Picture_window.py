from PyQt5.QtCore import Qt as Qtt
from PyQt5 import Qt
from PyQt5.QtGui import QPixmap, QIcon


class Picture(Qt.QDialog):

    def __init__(self, img_path):
        super().__init__()

        self.label = Qt.QLabel(self)

        self.setWindowTitle('Просмотр изображения')
        self.setWindowIcon(QIcon("Icon.png"))
        self.setWindowFlags(Qtt.CustomizeWindowHint | Qtt.WindowCloseButtonHint)

        self.pixmap = QPixmap(img_path)
        self.pixmap2 = self.pixmap.scaledToHeight(512)

        self.label.setPixmap(self.pixmap2)

        self.label.resize(self.pixmap2.width(),
                          self.pixmap2.height())

        self.setGeometry(610, 37, self.pixmap2.width(), self.pixmap2.height())
