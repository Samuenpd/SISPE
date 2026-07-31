from PyQt6 import uic 
from PyQt6.QtWidgets import QMainWindow, QMessageBox 
from screens.utils import aplicar_sombra 
from screens.fundo import BackgroundWidget 
from screens.efeitos import instalar_hover_crescimento 

class LoginScreen(QMainWindow):  # Corrigido: Herda apenas de QMainWindow
    def __init__(self, app, db):
        super().__init__()
        uic.loadUi("uis/login.ui", self) 

        # 1. Cria o widget de fundo independente passando esta janela como pai
        self.fundo = BackgroundWidget(self)
        
        # 2. Faz o fundo acompanhar automaticamente o redimensionamento da janela
        self.installEventFilter(self.fundo)

        # Deixa o central widget transparente para o fundo SVG aparecer
        self.centralwidget.setStyleSheet("background: transparent;") 

        # Sombra suave no card de login (profundidade calma, sem exagero) 
        aplicar_sombra(self.cardLogin, blur=36, y_offset=10, alpha=22) 

        # Botão de entrar cresce levemente ao passar o mouse 
        instalar_hover_crescimento(self.bntContinuar, escala=1.05) 

        self.app = app 
        self.db = db 
        
        self.bntContinuar.clicked.connect(self.login) 
        self.btnVerSenha.clicked.connect(self.toggle_senha) 
        self.btnVerSenha.setText("🔒")  # Corrigido: Texto decodificado para emoji legível
        self.senha_visivel = False 

    def login(self): 
        usuario = self.inputUsuario.text().strip() 
        senha = self.InputSenha.text().strip() 
        
        # validação básica 
        if not usuario or not senha: 
            QMessageBox.warning(self, "Erro", "Preencha todos os campos") 
            return 
            
        result = self.db.login(usuario, senha) 
        if result: 
            # salva usuário logado 
            self.app.usuario_logado = result 
            # manda pro sistema principal 
            self.app.main_app.carregar_usuario(result) 
            # troca tela 
            self.app.setCurrentIndex(1) 
            # limpa campos depois do login 
            self.inputUsuario.clear() 
            self.InputSenha.clear() 
        else: 
            QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos") 

    def toggle_senha(self): 
        if self.senha_visivel: 
            self.InputSenha.setEchoMode(self.InputSenha.EchoMode.Password) 
            self.btnVerSenha.setText("🔒")  # Corrigido: Texto decodificado
        else: 
            self.InputSenha.setEchoMode(self.InputSenha.EchoMode.Normal) 
            self.btnVerSenha.setText("🔓")  # Corrigido: Texto decodificado
        self.senha_visivel = not self.senha_visivel
