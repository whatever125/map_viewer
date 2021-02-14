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
geocode_api_server = 'https://geocode-maps.yandex.ru/1.x/'
geocode_api_key = '40d1649f-0493-4b70-98ba-98533de7710b'
static_api_server = "https://static-maps.yandex.ru/1.x/"


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.comboBox.currentIndexChanged.connect(self.change_type)
        self.pushButton.clicked.connect(self.find_toponym)
        self.pushButton_2.clicked.connect(self.delete_toponym)
        self.checkBox.clicked.connect(self.show_index)
        self.lon = 86.088374
        self.lat = 55.354727
        self.zoom = 10
        self.map_file = 'map.png'
        self.map_type = 'map'
        self.index = False
        self.found_index = False
        self.clicked = False
        self.points = []
        self.update_image()

    def find_toponym(self):
        text = self.lineEdit.text()
        if not text:
            self.label_2.setText('Пустая строка')
            return
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
            self.points = [*coordinates, 'comma']
            index = ''
            if self.index:
                index = self.find_index(list(map(lambda x: str(x), coordinates)))
            if index:
                self.lineEdit_2.setText(address + ', ' + index)
            else:
                self.lineEdit_2.setText(address)
            self.update_image()
        except Exception:
            self.label_2.setText('Ничего не нашлось')

    def find_toponym_on_click(self, lon, lat):
        search_params = {
            "apikey": search_api_key,
            "text": ','.join([lat, lon]),
            "lang": "ru_RU"
        }
        response = requests.get(search_api_server, params=search_params)

        if not response:
            self.label_2.setText(response.status_code, ' ', response.reason)
            return
        try:
            response = response.json()
            print(response)
            obj = response['features'][0]
            description = obj['properties']['GeocoderMetaData']['text']
            self.points = [lon, lat, 'comma']
            index = ''
            if self.index:
                index = self.find_index(list(map(lambda x: str(x), [lon, lat])))
            if index:
                self.lineEdit_2.setText(description + ', ' + index)
            else:
                self.lineEdit_2.setText(description)
            self.update_image()
        except Exception:
            self.label_2.setText('Ничего не нашлось')

    def delete_toponym(self):
        self.points = []
        self.lineEdit.setText('')
        self.lineEdit_2.setText('')
        self.update_image()
        self.clicked = False

    def change_type(self):
        self.map_type = MAP_TYPES[self.comboBox.currentText()]
        self.update_image()

    def show_index(self):
        self.index = bool(1 - self.index)
        if self.index:
            if self.clicked:
                index = self.find_index(self.points[:-1])
            else:
                index = self.find_index([str(self.lon), str(self.lat)])
            if index:
                self.lineEdit_2.setText(self.lineEdit_2.text() + ', ' + index)
        else:
            self.label_2.setText('')
            if self.found_index:
                self.lineEdit_2.setText(','.join(self.lineEdit_2.text().split(',')[:-1]))
            else:
                pass

    def find_index(self, coordinates):
        index_search_params = {
            "apikey": geocode_api_key,
            "geocode": ','.join(coordinates),
            "format": "json"
        }
        index_response = requests.get(geocode_api_server, params=index_search_params)

        if not index_response:
            self.label_2.setText(index_response.status_code, ' ', index_response.reason)
            return
        try:
            index_response = index_response.json()
            toponym = index_response["response"]["GeoObjectCollection"]["featureMember"][0][
                "GeoObject"]
            index = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
            self.label_2.setText('')
            self.found_index = True
            return index
        except Exception:
            self.label_2.setText('Почтовый индекс не найден')
            self.found_index = False
            return ''

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
                self.lat += 178.25792 / (2 ** (self.zoom - 1))
            elif event.key() == Qt.Key_Down:
                self.lat -= 178.25792 / (2 ** (self.zoom - 1))
            if self.lat > 85:
                self.lat = 85
            elif self.lat < -85:
                self.lat = -85
        if event.key() in [Qt.Key_Left, Qt.Key_Right]:
            if event.key() == Qt.Key_Left:
                self.lon -= ((422.4 / (2 ** (self.zoom - 1))) / 600) * 450
            elif event.key() == Qt.Key_Right:
                self.lon += ((422.4 / (2 ** (self.zoom - 1))) / 600) * 450
            if self.lon > 180:
                self.lon = 180
            elif self.lon < -180:
                self.lon = -180
        self.update_image()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x, y = event.x() - 200, event.y()
            if 0 <= x <= 450 and 0 <= y <= 450:
                x_k = (422.4 / (2 ** (self.zoom - 1))) / 600
                y_k = (178.25792 / (2 ** (self.zoom - 1))) / 450
                x, y = x - 225, 225 - y
                lon, lat = round(self.lon + x * x_k, 6), round(self.lat + y * y_k, 6)
                self.clicked = True
                self.find_toponym_on_click(str(lon), str(lat))

    def closeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
