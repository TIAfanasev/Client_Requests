from PyQt5.QtCore import Qt as Qtt
from PyQt5 import Qt
from PyQt5.QtGui import QPixmap


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