import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget

from database import DatabaseManager
from screens.login_qt import LoginScreen
from main_app_qt import MainApp
from screens.theme import GLOBAL_STYLESHEET
import os


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

    def resolver_caminho(caminho_relativo):
        """ Retorna o caminho absoluto para o arquivo, funcionando em modo de desenvolvimento ou no .exe """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, caminho_relativo)
        return os.path.join(os.path.abspath("."), caminho_relativo)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLESHEET)  # estilo visual global (screens/theme.py)

    window = App()
    window.resize(1000, 600)
    window.show()

    sys.exit(app.exec())