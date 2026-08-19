"""
uis/historico_relatorios_ui.py
================================
Definição PURAMENTE VISUAL da tela de histórico de relatórios de um aluno.

Equivalente ao antigo historico_relatorios.ui, em Python para poder usar
PyQt6-Fluent-Widgets. Sem banco de dados, sem geração de PDF, sem conexões
de sinal com comportamento — só monta os widgets.

Quem dá vida a estes widgets é screens/historico_relatorios.py.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView

from qfluentwidgets import (
    PushButton, PrimaryPushButton, TitleLabel, StrongBodyLabel,
    SimpleCardWidget, TableWidget, TextEdit, ScrollArea,
)

from screens.utils import aplicar_sombra
from screens.theme import CORES


class Ui_HistoricoRelatoriosScreen:
    """Monta a interface visual da tela de histórico e expõe os widgets
    como atributos de instância.

    Uso (em screens/historico_relatorios.py):
        self.ui = Ui_HistoricoRelatoriosScreen()
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
        corpo.addWidget(self._montar_detalhe(), 1)

    # ------------------------------------------------------------------ #
    def _montar_topo(self):
        linha = QHBoxLayout()
        linha.setSpacing(14)

        self.btnVoltar = PushButton("← Voltar")
        linha.addWidget(self.btnVoltar)

        self.labelTitulo = TitleLabel("Histórico de Relatórios")
        self.labelTitulo.setStyleSheet(f"color: {CORES['navy']}; font-size: 22px; background: transparent;")
        linha.addWidget(self.labelTitulo)

        linha.addStretch()

        self.btnExportarPDF = PrimaryPushButton("📄 Exportar Prontuário (PDF)")
        linha.addWidget(self.btnExportarPDF)
        return linha

    def _montar_tabela(self):
        card = SimpleCardWidget()
        card.setBorderRadius(16)
        card.setMaximumHeight(280)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        titulo = StrongBodyLabel("Relatórios Registrados", card)
        titulo.setStyleSheet(f"color: {CORES['texto']}; background: transparent;")
        layout.addWidget(titulo)

        self.tabelaHistorico = TableWidget(card)
        self.tabelaHistorico.setColumnCount(2)
        self.tabelaHistorico.setHorizontalHeaderLabels(["Data", "Prévia"])
        self.tabelaHistorico.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)
        self.tabelaHistorico.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self.tabelaHistorico.verticalHeader().setDefaultSectionSize(48)
        self.tabelaHistorico.verticalHeader().hide()

        header = self.tabelaHistorico.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.tabelaHistorico)
        return card

    def _montar_detalhe(self):
        card = SimpleCardWidget()
        card.setBorderRadius(16)
        card.setMinimumHeight(300)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        titulo = StrongBodyLabel("Relatório Selecionado", card)
        titulo.setStyleSheet(f"color: {CORES['texto']}; background: transparent;")
        layout.addWidget(titulo)

        self.textRelatorioCompleto = TextEdit(card)
        self.textRelatorioCompleto.setReadOnly(True)
        self.textRelatorioCompleto.setPlaceholderText(
            "Selecione um relatório na tabela acima para ver o conteúdo completo..."
        )
        layout.addWidget(self.textRelatorioCompleto, 1)
        return card
