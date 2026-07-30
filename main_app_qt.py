from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QSizePolicy
from screens.home import HomeScreen
from screens.psicologo import PsicologoScreen
from screens.admin import AdminScreen
from screens.pai import PaiScreen
from screens.vincular import VincularScreen
from screens.editar_aluno import EditarAlunoScreen
from screens.historico_relatorios import HistoricoRelatoriosScreen
from screens.configuracoes import ConfiguracoesScreen

class MainApp(QMainWindow):
    def __init__(self, db, app):
        super().__init__()
        uic.loadUi("uis/Main.ui", self)

        # Remove páginas placeholder
        while self.stackedWidget.count():
            widget = self.stackedWidget.widget(0)
            self.stackedWidget.removeWidget(widget)

        self.db = db
        self.app = app

        # Políticas de expansão
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.stackedWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # O stackedWidget (índice 1) recebe todo o espaço extra
        self.centralwidget.layout().setStretch(1, 1)

        # Telas
        self.home = HomeScreen()
        self.psico = PsicologoScreen(db, app, self)
        self.admin = AdminScreen(db)
        self.pai = PaiScreen(db, app)
        self.vincular = VincularScreen(db)
        self.editar_aluno = EditarAlunoScreen(db, self)
        self.historico = HistoricoRelatoriosScreen(db, self)
        self.configuracoes = ConfiguracoesScreen(db)
        self.stackedWidget.addWidget(self.home)
        self.stackedWidget.addWidget(self.psico)
        self.stackedWidget.addWidget(self.admin)
        self.stackedWidget.addWidget(self.pai)
        self.stackedWidget.addWidget(self.vincular)
        self.stackedWidget.addWidget(self.editar_aluno)
        self.stackedWidget.addWidget(self.historico)
        self.stackedWidget.addWidget(self.configuracoes)
        # Conexões da barra
        self.bnthome.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.home))
        self.bntvincular.clicked.connect(self.abrir_vincular)
        self.btngerenusua.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.admin))
        self.btnRegistrarAluno.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.psico))
        self.bntconfig.clicked.connect(self.abrir_configuracoes)
        self.bntsair.clicked.connect(self.logout)

    # ---------- Navegação entre telas internas ----------
    def abrir_vincular(self):
        self.vincular.atualizar()
        self.stackedWidget.setCurrentWidget(self.vincular)

    def abrir_editar_aluno(self, aluno_id, nome, sala, serie, gravidade):
        self.editar_aluno.carregar(aluno_id, nome, sala, serie, gravidade)
        self.stackedWidget.setCurrentWidget(self.editar_aluno)

    def abrir_historico(self, aluno_id, nome):
        self.historico.carregar(aluno_id, nome)
        self.stackedWidget.setCurrentWidget(self.historico)

    def voltar_para_psico(self):
        self.psico.atualizar()
        self.stackedWidget.setCurrentWidget(self.psico)

    def voltar_para_editar_aluno(self):
        self.stackedWidget.setCurrentWidget(self.editar_aluno)

    def abrir_configuracoes(self):
        self.configuracoes.carregar(self.usuario_logado)
        self.stackedWidget.setCurrentWidget(self.configuracoes)

    def carregar_usuario(self, user):
        self.usuario_logado = user
        tipo = user["tipo"]
        self.btnRegistrarAluno.hide()
        self.bntvincular.hide()
        self.btngerenusua.hide()
        if tipo == "admin":
            self.btngerenusua.show()
            self.bntvincular.show()
            self.admin.atualizar()
        elif tipo == "psicologo":
            self.btnRegistrarAluno.show()
            self.psico.atualizar()
        elif tipo == "pai":
            self.pai.atualizar()
        self.stackedWidget.setCurrentWidget(self.home)

    def logout(self):
        self.app.setCurrentIndex(0)
