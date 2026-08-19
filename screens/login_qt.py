"""
screens/login_qt.py
====================
Lógica da tela de login do SISPE.

Este arquivo NÃO constrói nenhum widget diretamente — toda a interface visual
vive em screens/login_ui.py (classe Ui_LoginScreen). Aqui só ficam:
autenticação, conexão de sinais e navegação entre telas.
"""

from PyQt6.QtWidgets import QWidget, QMessageBox

from uis.login_ui import Ui_LoginScreen
from screens.fundo import BackgroundWidget
from screens.utils import mostrar_alerta


class LoginScreen(QWidget):
    def __init__(self, app, db):
        super().__init__()
        self.app = app
        self.db = db

        self.ui = Ui_LoginScreen()
        self.ui.setupUi(self)

        # Fundo orgânico compartilhado (screens/fundo.py)
        self.fundo = BackgroundWidget(self)
        self.installEventFilter(self.fundo)

        self.ui.bntContinuar.clicked.connect(self.login)

    def login(self):
        usuario = self.ui.inputUsuario.text().strip()
        senha = self.ui.inputSenha.text().strip()

        if not usuario or not senha:
            mostrar_alerta(self, QMessageBox.Icon.Warning, "Erro", "Preencha todos os campos")
            return

        resultado = self.db.login(usuario, senha)
        if resultado:
            self.app.usuario_logado = resultado
            self.app.main_app.carregar_usuario(resultado)
            self.app.setCurrentIndex(1)
            self.ui.inputUsuario.clear()
            self.ui.inputSenha.clear()
        else:
            mostrar_alerta(self, QMessageBox.Icon.Warning, "Erro", "Usuário ou senha inválidos")
