import os
import sys
import random
import requests
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget


MAP_TYPES = {'Схема': 'map', 'Спутник': 'sat', 'Гибрид': 'sat,skl'}
search_api_server = "https://search-maps.yandex.ru/v1/"
search_api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
static_api_server = "https://static-maps.yandex.ru/1.x/"


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.comboBox.currentIndexChanged.connect(self.change_type)
        self.pushButton.clicked.connect(self.find_toponym)
        self.pushButton_2.clicked.connect(self.delete_toponym)
        self.lon = 86.088374
        self.lat = 55.354727
        self.zoom = 10
        self.map_file = 'map.png'
        self.map_type = 'map'
        self.points = []
        self.update_image()

    def find_toponym(self):
        text = self.lineEdit.text()
        search_params = {
            "apikey": search_api_key,
            "text": text,
            "lang": "ru_RU"
        }
        response = requests.get(search_api_server, params=search_params)

        if not response:
            self.label_2.setText(response.status_code, ' ', response.reason)
            return
        try:
            response = response.json()
            obj = response['features'][0]
            coordinates = obj['geometry']['coordinates']
            address = obj['properties']['description']
            self.lon, self.lat = coordinates
            self.points = [*coordinates, 'round']
            self.lineEdit_2.setText(address)
            self.update_image()
        except Exception:
            self.label_2.setText('Ничего не нашлось')

    def delete_toponym(self):
        self.points = []
        self.lineEdit_2.setText('')
        self.update_image()

    def change_type(self):
        self.map_type = MAP_TYPES[self.comboBox.currentText()]
        self.update_image()

    def update_image(self):
        self.get_image()
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def get_image(self):
        search_params = {
            "ll": ','.join([str(self.lon), str(self.lat)]),
            "size": '450,450',
            "z": str(self.zoom),
            "l": self.map_type,
            "pt": self.make_points() if self.points else ''
        }
        response = requests.get(static_api_server, params=search_params)

        if not response:
            self.label_2.setText(response.status_code, ' ', response.reason)
            return

        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def make_points(self):
        string = ''
        for i in range(len(self.points)):
            string += str(self.points[i])
            if (i + 1) % 3 == 0:
                string += '~'
            else:
                string += ','
        return string[:-1]

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_PageUp, Qt.Key_PageDown]:
            if event.key() == Qt.Key_PageUp:
                self.zoom += 1
            elif event.key() == Qt.Key_PageDown:
                self.zoom -= 1
            if self.zoom > 17:
                self.zoom = 17
            if self.zoom < 0:
                self.zoom = 0
        if event.key() in [Qt.Key_Up, Qt.Key_Down]:
            if event.key() == Qt.Key_Up:
                self.lat += 175 / 2 ** self.zoom
            elif event.key() == Qt.Key_Down:
                self.lat -= 175 / 2 ** self.zoom
            if self.lat > 85:
                self.lat = 85
            elif self.lat < -85:
                self.lat = -85
        if event.key() in [Qt.Key_Left, Qt.Key_Right]:
            if event.key() == Qt.Key_Left:
                self.lon -= 300 / 2 ** self.zoom
            elif event.key() == Qt.Key_Right:
                self.lon += 300 / 2 ** self.zoom
            if self.lon > 180:
                self.lon = 180
            elif self.lon < -180:
                self.lon = -180
        self.update_image()
        event.accept()

    def closeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
