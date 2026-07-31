from PyQt6 import uic 
from PyQt6.QtWidgets import QMainWindow, QSizePolicy, QApplication 
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

class MainApp(QMainWindow):  # Herda apenas de QMainWindow
    def __init__(self, db, app):
        super().__init__()
        uic.loadUi("uis/Main.ui", self) 

        # 1. Instancia o widget de fundo independente passando esta janela principal como pai
        self.fundo = BackgroundWidget(self) 
        
        # 2. Faz o fundo acompanhar e escutar o redimensionamento desta janela automaticamente
        self.installEventFilter(self.fundo) 

        # Deixa o central widget transparente para o fundo SVG aparecer por trás
        self.centralwidget.setStyleSheet("background: transparent;") 

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
        self.home = HomeScreen(db) 
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

        # ---------- Visual: indicador de item ativo + hover animado na barra lateral ---------- # 
        self._botoes_nav = [self.bnthome, self.bntvincular, self.btngerenusua, self.btnRegistrarAluno, self.bntconfig] 
        for botao in self._botoes_nav + [self.bntsair]: 
            instalar_hover_crescimento(botao, escala=1.06) 

        # Conexões da barra 
        self.bnthome.clicked.connect(self._ir_para_home) 
        self.bntvincular.clicked.connect(self.abrir_vincular) 
        self.btngerenusua.clicked.connect(lambda: self._ir_para(self.admin, self.btngerenusua)) 
        self.btnRegistrarAluno.clicked.connect(lambda: self._ir_para(self.psico, self.btnRegistrarAluno)) 
        self.bntconfig.clicked.connect(self.abrir_configuracoes) 
        self.bntsair.clicked.connect(self.logout) 

    # ---------- Visual: navegação com transição suave + indicador ativo ---------- 
    def _ir_para(self, tela, botao=None): 
        """Navegação que troca o widget atual do stackedWidget com fade-in e realça o botão ativo."""
        trocar_tela_com_fade(self.stackedWidget, tela) 
        if botao is not None: 
            self._marcar_botao_ativo(botao) 

    def _marcar_botao_ativo(self, botao): 
        for b in self._botoes_nav: 
            b.setProperty("ativo", b is botao) 
            b.style().unpolish(b) 
            b.style().polish(b) 

    # ---------- Navegação entre telas internas ---------- 
    def _ir_para_home(self): 
        self.home.atualizar_dashboard() 
        self._ir_para(self.home, self.bnthome) 

    def abrir_vincular(self): 
        self.vincular.atualizar() 
        self._ir_para(self.vincular, self.bntvincular) 

    def abrir_editar_aluno(self, aluno_id, nome, sala, serie, gravidade): 
        self.editar_aluno.carregar(aluno_id, nome, sala, serie, gravidade) 
        self._ir_para(self.editar_aluno) 

    def abrir_historico(self, aluno_id, nome): 
        self.historico.carregar(aluno_id, nome) 
        self._ir_para(self.historico) 

    def voltar_para_psico(self): 
        self.psico.atualizar() 
        self._ir_para(self.psico, self.btnRegistrarAluno) 

    def voltar_para_editar_aluno(self): 
        self._ir_para(self.editar_aluno) 

    def abrir_configuracoes(self): 
        self.configuracoes.carregar(self.usuario_logado) 
        self._ir_para(self.configuracoes, self.bntconfig) 

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
        self._ir_para_home() 

    def logout(self): 
        self.app.setCurrentIndex(0)
