"""
screens/login_ui.py
====================
Definição PURAMENTE VISUAL da tela de login do SISPE.

Equivalente ao antigo login.ui, em Python porque o Qt Designer não reconhece
componentes do PyQt6-Fluent-Widgets sem o plugin pago. Segue a mesma
convenção do pyuic: uma classe `Ui_LoginScreen` com `setupUi(tela)` que só
monta os widgets — sem autenticação, sem banco, sem lógica.

Quem dá vida a estes widgets é screens/login_qt.py.

Requer: pip install PyQt6-Fluent-Widgets
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from qfluentwidgets import (
    LineEdit, PasswordLineEdit, PrimaryPushButton, TitleLabel,
    CaptionLabel, SimpleCardWidget,
)

from screens.utils import aplicar_sombra
from screens.theme import CORES


class Ui_LoginScreen:
    """Monta a interface visual da tela de login e expõe os widgets como
    atributos de instância. Não faz nada além disso.

    Uso (em screens/login_qt.py):
        self.ui = Ui_LoginScreen()
        self.ui.setupUi(self)
        # depois: self.ui.inputUsuario, self.ui.inputSenha, self.ui.bntContinuar
    """

    def setupUi(self, tela: QWidget):
        tela.setStyleSheet("background: transparent;")

        raiz = QVBoxLayout(tela)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.cardLogin = SimpleCardWidget(tela)
        self.cardLogin.setBorderRadius(22)
        self.cardLogin.setFixedWidth(440)
        aplicar_sombra(self.cardLogin, blur=36, y_offset=10, alpha=22)

        v = QVBoxLayout(self.cardLogin)
        v.setContentsMargins(40, 44, 40, 40)
        v.setSpacing(6)
        v.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        marca = CaptionLabel("🧭  SISPE", self.cardLogin)
        marca.setStyleSheet(
            f"color: {CORES['azul']}; font-size: 15px; font-weight: 700; "
            "letter-spacing: 2px; background: transparent;"
        )
        marca.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(marca)

        titulo = TitleLabel("Bem-vindo(a) de volta", self.cardLogin)
        titulo.setStyleSheet(f"color: {CORES['texto']}; font-size: 24px; background: transparent;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(titulo)

        subtitulo = QLabel(
            "Acesse para acompanhar, com calma, o suporte psicológico dos alunos",
            self.cardLogin,
        )
        subtitulo.setWordWrap(True)
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet(f"color: {CORES['texto_sec']}; font-size: 13px; background: transparent;")
        v.addWidget(subtitulo)

        v.addSpacing(20)

        # PasswordLineEdit já vem com botão de "olhinho" embutido — não
        # precisamos mais do btnVerSenha manual que existia antes.
        self.inputUsuario = LineEdit(self.cardLogin)
        self.inputUsuario.setPlaceholderText("Usuário")
        self.inputUsuario.setFixedHeight(48)
        v.addWidget(self.inputUsuario)

        v.addSpacing(10)

        self.inputSenha = PasswordLineEdit(self.cardLogin)
        self.inputSenha.setPlaceholderText("Senha")
        self.inputSenha.setFixedHeight(48)
        v.addWidget(self.inputSenha)

        v.addSpacing(26)

        self.bntContinuar = PrimaryPushButton("Entrar", self.cardLogin)
        self.bntContinuar.setFixedHeight(48)
        v.addWidget(self.bntContinuar)

        raiz.addWidget(self.cardLogin, alignment=Qt.AlignmentFlag.AlignCenter)
