import sqlite3
import datetime


class DataBase:
    def __init__(self, path='database.sqlite'):
        self.con = sqlite3.connect(path)

    def take_book(self, id_title, id_reader, days=14):
        cur = self.con.cursor()
        status = True
        id_book = cur.execute("""SELECT id_book
                                FROM books 
                                WHERE title = ? and place = 0""", (id_title,)).fetchone()
        if id_book:  # Есть свободные книги
            # Меняем статус книги
            id_book = id_book[-1]
            today = datetime.date.today()
            return_day = today + datetime.timedelta(days=days)
            cur.execute("""UPDATE books
                            SET place = ?
                            SET data_taken = ?
                            SET data_return = ?
                            WHERE id_book = ?""", (id_reader, str(today), str(return_day), id_book))

            # меняем количество книг в доступе
            # Количество книг в наличии
            count = int(cur.execute("""SELECT stock
                                        FROM books_title
                                        WHERE id_title = ?""", (id_title,)).fetchone()[-1])

            cur.execute("""UPDATE books_title
                            SET stock = ?
                            WHERE id_title = ?""", (count - 1, id_title))

            # Добаляем книгу в список к пользователю
            books = cur.execute("""SELECT books
                                    FROM readers
                                    WHERE id_reader = ?""", (id_reader,)).fetchone()[-1]
            books += str(id_book[-1]) + ' '
            cur.execute("""UPDATE readers
                            SET books = ?
                            WHERE id_reader = ?""", (books, id_reader))

        else:
            status = False

        self.con.commit()  # Сохраняем изменения
        cur.close()
        return status

    def return_book(self, id_reader, id_book):
        # У данного пользователя эта книга точно есть
        cur = self.con.cursor()
        # Проверка задолженности по книге
        debt = False
        return_data = cur.execute("""SELECT data_return
                        FROM books
                        WHERE id_book = ?""", (id_book,)).fetchone()[-1]
        return_data = datetime.date(*map(int, return_data.split('-')))
        if datetime.date.today() > return_data:
            debt = True
        # Меняем данные книги
        cur.execute("""UPDATE books
                        SET place = 0
                        SET data_take = NULL
                        SET data_return = NULL
                        WHERE id_book = ?""", (id_book,))

        # Меняем данные множества книг с этим названием
        id_title = cur.execute("""SELECT title
                                        FROM books
                                        WHERE id_book = ?)
                                    """, (id_book,)).fetchone()[-1]
        count = int(cur.execute("""SELECT stock
                                    FROM books_title
                                    WHERE id_title = ?
                                    """, (id_title,)).fetchone()[-1])
        cur.execute("""UPDATE books_title
                        SET stock = ?
                        WHERE id_title = ?""", (count + 1, id_title))

        # Меняем список книг читателя
        books = cur.execute("""SELECT books
                                FROM readers
                                WHERE id_reader = ?""", (id_reader,)).fetchone()[-1].split()
        del books[books.index(str(id_book))]
        cur.execute("""UPDATE readers
                        SET books = ?
                        WHERE id_reader = ?""", (' '.join(books), id_reader))
        self.con.commit()
        cur.close()
        return True, debt

    def create_reader(self, name):
        # Пользователь ранее не существовал
        cur = self.con.cursor()
        cur.execute("""INSERT 
                        INTO readers(name, books) 
                        VALUES(?, '')""", (name, ))
        self.con.commit()
        id_reader = cur.execute("""SELECT id_reader
                                    FROM readers
                                    WHERE name = ?""", (name, )).fetchone()[-1]
        cur.close()
        return True, int(id_reader)


    def add_new_book(self, title, count, author, section, picture=None):
        cur
        # Создаём книгу с таким названием

    def close(self):
        self.con.close()
