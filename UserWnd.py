import sys

from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic


class UserWnd(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi("userWidget.ui", self)
        self.parentForm = args[0]
        self.open()
        self.user = None
        self.author = None
        self.section = None
        self.takeBtn.setChecked(True)
        self.mode_wdgs = [self.authorLbl, self.authorsList, self.sectionLbl, self.sectionsList]
        self.returnBtn.toggled.connect(self.change_mode)
        self.takeBtn.toggled.connect(self.change_mode)
        self.exitBtn.clicked.connect(self.exit)


    def change_mode(self):
        if self.returnBtn.isChecked() and not self.authorLbl.isHidden():
            for elem in self.mode_wdgs:
                elem.setVisible(False)

            if not self.usersList.selectedItems():
                self.completeBtn.setEnabled(False)
            self.update_table()
        elif self.takeBtn.isChecked() and self.authorLbl.isHidden():
            for elem in self.mode_wdgs:
                elem.setVisible(True)
            self.completeBtn.setEnabled(False)
            self.update_table()

    def open(self):
        self.show()
        # Очищаем QlistWidgets
        self.usersList.clear()
        self.sectionsList.clear()
        self.authorsList.clear()
        # Заполняем QList'ы

        # Список пользователей
        users = self.parentForm.db.give_readers()
        self.usersList.addItems(*zip(*users))
        # Список жанров
        sections = self.parentForm.db.give_sections()
        self.sectionsList.addItems(*zip(*sections))
        # Список авторов
        authors = self.parentForm.db.give_authors()
        self.authorsList.addItems(*zip(*authors))

    def update_table(self):
        # Очищаем таблицу
        self.tableWidget.setTowCount(0)
        # Выводим таблицу
        if self.takeBtn.isChecked():
            # data = self.parentForm.db.filter_
            pass
        else:
            pass

    def exit(self):
        self.hide()
        self.parentForm.show()
