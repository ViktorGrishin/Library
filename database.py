import sqlite3
import datetime


class DataBase:
    def __init__(self, path='database.sqlite'):
        self.con = sqlite3.connect(path)

    def take_book(self, id_title, id_reader, days=14):
        cur = self.con.cursor()
        status = True
        id_book = cur.execute("""SELECT id 
                                FROM books 
                                WHERE title = ? and place = 0""", (id_title,)).fetchone()
        if id_book:  # Есть свободные книги
            # Меняем статус книги
            print(id_book)
            today = datetime.date.today()
            return_day = today + datetime.timedelta(days=days)
            cur.execute("""UPDATE books
                            SET place = ?
                            SET data_taken = ?
                            SET data_return = ?
                            WHERE id = ?""", (id_reader, str(today), str(return_day), id_book))

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

        cur.close()
        return status

    def close(self):
        self.con.close()
