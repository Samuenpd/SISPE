"""
uis/admin_ui.py
=================
Definição PURAMENTE VISUAL da tela de administração (gerenciar usuários).

Equivalente ao antigo admin.ui, em Python para poder usar
PyQt6-Fluent-Widgets. Sem banco de dados, sem regra de negócio, sem
conexões de sinal com comportamento — só monta os widgets.

Quem dá vida a estes widgets é screens/admin.py.

Requer: pip install PyQt6-Fluent-Widgets
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView

from qfluentwidgets import (
    LineEdit, ComboBox, SearchLineEdit, PrimaryPushButton,
    TitleLabel, CaptionLabel, StrongBodyLabel, SimpleCardWidget,
    TableWidget, ScrollArea,
)

from screens.utils import aplicar_sombra
from screens.theme import CORES


class Ui_AdminScreen:
    """Monta a interface visual da tela de administração e expõe os
    widgets como atributos de instância.

    Uso (em screens/admin.py):
        self.ui = Ui_AdminScreen()
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
        corpo.setSpacing(24)
        corpo.setContentsMargins(48, 40, 48, 40)

        corpo.addWidget(self._montar_titulo())
        corpo.addWidget(self._montar_stats())
        corpo.addWidget(self._montar_criar_usuario())
        corpo.addWidget(self._montar_tabela(), 1)

    # ------------------------------------------------------------------ #
    def _montar_titulo(self):
        titulo = TitleLabel("Painel Administrativo — Gerenciamento de Usuários")
        titulo.setStyleSheet(f"color: {CORES['navy']}; font-size: 24px; background: transparent;")
        return titulo

    def _montar_stats(self):
        card = SimpleCardWidget()
        card.setBorderRadius(16)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(24, 18, 24, 18)

        self.labelInfo = StrongBodyLabel(
            "📊 Total: 0 | 👨‍👩‍👧 Responsáveis: 0 | 🧠 Psicólogos: 0", card
        )
        self.labelInfo.setStyleSheet(f"color: {CORES['texto']}; background: transparent;")
        layout.addWidget(self.labelInfo)
        return card

    def _montar_criar_usuario(self):
        card = SimpleCardWidget()
        card.setBorderRadius(16)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        titulo = CaptionLabel("Criar novo usuário", card)
        titulo.setStyleSheet(f"color: {CORES['texto_sec']}; background: transparent;")
        layout.addWidget(titulo)

        linha = QHBoxLayout()
        linha.setSpacing(14)

        self.inputUsername = LineEdit(card)
        self.inputUsername.setPlaceholderText("Digite o username")
        self.inputUsername.setFixedHeight(44)

        self.inputSenha = LineEdit(card)
        self.inputSenha.setPlaceholderText("Digite a senha")
        self.inputSenha.setFixedHeight(44)

        self.comboTipo = ComboBox(card)
        self.comboTipo.addItems(["👨‍👩‍👧 Pai", "🧠 Psicólogo"])
        self.comboTipo.setFixedHeight(44)
        self.comboTipo.setFixedWidth(180)

        self.btnCriarUsuario = PrimaryPushButton("➕ Criar Usuário", card)
        self.btnCriarUsuario.setFixedHeight(44)

        linha.addWidget(self.inputUsername, 2)
        linha.addWidget(self.inputSenha, 2)
        linha.addWidget(self.comboTipo)
        linha.addWidget(self.btnCriarUsuario)

        layout.addLayout(linha)
        return card

    def _montar_tabela(self):
        card = SimpleCardWidget()
        card.setBorderRadius(16)
        card.setMinimumHeight(420)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        cabecalho = QHBoxLayout()
        titulo = StrongBodyLabel("Usuários Cadastrados", card)
        titulo.setStyleSheet(f"color: {CORES['texto']}; background: transparent;")
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()

        self.inputBusca = SearchLineEdit(card)
        self.inputBusca.setPlaceholderText("Pesquisar por username...")
        self.inputBusca.setFixedWidth(260)
        cabecalho.addWidget(self.inputBusca)

        layout.addLayout(cabecalho)

        self.tabelaUsuarios = TableWidget(card)
        self.tabelaUsuarios.setColumnCount(3)
        self.tabelaUsuarios.setHorizontalHeaderLabels(["Username", "Tipo", "Ações"])
        self.tabelaUsuarios.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)
        self.tabelaUsuarios.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self.tabelaUsuarios.verticalHeader().setDefaultSectionSize(52)
        self.tabelaUsuarios.verticalHeader().hide()

        header = self.tabelaUsuarios.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.tabelaUsuarios)
        return card
