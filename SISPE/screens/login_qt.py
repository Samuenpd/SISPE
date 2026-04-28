from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox

class LoginScreen(QMainWindow):
    def __init__(self, app, db):
        super().__init__()

        uic.loadUi("uis/login.ui", self)

        self.app = app
        self.db = db

        self.bntContinuar.clicked.connect(self.login)
        self.btnVerSenha.clicked.connect(self.toggle_senha)
        self.btnVerSenha.setText("🔒")

        self.senha_visivel = False

    def login(self):
        usuario = self.inputUsuario.text().strip()
        senha = self.InputSenha.text().strip()

        # validação básica
        if not usuario or not senha:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos")
            return

        result = self.db.login(usuario, senha)

        if result:
            # salva usuário logado
            self.app.usuario_logado = result

            # manda pro sistema principal
            self.app.main_app.carregar_usuario(result)

            # troca tela
            self.app.setCurrentIndex(1)

            # limpa campos depois do login
            self.inputUsuario.clear()
            self.InputSenha.clear()

        else:
            QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos")


    def toggle_senha(self):
        if self.senha_visivel:
            self.InputSenha.setEchoMode(self.InputSenha.EchoMode.Password)
            self.btnVerSenha.setText("🔒")
        else:
            self.InputSenha.setEchoMode(self.InputSenha.EchoMode.Normal)
            self.btnVerSenha.setText("🔓")

        self.senha_visivel = not self.senha_visivel