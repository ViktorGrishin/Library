from PyQt5.QtWidgets import QWidget


class UserWnd(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.parentForm = args[0]
