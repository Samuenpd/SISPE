"""
uis/editar_aluno_ui.py
========================
Definição PURAMENTE VISUAL da tela de edição de aluno + novo relatório.

Equivalente ao antigo editar_aluno.ui, em Python para poder usar
PyQt6-Fluent-Widgets. Segue a convenção do pyuic: uma classe
`Ui_EditarAlunoScreen` com `setupUi(tela)` que só monta os widgets — sem
banco de dados, sem geração de PDF, sem conexões de sinal com comportamento.

Quem dá vida a estes widgets é screens/editar_aluno.py.

Requer: pip install PyQt6-Fluent-Widgets
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from qfluentwidgets import (
    LineEdit, ComboBox, PrimaryPushButton, PushButton, TitleLabel,
    CaptionLabel, StrongBodyLabel, SimpleCardWidget, TextEdit, ScrollArea,
)

from screens.utils import aplicar_sombra
from screens.theme import CORES


class Ui_EditarAlunoScreen:
    """Monta a interface visual da tela de edição de aluno e expõe os
    widgets como atributos de instância. Não faz nada além disso.

    Uso (em screens/editar_aluno.py):
        self.ui = Ui_EditarAlunoScreen()
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
        corpo.addWidget(self._montar_info())
        corpo.addWidget(self._montar_relatorio(), 1)

    # ------------------------------------------------------------------ #
    def _montar_topo(self):
        linha = QHBoxLayout()
        linha.setSpacing(14)

        self.btnVoltar = PushButton("← Voltar")
        linha.addWidget(self.btnVoltar)

        self.labelTitulo = TitleLabel("Editando Aluno")
        self.labelTitulo.setStyleSheet(f"color: {CORES['navy']}; font-size: 22px; background: transparent;")
        linha.addWidget(self.labelTitulo)

        linha.addStretch()
        return linha

    def _montar_info(self):
        card = SimpleCardWidget()
        card.setBorderRadius(16)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

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
        self.inputNome.setFixedHeight(44)

        self.inputSala = LineEdit(card)
        self.inputSala.setFixedHeight(44)
        self.inputSala.setFixedWidth(120)

        self.inputSerie = LineEdit(card)
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
        self.btnSalvar = PrimaryPushButton("💾 Salvar Informações", card)
        self.btnSalvar.setFixedHeight(44)
        linha_botoes.addWidget(self.btnSalvar)
        layout.addLayout(linha_botoes)

        return card

    def _montar_relatorio(self):
        card = SimpleCardWidget()
        card.setBorderRadius(16)
        card.setMinimumHeight(360)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        titulo = StrongBodyLabel("Escrever Novo Relatório", card)
        titulo.setStyleSheet(f"color: {CORES['texto']}; background: transparent;")
        layout.addWidget(titulo)

        self.textNovoRelatorio = TextEdit(card)
        self.textNovoRelatorio.setPlaceholderText("Escreva aqui as observações do atendimento...")
        layout.addWidget(self.textNovoRelatorio, 1)

        rodape = QHBoxLayout()
        rodape.setSpacing(12)

        self.labelStatusPdf = CaptionLabel("", card)
        self.labelStatusPdf.setStyleSheet(f"color: {CORES['texto_sec']}; background: transparent;")
        rodape.addWidget(self.labelStatusPdf)
        rodape.addStretch()

        self.btnHistorico = PushButton("📖 Ver Histórico", card)
        rodape.addWidget(self.btnHistorico)

        self.btnSalvarRelatorio = PrimaryPushButton("💾 Salvar Relatório (PDF)", card)
        rodape.addWidget(self.btnSalvarRelatorio)

        layout.addLayout(rodape)
        return card
