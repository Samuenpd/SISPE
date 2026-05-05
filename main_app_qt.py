from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QSizePolicy
from screens.home import HomeScreen
from screens.psicologo import PsicologoScreen
from screens.admin import AdminScreen
from screens.pai import PaiScreen

class MainApp(QMainWindow):
    def __init__(self, db, app):
        super().__init__()
        uic.loadUi("uis/Main.ui", self)

        # Remove páginas placeholder
        while self.stackedWidget.count():
            widget = self.stackedWidget.widget(0)
            self.stackedWidget.removeWidget(widget)

        self.db = db
        self.app = app

        # Políticas de expansão
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.stackedWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # O stackedWidget (índice 1) recebe todo o espaço extra
        self.centralwidget.layout().setStretch(1, 1)

        # Telas
        self.home = HomeScreen()
        self.psico = PsicologoScreen(db, app)
        self.admin = AdminScreen(db)
        self.pai = PaiScreen(db, app)

        self.stackedWidget.addWidget(self.home)
        self.stackedWidget.addWidget(self.psico)
        self.stackedWidget.addWidget(self.admin)
        self.stackedWidget.addWidget(self.pai)

        # Conexões da barra
        self.bnthome.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.home))
        self.bntvincular.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.admin))
        self.btngerenusua.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.admin))
        self.btnRegistrarAluno.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.psico))
        self.bntsair.clicked.connect(self.logout)

    def carregar_usuario(self, user):
        tipo = user["tipo"]
        self.btnRegistrarAluno.hide()
        self.bntvincular.hide()
        self.btngerenusua.hide()
        if tipo == "admin":
            self.btngerenusua.show()
            self.admin.atualizar()
        elif tipo == "psicologo":
            self.btnRegistrarAluno.show()
            self.psico.atualizar()
        elif tipo == "pai":
            self.pai.atualizar()
        self.stackedWidget.setCurrentWidget(self.home)

    def logout(self):
        self.app.setCurrentIndex(0)