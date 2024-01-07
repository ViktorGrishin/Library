from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5 import uic, QtWidgets


class UserWnd(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi("userWidget.ui", self)
        self.parentForm = args[0]
        self.open()

        self.takeBtn.setChecked(True)
        self.completeBtn.setEnabled(False)
        self.mode_wdgs = [self.authorLbl, self.authorsList, self.sectionLbl, self.sectionsList, self.clearFilterBtn]

        self.returnBtn.toggled.connect(self.change_mode)
        self.takeBtn.toggled.connect(self.change_mode)
        self.exitBtn.clicked.connect(self.exit)
        self.updateBtn.clicked.connect(self.update_table)
        self.authorsList.itemClicked.connect(self.disable_complete)
        self.sectionsList.itemClicked.connect(self.disable_complete)
        self.usersList.itemClicked.connect(self.disable_complete)
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.tableWidget.clicked.connect(self.choose)
        self.completeBtn.clicked.connect(self.complete)
        self.clearFilterBtn.clicked.connect(self.clear_filter)

        self.update_table()


    def clear_filter(self):
        self.show()
        # Очищаем QlistWidgets
        self.sectionsList.clear()
        self.authorsList.clear()
        # Заполняем QList'ы

        # Список жанров
        sections = self.parentForm.db.give_sections()
        self.sectionsList.addItems(*zip(*sections))
        # Список авторов
        authors = self.parentForm.db.give_authors()
        self.authorsList.addItems(*zip(*authors))

        # Так как пользователь ещё ничего не выбрал, выключаем кнопку действия
        self.completeBtn.setEnabled(False)

    def complete(self):
        if self.takeBtn.isChecked():
            # Взятие книги
            # Проверяем, что пользователь выбрал книгу
            if not self.tableWidget.currentRow() is None:
                # Проверка выбора пользователя
                if self.usersList.selectedItems():
                    name = self.usersList.currentItem().text()
                    id_reader = self.parentForm.db.give_reader_id(name)
                else:
                    self.statusbar.showMessage("Ошибка! Выберете пользователя")
                    return
                # Берём книгу
                title = self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
                ok, id_book = self.parentForm.db.take_book(title=title, id_reader=id_reader)
                if ok:
                    self.statusbar.showMessage(f"Вы успешно взяли книгу с номером {id_book}!")
                else:
                    self.statusbar.showMessage("Ошибка!")

            else:
                self.completeBtn.setEnabled(False)
                self.statusbar.showMessage("Ошибка! Выберете ячейку с книгой")
        else:
            # Возврат книги
            # Книга для возврата выбрана
            if not self.tableWidget.currentRow() is None:
                # Возвращаем книгу в библиотеку
                id_book = self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
                reader_name = self.usersList.currentItem().text()
                ok, debt = self.parentForm.db.return_book(id_book=id_book, reader_name=reader_name)
                if ok:
                    if debt:
                        self.statusbar.showMessage(f'Оплатите задолженность. Книга с номером {id_book} возвращена')
                    else:
                        self.statusbar.showMessage(f'Книга с номером {id_book} успешно возвращена')
                else:
                    self.statusbar.showMessage("Ошибка!")

            else:
                self.completeBtn.setEnabled(False)
                self.statusbar.showMessage("Ошибка! Выберете ячейку с книгой")

        self.update_table()

    def choose(self):
        if not self.tableWidget.currentRow() is None:
            self.completeBtn.setEnabled(True)
        else:
            self.completeBtn.setEnabled(False)

    def disable_complete(self):
        self.completeBtn.setEnabled(False)

    def change_mode(self):
        if self.returnBtn.isChecked() and not self.authorLbl.isHidden():
            for elem in self.mode_wdgs:
                elem.setVisible(False)

            self.completeBtn.setEnabled(False)
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

        # Так как пользователь ещё ничего не выбрал, выключаем кнопку действия
        self.completeBtn.setEnabled(False)

    def update_table(self):
        # Очищаем таблицу
        self.tableWidget.setRowCount(0)
        # Выводим таблицу
        if self.takeBtn.isChecked():
            # Настраиваем фильтры для поиска
            author = self.authorsList.currentItem()
            section = self.sectionsList.currentItem()
            author = author.text() if author else None
            section = section.text() if section else None
            # Отправляем запрос
            data = self.parentForm.db.filter_books(author=author, section=section)
            # Заполняем таблицу
            title = ['Название', 'Обложка']
            self.tableWidget.setColumnCount(len(title))
            self.tableWidget.setHorizontalHeaderLabels(title)
            for i, row in enumerate(data):
                self.tableWidget.setRowCount(
                    self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(elem))
            self.tableWidget.resizeColumnsToContents()
        else:
            # Очищаем таблицу
            self.tableWidget.setRowCount(0)
            # Получаем данные
            if not self.usersList.currentItem():
                self.statusbar.showMessage("Ошибка! Выберете пользователя")
                return
            name_reader = self.usersList.currentItem().text()
            data = self.parentForm.db.give_readers_books(reader_name=name_reader)
            # Заполняем таблицу
            title = ['Номер книги', 'Название', 'Обложка']
            self.tableWidget.setColumnCount(len(title))
            self.tableWidget.setHorizontalHeaderLabels(title)
            for i, row in enumerate(data):
                self.tableWidget.setRowCount(
                    self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(str(elem)))
            self.tableWidget.resizeColumnsToContents()
        self.completeBtn.setEnabled(False)

    def exit(self):
        self.hide()
        self.parentForm.show()
