"""
uis/vincular_ui.py
====================
Definição PURAMENTE VISUAL da tela de vincular responsável (pai) a aluno.

Equivalente ao antigo vincular.ui, em Python para poder usar
PyQt6-Fluent-Widgets. Sem banco de dados, sem regra de negócio, sem
conexões de sinal com comportamento — só monta os widgets.

Quem dá vida a estes widgets é screens/vincular.py.

Requer: pip install PyQt6-Fluent-Widgets
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView

from qfluentwidgets import (
    ComboBox, PrimaryPushButton,
    TitleLabel, CaptionLabel, StrongBodyLabel, SimpleCardWidget,
    TableWidget, ScrollArea,
)

from screens.utils import aplicar_sombra
from screens.theme import CORES


class Ui_VincularScreen:
    """Monta a interface visual da tela de vínculo pai↔aluno e expõe os
    widgets como atributos de instância. Não faz nada além disso.

    Uso (em screens/vincular.py):
        self.ui = Ui_VincularScreen()
        self.ui.setupUi(self)
        # depois: self.ui.comboPai, self.ui.comboAluno, self.ui.btnVincular,
        # self.ui.tabelaVinculos, self.ui.labelInfo
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
        corpo.setSpacing(24)
        corpo.setContentsMargins(48, 40, 48, 40)

        corpo.addWidget(self._montar_titulo())
        corpo.addWidget(self._montar_stats())
        corpo.addWidget(self._montar_vincular())
        corpo.addWidget(self._montar_tabela(), 1)

    # ------------------------------------------------------------------ #
    def _montar_titulo(self):
        titulo = TitleLabel("Vincular Responsável a Aluno")
        titulo.setStyleSheet(f"color: {CORES['navy']}; font-size: 24px; background: transparent;")
        return titulo

    def _montar_stats(self):
        card = SimpleCardWidget()
        card.setBorderRadius(16)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(24, 18, 24, 18)

        self.labelInfo = StrongBodyLabel("🔗 Vínculos ativos: 0", card)
        self.labelInfo.setStyleSheet(f"color: {CORES['texto']}; background: transparent;")
        layout.addWidget(self.labelInfo)
        return card

    def _montar_vincular(self):
        card = SimpleCardWidget()
        card.setBorderRadius(16)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        titulo = CaptionLabel("Criar novo vínculo", card)
        titulo.setStyleSheet(f"color: {CORES['texto_sec']}; background: transparent;")
        layout.addWidget(titulo)

        def _campo(rotulo, widget):
            v = QVBoxLayout()
            v.setSpacing(6)
            lbl = CaptionLabel(rotulo)
            lbl.setStyleSheet(f"color: {CORES['texto_sec']}; background: transparent;")
            v.addWidget(lbl)
            v.addWidget(widget)
            return v

        linha = QHBoxLayout()
        linha.setSpacing(14)

        self.comboPai = ComboBox(card)
        self.comboPai.setFixedHeight(44)
        self.comboPai.setPlaceholderText("Selecione o responsável")

        self.comboAluno = ComboBox(card)
        self.comboAluno.setFixedHeight(44)
        self.comboAluno.setPlaceholderText("Selecione o aluno")

        self.btnVincular = PrimaryPushButton("🔗 Vincular", card)
        self.btnVincular.setFixedHeight(44)

        linha.addLayout(_campo("Responsável (pai)", self.comboPai), 1)
        linha.addLayout(_campo("Aluno", self.comboAluno), 1)

        # Espaço vazio equivalente ao rótulo do combo, para o botão alinhar
        # com a base dos campos ao lado, não com o topo.
        colunaBotao = QVBoxLayout()
        colunaBotao.setSpacing(6)
        espaco = CaptionLabel(" ")
        espaco.setStyleSheet("background: transparent;")
        colunaBotao.addWidget(espaco)
        colunaBotao.addWidget(self.btnVincular)
        linha.addLayout(colunaBotao)

        layout.addLayout(linha)
        return card

    def _montar_tabela(self):
        card = SimpleCardWidget()
        card.setBorderRadius(16)
        card.setMinimumHeight(360)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        titulo = StrongBodyLabel("Vínculos Cadastrados", card)
        titulo.setStyleSheet(f"color: {CORES['texto']}; background: transparent;")
        layout.addWidget(titulo)

        self.tabelaVinculos = TableWidget(card)
        self.tabelaVinculos.setColumnCount(3)
        self.tabelaVinculos.setHorizontalHeaderLabels(["Responsável", "Aluno", "Ações"])
        self.tabelaVinculos.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)
        self.tabelaVinculos.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self.tabelaVinculos.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabelaVinculos.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tabelaVinculos.verticalHeader().setDefaultSectionSize(52)
        self.tabelaVinculos.verticalHeader().hide()

        header = self.tabelaVinculos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.tabelaVinculos)
        return card
