"""
uis/configuracoes_ui.py
=========================
Definição PURAMENTE VISUAL da tela de configurações (perfil + agenda do
psicólogo + lista de filhos do responsável).

Equivalente ao antigo configuracoes.ui, em Python para poder usar
PyQt6-Fluent-Widgets. Sem banco de dados, sem regra de negócio, sem
conexões de sinal com comportamento — só monta os widgets.

Quem dá vida a estes widgets é screens/configuracoes.py.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCalendarWidget,
    QScrollArea, QLineEdit, QTimeEdit,
)

from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, CaptionLabel, SimpleCardWidget,
    PrimaryPushButton, PushButton, ScrollArea as FluentScrollArea,
)

from screens.utils import aplicar_sombra
from screens.theme import CORES, estilo_lista


class Ui_ConfiguracoesScreen:
    """Monta a interface visual da tela de configurações e expõe os
    widgets como atributos de instância.

    Uso (em screens/configuracoes.py):
        self.ui = Ui_ConfiguracoesScreen()
        self.ui.setupUi(self)
    """

    def setupUi(self, tela: QWidget):
        tela.setStyleSheet("background: transparent;")

        raiz = QVBoxLayout(tela)
        raiz.setContentsMargins(0, 0, 0, 0)

        self.scrollArea = FluentScrollArea(tela)
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

        titulo = TitleLabel("⚙️ Configurações")
        titulo.setStyleSheet(f"color: {CORES['navy']}; font-size: 24px; background: transparent;")
        corpo.addWidget(titulo)

        corpo.addWidget(self._montar_perfil())
        corpo.addWidget(self._montar_filhos())
        corpo.addWidget(self._montar_agenda(), 1)

    # ------------------------------------------------------------------ #
    def _montar_perfil(self):
        card = SimpleCardWidget()
        card.setBorderRadius(18)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(6)

        icone = QLabel("👤", card)
        icone.setStyleSheet("font-size: 34px; background: transparent;")
        layout.addWidget(icone)

        self.labelUsername = StrongBodyLabel("usuario", card)
        self.labelUsername.setStyleSheet(f"color: {CORES['texto']}; font-size: 20px; background: transparent;")
        layout.addWidget(self.labelUsername)

        self.labelTipo = CaptionLabel("Tipo de conta", card)
        self.labelTipo.setStyleSheet(
            f"color: {CORES['azul']}; background: {CORES['azul_claro']}; "
            "border-radius: 10px; padding: 4px 12px;"
        )
        layout.addWidget(self.labelTipo)

        self.labelDataCriacao = CaptionLabel("Membro desde —", card)
        self.labelDataCriacao.setStyleSheet(f"color: {CORES['texto_sec']}; background: transparent;")
        layout.addWidget(self.labelDataCriacao)

        return card

    def _montar_filhos(self):
        from PyQt6.QtWidgets import QListWidget

        self.frameFilhos = SimpleCardWidget()
        self.frameFilhos.setBorderRadius(18)
        aplicar_sombra(self.frameFilhos, blur=20, y_offset=5, alpha=16)

        layout = QVBoxLayout(self.frameFilhos)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        titulo = StrongBodyLabel("🎓 Alunos Vinculados", self.frameFilhos)
        titulo.setStyleSheet(f"color: {CORES['texto']}; background: transparent;")
        layout.addWidget(titulo)

        self.listaFilhos = QListWidget(self.frameFilhos)
        self.listaFilhos.setStyleSheet(estilo_lista())
        layout.addWidget(self.listaFilhos)

        return self.frameFilhos

    def _montar_agenda(self):
        self.frameAgenda = SimpleCardWidget()
        self.frameAgenda.setBorderRadius(18)
        self.frameAgenda.setMinimumHeight(460)
        aplicar_sombra(self.frameAgenda, blur=20, y_offset=5, alpha=16)

        layout = QHBoxLayout(self.frameAgenda)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        self.calendarAgenda = QCalendarWidget(self.frameAgenda)
        self.calendarAgenda.setMinimumWidth(320)
        self.calendarAgenda.setMaximumWidth(360)
        self.calendarAgenda.setStyleSheet(f"""
            QCalendarWidget {{ background-color: #FFFFFF; border-radius: 8px; }}
            QCalendarWidget QTableView {{ background-color: #FFFFFF; color: {CORES['texto']}; }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{ background-color: {CORES['azul']}; }}
            QCalendarWidget QToolButton {{ color: white; }}
            QCalendarWidget QHeaderView::section {{ background-color: #F1F5F9; color: {CORES['texto_sec']}; }}
        """)
        layout.addWidget(self.calendarAgenda)

        direita = QVBoxLayout()
        direita.setSpacing(10)

        self.labelDia = StrongBodyLabel("Compromissos do dia", self.frameAgenda)
        self.labelDia.setStyleSheet(f"color: {CORES['texto']}; font-size: 16px; background: transparent;")
        direita.addWidget(self.labelDia)

        self.scrollCompromissos = QScrollArea(self.frameAgenda)
        self.scrollCompromissos.setWidgetResizable(True)
        self.scrollCompromissos.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scrollCompromissos.setStyleSheet("background: transparent;")

        self.conteudoCompromissos = QWidget()
        self.conteudoCompromissos.setStyleSheet("background: transparent;")
        self.layoutCompromissos = QVBoxLayout(self.conteudoCompromissos)
        self.layoutCompromissos.setSpacing(10)
        self.layoutCompromissos.setContentsMargins(0, 0, 0, 0)
        self.scrollCompromissos.setWidget(self.conteudoCompromissos)
        direita.addWidget(self.scrollCompromissos, 1)

        self.btnNovoCompromisso = PushButton("+ Novo compromisso", self.frameAgenda)
        self.btnNovoCompromisso.setMinimumHeight(40)
        direita.addWidget(self.btnNovoCompromisso)

        self.frameNovoCompromisso = SimpleCardWidget(self.frameAgenda)
        self.frameNovoCompromisso.setBorderRadius(12)
        self.frameNovoCompromisso.setVisible(False)

        formNovo = QVBoxLayout(self.frameNovoCompromisso)
        formNovo.setContentsMargins(16, 16, 16, 16)
        formNovo.setSpacing(10)

        self.inputTitulo = QLineEdit(self.frameNovoCompromisso)
        self.inputTitulo.setPlaceholderText("Título do compromisso")
        formNovo.addWidget(self.inputTitulo)

        self.inputHora = QTimeEdit(self.frameNovoCompromisso)
        formNovo.addWidget(self.inputHora)

        self.inputDescricao = QLineEdit(self.frameNovoCompromisso)
        self.inputDescricao.setPlaceholderText("Descrição (opcional)")
        formNovo.addWidget(self.inputDescricao)

        # Seletor de cor — preenchido dinamicamente pela lógica
        # (screens.configuracoes._construir_seletor_de_cores), pois as cores
        # disponíveis fazem parte do comportamento, não do layout.
        self.layoutCores = QHBoxLayout()
        self.layoutCores.setSpacing(12)
        formNovo.addLayout(self.layoutCores)

        linhaBotoes = QHBoxLayout()
        self.btnSalvarCompromisso = PrimaryPushButton("Salvar", self.frameNovoCompromisso)
        self.btnCancelarCompromisso = PushButton("Cancelar", self.frameNovoCompromisso)
        linhaBotoes.addWidget(self.btnSalvarCompromisso)
        linhaBotoes.addWidget(self.btnCancelarCompromisso)
        formNovo.addLayout(linhaBotoes)

        direita.addWidget(self.frameNovoCompromisso)

        layout.addLayout(direita, 1)
        return self.frameAgenda
