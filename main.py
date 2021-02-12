import os
import sys
import random
import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.lon = 86.088374
        self.lat = 55.354727
        self.zoom = 10
        self.map_file = 'map.png'
        self.update_image()

    def update_image(self):
        self.get_image()
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def get_image(self):
        search_api_server = "https://static-maps.yandex.ru/1.x/"
        search_params = {
            "ll": ','.join([str(self.lon), str(self.lat)]),
            "size": '450,450',
            "z": str(self.zoom),
            "l": 'map'
        }
        response = requests.get(search_api_server, params=search_params)

        if not response:
            print("Ошибка выполнения запроса")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            return

        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def closeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
