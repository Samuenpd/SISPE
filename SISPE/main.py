import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget

from database import DatabaseManager
from screens.login_qt import LoginScreen
from main_app_qt import MainApp


class App(QStackedWidget):
    def __init__(self):
        super().__init__()

        # banco
        self.db = DatabaseManager()

        # controle de usuário
        self.usuario_logado = None

        # telas principais
        self.login = LoginScreen(self, self.db)
        self.main_app = MainApp(self.db, self)

        # adiciona no stack
        self.addWidget(self.login)     # index 0
        self.addWidget(self.main_app)  # index 1

        # começa no login
        self.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = App()
    window.resize(1000, 600)
    window.show()

    sys.exit(app.exec())