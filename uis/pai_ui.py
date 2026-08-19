"""
uis/pai_ui.py
==============
Definição PURAMENTE VISUAL da tela do responsável (pai/mãe) — "Meus Filhos".

Equivalente ao antigo pai.ui, em Python para poder usar
PyQt6-Fluent-Widgets. Sem banco de dados, sem regra de negócio, sem
conexões de sinal com comportamento — só monta os widgets.

Quem dá vida a estes widgets é screens/pai.py.

Requer: pip install PyQt6-Fluent-Widgets
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHeaderView

from qfluentwidgets import (
    TitleLabel, CaptionLabel, StrongBodyLabel, SimpleCardWidget,
    TableWidget, TextEdit, ScrollArea,
)

from screens.utils import aplicar_sombra
from screens.theme import CORES


class Ui_PaiScreen:
    """Monta a interface visual da tela do responsável e expõe os widgets
    como atributos de instância.

    Uso (em screens/pai.py):
        self.ui = Ui_PaiScreen()
        self.ui.setupUi(self)
    """

    def setupUi(self, tela: QWidget):
        tela.setStyleSheet("background: transparent;")

        raiz = QVBoxLayout(tela)
        raiz.setContentsMargins(0, 0, 0, 0)

        self.scrollArea = ScrollArea(tela)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("background: transparent; border: none;")
        self.scrollArea.viewport().setStyleSheet("background: transparent;")
        raiz.addWidget(self.scrollArea)

        self.conteudo = QWidget(tela)
        self.conteudo.setStyleSheet("background: transparent;")
        self.scrollArea.setWidget(self.conteudo)

        corpo = QVBoxLayout(self.conteudo)
        corpo.setSpacing(20)
        corpo.setContentsMargins(48, 40, 48, 40)

        corpo.addLayout(self._montar_topo())
        corpo.addWidget(self._montar_tabela())
        corpo.addWidget(self._montar_relatorios(), 1)

    # ------------------------------------------------------------------ #
    def _montar_topo(self):
        v = QVBoxLayout()
        v.setSpacing(2)

        titulo = TitleLabel("Meus Filhos")
        titulo.setStyleSheet(f"color: {CORES['navy']}; font-size: 24px; background: transparent;")
        v.addWidget(titulo)

        subtitulo = CaptionLabel("Selecione um aluno na lista para ver os relatórios registrados.")
        subtitulo.setStyleSheet(f"color: {CORES['texto_sec']}; background: transparent;")
        v.addWidget(subtitulo)

        return v

    def _montar_tabela(self):
        card = SimpleCardWidget()
        card.setBorderRadius(16)
        card.setMaximumHeight(260)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        titulo = StrongBodyLabel("Alunos Vinculados", card)
        titulo.setStyleSheet(f"color: {CORES['texto']}; background: transparent;")
        layout.addWidget(titulo)

        self.tabelaFilhos = TableWidget(card)
        self.tabelaFilhos.setColumnCount(3)
        self.tabelaFilhos.setHorizontalHeaderLabels(["Nome", "Sala", "Série"])
        self.tabelaFilhos.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)
        self.tabelaFilhos.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self.tabelaFilhos.verticalHeader().setDefaultSectionSize(48)
        self.tabelaFilhos.verticalHeader().hide()

        header = self.tabelaFilhos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.tabelaFilhos)

        self.labelSemFilhos = CaptionLabel(
            "Nenhum aluno vinculado à sua conta ainda. Fale com a administração da escola.",
            card,
        )
        self.labelSemFilhos.setStyleSheet(f"color: {CORES['texto_sec']}; background: transparent;")
        self.labelSemFilhos.setWordWrap(True)
        self.labelSemFilhos.setVisible(False)
        layout.addWidget(self.labelSemFilhos)

        return card

    def _montar_relatorios(self):
        card = SimpleCardWidget()
        card.setBorderRadius(16)
        card.setMinimumHeight(280)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        titulo = StrongBodyLabel("Relatórios", card)
        titulo.setStyleSheet(f"color: {CORES['texto']}; background: transparent;")
        layout.addWidget(titulo)

        self.textRelatorios = TextEdit(card)
        self.textRelatorios.setReadOnly(True)
        self.textRelatorios.setPlaceholderText("Selecione um aluno acima para ver os relatórios...")
        layout.addWidget(self.textRelatorios, 1)

        return card
