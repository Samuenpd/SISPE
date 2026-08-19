"""
uis/main_ui.py
================
Definição PURAMENTE VISUAL da janela principal do SISPE: barra de
navegação superior (TopBar) + QStackedWidget que hospeda as telas
internas (home, psicólogo, admin, pai, vincular, etc).

Equivalente ao antigo Main.ui, em Python porque o Qt Designer não
reconhece componentes do PyQt6-Fluent-Widgets sem o plugin pago. Segue a
mesma convenção das outras telas: uma classe `Ui_MainWindow` com
`setupUi(janela)` que só monta os widgets e guarda referências a eles
como atributos — sem navegação, sem lógica de troca de tela, sem
carregar/salvar usuário logado.

Quem dá vida a estes widgets é main_app_qt.py.

NOTA: os botões da barra usam QPushButton "puro" (não os componentes
Fluent), porque dependem de um QSS bem específico — indicador de aba
ativa via propriedade dinâmica "ativo" e hover vermelho no botão Sair —
que os widgets Fluent não respeitam do mesmo jeito (eles pintam a si
mesmos via código, não só via QSS). O efeito de "crescer no hover" é
aplicado depois, por cima, em main_app_qt.py via
screens.efeitos.instalar_hover_crescimento().
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QPushButton, QStackedWidget, QSizePolicy,
)

from screens.theme import CORES


class Ui_MainWindow:
    """Monta a interface visual da janela principal e expõe os widgets
    como atributos de instância.

    Uso (em main_app_qt.py):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # depois: self.ui.centralwidget, self.ui.stackedWidget,
        # self.ui.bnthome, self.ui.bntvincular, self.ui.btngerenusua,
        # self.ui.btnRegistrarAluno, self.ui.bntMeusFilhos,
        # self.ui.bntconfig, self.ui.bntsair
    """

    def setupUi(self, janela: QMainWindow):
        janela.setWindowTitle("SISPE")
        janela.resize(1047, 644)

        self.centralwidget = QWidget(janela)
        self.centralwidget.setStyleSheet("background: transparent;")
        janela.setCentralWidget(self.centralwidget)

        raiz = QVBoxLayout(self.centralwidget)
        raiz.setSpacing(0)
        raiz.setContentsMargins(0, 0, 0, 0)

        raiz.addWidget(self._montar_topbar())
        raiz.addWidget(self._montar_stack())

    # ------------------------------------------------------------------ #
    def _montar_topbar(self):
        self.TopBar = QFrame()
        self.TopBar.setObjectName("TopBar")
        self.TopBar.setMinimumHeight(64)
        self.TopBar.setMaximumHeight(64)
        self.TopBar.setStyleSheet(f"""
            #TopBar {{
                background: {CORES['branco']};
                border: none;
                border-bottom: 1px solid {CORES['cinza_medio']};
            }}
            QPushButton {{
                color: {CORES['texto_sec']};
                background: transparent;
                border: none;
                border-bottom: 3px solid transparent;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                color: {CORES['azul_escuro']};
                background: #F1F7FB;
            }}
            QPushButton[ativo="true"] {{
                color: {CORES['azul_escuro']};
                background: {CORES['azul_claro']};
                border-bottom: 3px solid {CORES['azul']};
            }}
            #bntsair:hover {{
                color: {CORES['erro']};
                background: #FBEEEC;
            }}
            #labelMarcaTopo {{
                color: {CORES['azul_escuro']};
                font-size: 16px;
                font-weight: 700;
                padding-left: 8px;
            }}
        """)

        linha = QHBoxLayout(self.TopBar)
        linha.setContentsMargins(16, 0, 16, 0)
        linha.setSpacing(4)

        self.labelMarcaTopo = QLabel("🧭 SISPE")
        self.labelMarcaTopo.setObjectName("labelMarcaTopo")
        linha.addWidget(self.labelMarcaTopo)

        linha.addSpacing(28)
        linha.addStretch()

        self.bnthome = self._botao_nav("🏠 Início", largura_max=150)
        self.btnRegistrarAluno = self._botao_nav("🎓 Registrar aluno", largura_max=170)
        self.bntvincular = self._botao_nav("🔗 Vincular", largura_max=150)
        self.btngerenusua = self._botao_nav("👥 Gerenciar usuários", largura_max=210, largura_min=170)
        self.bntMeusFilhos = self._botao_nav("👨‍👩‍👧 Meus Filhos", largura_max=170)
        self.bntconfig = self._botao_nav("⚙️ Configurações", largura_max=170)

        for botao in (
            self.bnthome, self.btnRegistrarAluno, self.bntvincular,
            self.btngerenusua, self.bntMeusFilhos, self.bntconfig,
        ):
            linha.addWidget(botao)

        linha.addStretch()

        self.bntsair = self._botao_nav("🚪 Sair", largura_max=150)
        self.bntsair.setObjectName("bntsair")
        linha.addWidget(self.bntsair)

        return self.TopBar

    @staticmethod
    def _botao_nav(texto, largura_max, largura_min=0):
        botao = QPushButton(texto)
        botao.setMinimumSize(largura_min, 50)
        botao.setMaximumSize(largura_max, 50)
        return botao

    def _montar_stack(self):
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        return self.stackedWidget
