from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from screens.utils import aplicar_sombra

class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("uis/home.ui", self)

        # Sombra suave nos cards (profundidade calma, sem exagero)
        for card in (self.frameSaudacao, self.frameSobre, self.frameEquipe,
                     self.frameObjetivos, self.frameTeoria, self.frameODS):
            aplicar_sombra(card)

        # Scroll area para todo o conteúdo
        self.conteudo = QWidget()
        self.conteudo.setLayout(self.mainLayout)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.conteudo)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QScrollArea.Shape.NoFrame)

        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(0, 0, 0, 0)
        layout_externo.addWidget(self.scrollArea)

    def atualizar(self, usuario=None):
        """Atualiza a saudação personalizada."""
        if usuario:
            tipo = usuario['tipo'].capitalize()
            self.labelMensagem.setText(f"Bem-vindo(a), {tipo}!")