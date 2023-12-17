import sqlite3


class DataBase:
    def __init__(self, path='database.'):
        self.con = sqlite3.connect(path)
