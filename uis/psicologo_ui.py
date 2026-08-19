"""
screens/psicologo_ui.py
========================
Definição PURAMENTE VISUAL da tela de cadastro de alunos (psicólogo).

Equivalente ao antigo psicologo.ui, em Python para poder usar
PyQt6-Fluent-Widgets. Segue a convenção do pyuic: uma classe
`Ui_PsicologoScreen` com `setupUi(tela)` que só monta os widgets — sem
consultas ao banco, sem regra de negócio, sem conexões de sinal com
comportamento.

Quem dá vida a estes widgets é screens/psicologo.py.

Requer: pip install PyQt6-Fluent-Widgets
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView

from qfluentwidgets import (
    LineEdit, ComboBox, SearchLineEdit, PrimaryPushButton, PushButton,
    TitleLabel, CaptionLabel, StrongBodyLabel, SimpleCardWidget,
    TableWidget, ScrollArea,
)

from screens.utils import aplicar_sombra
from screens.theme import CORES


class Ui_PsicologoScreen:
    """Monta a interface visual da tela do psicólogo e expõe os widgets
    como atributos de instância. Não faz nada além disso.

    Uso (em screens/psicologo.py):
        self.ui = Ui_PsicologoScreen()
        self.ui.setupUi(self)
        # depois: self.ui.inputNome, self.ui.btnCadastrar, self.ui.tabelaAlunos, etc.
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
        corpo.addWidget(self._montar_cadastro())
        corpo.addWidget(self._montar_tabela(), 1)

    # ------------------------------------------------------------------ #
    def _montar_titulo(self):
        titulo = TitleLabel("Cadastro de Alunos — Atendimento Psicológico")
        titulo.setStyleSheet(f"color: {CORES['navy']}; font-size: 26px; background: transparent;")
        return titulo

    def _montar_cadastro(self):
        card = SimpleCardWidget()
        card.setBorderRadius(18)
        aplicar_sombra(card, blur=24, y_offset=6, alpha=18)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

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

        self.inputNome = LineEdit(card)
        self.inputNome.setPlaceholderText("Nome completo do aluno")
        self.inputNome.setFixedHeight(44)

        self.inputSala = LineEdit(card)
        self.inputSala.setPlaceholderText("Ex: A101")
        self.inputSala.setFixedHeight(44)
        self.inputSala.setFixedWidth(120)

        self.inputSerie = LineEdit(card)
        self.inputSerie.setPlaceholderText("Ex: 9º ano")
        self.inputSerie.setFixedHeight(44)
        self.inputSerie.setFixedWidth(140)

        self.comboGravidade = ComboBox(card)
        self.comboGravidade.addItems(["Baixo", "Médio", "Grave"])
        self.comboGravidade.setFixedHeight(44)
        self.comboGravidade.setFixedWidth(140)

        linha.addLayout(_campo("Nome do aluno", self.inputNome), 2)
        linha.addLayout(_campo("Sala", self.inputSala))
        linha.addLayout(_campo("Série", self.inputSerie))
        linha.addLayout(_campo("Gravidade", self.comboGravidade))
        layout.addLayout(linha)

        linha_botoes = QHBoxLayout()
        linha_botoes.addStretch()
        self.btnCadastrar = PrimaryPushButton("➕ Cadastrar Aluno", card)
        self.btnCadastrar.setFixedHeight(44)
        linha_botoes.addWidget(self.btnCadastrar)
        layout.addLayout(linha_botoes)

        return card

    def _montar_tabela(self):
        card = SimpleCardWidget()
        card.setBorderRadius(18)
        card.setMinimumHeight(480)
        aplicar_sombra(card, blur=24, y_offset=6, alpha=18)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        cabecalho = QHBoxLayout()
        titulo = StrongBodyLabel("Lista de Alunos Cadastrados", card)
        titulo.setStyleSheet(f"color: {CORES['texto']}; background: transparent;")
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()

        self.inputBusca = SearchLineEdit(card)
        self.inputBusca.setPlaceholderText("Pesquisar aluno por nome...")
        self.inputBusca.setFixedWidth(280)
        cabecalho.addWidget(self.inputBusca)

        self.btnLimpar = PushButton("🗑️ Limpar", card)
        cabecalho.addWidget(self.btnLimpar)

        layout.addLayout(cabecalho)

        self.tabelaAlunos = TableWidget(card)
        self.tabelaAlunos.setColumnCount(6)
        self.tabelaAlunos.setHorizontalHeaderLabels(
            ["Nome", "Sala", "Série", "Gravidade", "Data", "Ações"]
        )
        self.tabelaAlunos.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)
        self.tabelaAlunos.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self.tabelaAlunos.verticalHeader().setDefaultSectionSize(52)
        self.tabelaAlunos.verticalHeader().hide()

        header = self.tabelaAlunos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, 6):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.tabelaAlunos)

        return card
