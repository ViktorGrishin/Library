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
                             SET place = ?,
                              data_taken = ?,
                              data_return = ?
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
            books += str(id_book) + ' '
            cur.execute("""UPDATE readers
                            SET books = ?
                            WHERE id_reader = ?""", (books, id_reader))

        else:
            status = False

        self.con.commit()  # Сохраняем изменения
        cur.close()
        return status

    def return_book(self, id_book, id_reader):
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
                        SET place = 0,
                         data_taken = NULL,
                         data_return = NULL
                        WHERE id_book = ?""", (id_book,))

        # Меняем данные множества книг с этим названием
        id_title = cur.execute("""SELECT title
                                        FROM books
                                        WHERE id_book = ?
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
        cur = self.con.cursor()
        id_reader = cur.execute("""SELECT id_reader
                                    FROM readers
                                    WHERE name = ?""", (name,)).fetchone()
        if id_reader:
            return False, id_reader[-1]

        # Пользователь ранее не существовал

        cur.execute("""INSERT 
                        INTO readers (name, books) 
                        VALUES(?, '')""", (name,))

        id_reader = cur.execute("""SELECT id_reader
                                    FROM readers
                                    WHERE name = ?""", (name,)).fetchone()[-1]
        self.con.commit()
        cur.close()
        return True, int(id_reader)

    def add_books(self, title, count, author, section, picture=None):  # добавляет книги
        cur = self.con.cursor()
        id_title = cur.execute("""SELECT id_title
                                    FROM books_title
                                    WHERE title = ?""", (title, )).fetchone()

        # Проверка наличия автора
        id_author = cur.execute("""SELECT id_author
                                    FROM authors
                                    WHERE name = ?
                                    """, (author,)).fetchone()

        if not id_author:
            cur.execute("""INSERT 
                            INTO authors (name, )
                            VALUES (?, )""", (author,))
            id_author = cur.execute("""SELECT id_author
                                        FROM authors
                                        WHERE name = ?""", (author,)).fetchone()
        id_author = id_author[-1]
        # Проверка наличия секции
        id_section = cur.execute("""SELECT id_section
                                    FROM sections
                                    WHERE title = ?""", (section,)).fetchone()
        if not id_section:
            cur.execute("""INSERT
                            INTO section (title, )
                            VALUES (?, )""", section)
            id_section = cur.execute("""SELECT id_section
                                                FROM sections
                                                WHERE title = ?""", (section,)).fetchone()
        id_section = id_section[-1]

        if not id_title:
            # Создаём обложку книги
            cur.execute("""INSERT INTO books_title (title, stock, total, author, picture, section)
                                VALUES (?, ?, ?, ?, ?, ?)""", (title, count, count, id_author, picture, id_section))
            id_title = cur.execute("""SELECT id_title
                                                FROM books_title
                                                WHERE title = ?""", (title,)).fetchone()[-1]
        else:
            # Увеличиваем общее число книг
            id_title = id_title[-1]
            stock, total = cur.execute("""SELECT stock, total
                                            FROM books_title
                                            WHERE id_title = ?""", (id_title, )).fetchone()
            cur.execute("""UPDATE books_title
                            SET stock = ?, 
                                total = ?
                            WHERE id_title = ?""", (stock + count, total + count, id_title))

        # Добавляем книги в общий список книг
        for i in range(count):
            cur.execute("""INSERT INTO books(title, place)
                            VALUES(?, 0)""", (id_title, ))
        self.con.commit()
        cur.close()
        return True

    def add_picture_book(self, id_title, picture):
        cur = self.con.cursor()
        cur.execute("""UPDATE books_title
                        SET picture = ?
                        WHERE id_title = ?""", (picture, id_title))
        self.con.commit()
        cur.close()
        return True


    def filter_books(self, author=None, section=None):
        cur = self.con.cursor()
        condition = []
        # Критерии выбора книги
        if author:
            id_author = cur.execute("""SELECT id_author
                                        FROM authors 
                                        WHERE name = ?""", (author,)).fetchone()[-1]

            condition.append(f'author = {id_author}')
        if section:
            id_section = cur.execute("""SELECT id_section
                                            FROM sections
                                            WHERE title = ?""", (section,)).fetchone()[-1]
            condition.append(f'section = {id_section}')
        # Формулируем критерии в виде условия WHERE SQL запроса
        if condition:
            condition = 'WHERE ' + ' AND '.join(condition)
        else:
            condition = ''
        books = cur.execute("""SELECT id_title, title, picture
                                FROM books_title
                                 """ + condition).fetchall()
        return books

    def write_off_book(self, id_book):
        pass

    def close(self):
        self.con.close()



