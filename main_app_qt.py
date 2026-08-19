from PyQt6.QtWidgets import QMainWindow, QSizePolicy
from screens.home import HomeScreen
from screens.psicologo import PsicologoScreen
from screens.admin import AdminScreen
from screens.pai import PaiScreen
from screens.vincular import VincularScreen
from screens.editar_aluno import EditarAlunoScreen
from screens.historico_relatorios import HistoricoRelatoriosScreen
from screens.configuracoes import ConfiguracoesScreen
from screens.efeitos import trocar_tela_com_fade, instalar_hover_crescimento
from screens.fundo import BackgroundWidget
from uis.main_ui import Ui_MainWindow


class MainApp(QMainWindow):  # Herda apenas de QMainWindow
    def __init__(self, db, app):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.usuario_logado = None

        # 1. Instancia o widget de fundo independente passando esta janela principal como pai
        self.fundo = BackgroundWidget(self)

        # 2. Faz o fundo acompanhar e escutar o redimensionamento desta janela automaticamente
        self.installEventFilter(self.fundo)

        self.db = db
        self.app = app

        # Políticas de expansão
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ui.stackedWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # O stackedWidget (índice 1) recebe todo o espaço extra
        self.ui.centralwidget.layout().setStretch(1, 1)

        # Telas
        self.home = HomeScreen(db)
        self.psico = PsicologoScreen(db, app, self)
        self.admin = AdminScreen(db)
        self.pai = PaiScreen(db, app)
        self.vincular = VincularScreen(db)
        self.editar_aluno = EditarAlunoScreen(db, self)
        self.historico = HistoricoRelatoriosScreen(db, self)
        self.configuracoes = ConfiguracoesScreen(db)

        self.ui.stackedWidget.addWidget(self.home)
        self.ui.stackedWidget.addWidget(self.psico)
        self.ui.stackedWidget.addWidget(self.admin)
        self.ui.stackedWidget.addWidget(self.pai)
        self.ui.stackedWidget.addWidget(self.vincular)
        self.ui.stackedWidget.addWidget(self.editar_aluno)
        self.ui.stackedWidget.addWidget(self.historico)
        self.ui.stackedWidget.addWidget(self.configuracoes)

        # ---------- Visual: indicador de item ativo + hover animado na barra lateral ----------
        self._botoes_nav = [
            self.ui.bnthome, self.ui.bntvincular, self.ui.btngerenusua,
            self.ui.btnRegistrarAluno, self.ui.bntMeusFilhos, self.ui.bntconfig,
        ]
        for botao in self._botoes_nav + [self.ui.bntsair]:
            instalar_hover_crescimento(botao, escala=1.06)

        # Conexões da barra
        self.ui.bnthome.clicked.connect(self._ir_para_home)
        self.ui.bntvincular.clicked.connect(self.abrir_vincular)
        self.ui.btngerenusua.clicked.connect(lambda: self._ir_para(self.admin, self.ui.btngerenusua))
        self.ui.btnRegistrarAluno.clicked.connect(lambda: self._ir_para(self.psico, self.ui.btnRegistrarAluno))
        self.ui.bntMeusFilhos.clicked.connect(self.abrir_meus_filhos)
        self.ui.bntconfig.clicked.connect(self.abrir_configuracoes)
        self.ui.bntsair.clicked.connect(self.logout)

    # ---------- Visual: navegação com transição suave + indicador ativo ----------
    def _ir_para(self, tela, botao=None):
        """Navegação que troca o widget atual do stackedWidget com fade-in e realça o botão ativo."""
        trocar_tela_com_fade(self.ui.stackedWidget, tela)
        if botao is not None:
            self._marcar_botao_ativo(botao)

    def _marcar_botao_ativo(self, botao):
        for b in self._botoes_nav:
            b.setProperty("ativo", b is botao)
            b.style().unpolish(b)
            b.style().polish(b)

    # ---------- Navegação entre telas internas ----------
    def _ir_para_home(self):
        self.home.atualizar(self.usuario_logado)
        self._ir_para(self.home, self.ui.bnthome)

    def abrir_vincular(self):
        self.vincular.atualizar()
        self._ir_para(self.vincular, self.ui.bntvincular)

    def abrir_meus_filhos(self):
        self.pai.atualizar()
        self._ir_para(self.pai, self.ui.bntMeusFilhos)

    def abrir_editar_aluno(self, aluno_id, nome, sala, serie, gravidade):
        self.editar_aluno.carregar(aluno_id, nome, sala, serie, gravidade)
        self._ir_para(self.editar_aluno)

    def abrir_historico(self, aluno_id, nome):
        self.historico.carregar(aluno_id, nome)
        self._ir_para(self.historico)

    def voltar_para_psico(self):
        self.psico.atualizar()
        self._ir_para(self.psico, self.ui.btnRegistrarAluno)

    def voltar_para_editar_aluno(self):
        self._ir_para(self.editar_aluno)

    def abrir_configuracoes(self):
        self.configuracoes.carregar(self.usuario_logado)
        self._ir_para(self.configuracoes, self.ui.bntconfig)

    def carregar_usuario(self, user):
        self.usuario_logado = user
        tipo = user["tipo"]
        self.ui.btnRegistrarAluno.hide()
        self.ui.bntvincular.hide()
        self.ui.btngerenusua.hide()
        self.ui.bntMeusFilhos.hide()

        if tipo == "admin":
            self.ui.btngerenusua.show()
            self.ui.bntvincular.show()
            self.admin.atualizar()
        elif tipo == "psicologo":
            self.ui.btnRegistrarAluno.show()
            self.psico.atualizar()
        elif tipo == "pai":
            self.ui.bntMeusFilhos.show()
            self.pai.atualizar()
        self._ir_para_home()

    def logout(self):
        self.app.setCurrentIndex(0)
