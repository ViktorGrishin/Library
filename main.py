import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
from UserWnd import UserWnd
from database import DataBase


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Загружаем интерфейс
        uic.loadUi('startWidget.ui', self)
        # Подключаем базу данных
        self.db = DataBase()
        # Прикрепляем функции к кнопкам
        self.enterBtn.clicked.connect(self.open_user_wnd)
        self.createBtn.clicked.connect(self.create_user)


    # Функции перехода в др окна
    def open_user_wnd(self):
        self.user_wnd = UserWnd(self)
        self.statusbar.showMessage("")
        self.hide()
        self.user_wnd.open()

    def create_user(self):
        # Создаём диалоговое окно, чтобы получить имя пользователя
        name, ok_pressed = QInputDialog.getText(self, "Введите имя",
                                                "Как вас зовут?")
        if ok_pressed:
            ok, id_user = self.db.create_reader(name)
            if not ok:
                self.statusbar.showMessage("Пользователь уже существует")
            else:
                self.statusbar.showMessage(f'Пользователь "{name}" успешно создан. Вы у нас {id_user} по счёту')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
