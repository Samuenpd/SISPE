from PyQt6 import uic 
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea 
from screens.utils import aplicar_sombra 

class HomeScreen(QWidget): 
    def __init__(self, db): 
        super().__init__() 
        uic.loadUi("uis/home.ui", self) 
        self.db = db 

        # Sombra suave nos cards (profundidade calma, sem exagero) 
        for card in (self.frameSaudacao, self.frameSobre, self.frameEquipe, 
                     self.frameObjetivos, self.frameTeoria, self.frameODS, 
                     self.frameStatAlunos, self.frameStatRelatorios, 
                     self.frameStatPais, self.frameStatUrgentes): 
            aplicar_sombra(card) 

        # Criamos um container normal para o conteúdo rolável
        self.conteudo = QWidget() 
        self.conteudo.setLayout(self.mainLayout) 
        
        # Garante total transparência para herdar o SVG da janela principal
        self.conteudo.setStyleSheet("background: transparent;") 

        # Configuração da Scroll Area
        self.scrollArea = QScrollArea() 
        self.scrollArea.setWidget(self.conteudo) 
        self.scrollArea.setWidgetResizable(True) 
        self.scrollArea.setFrameShape(QScrollArea.Shape.NoFrame) 
        
        # Transparente para o fundo decorativo da MainApp aparecer por baixo
        self.scrollArea.setStyleSheet("background: transparent;") 
        self.scrollArea.viewport().setStyleSheet("background: transparent;") 

        # Layout externo da página que segura a barra de rolagem
        layout_externo = QVBoxLayout(self) 
        layout_externo.setContentsMargins(0, 0, 0, 0) 
        layout_externo.addWidget(self.scrollArea) 

        self.atualizar_dashboard() 

    def atualizar(self, usuario=None): 
        """Atualiza a saudação personalizada (comportamento original, inalterado).""" 
        if usuario: 
            tipo = usuario['tipo'].capitalize() 
            self.labelMensagem.setText(f"Bem-vindo(a), {tipo}!") 
        self.atualizar_dashboard() 

    def atualizar_dashboard(self): 
        """Preenche os cards de estatísticas da tela inicial com números reais.""" 
        cursor = self.db.conn.cursor() 
        
        cursor.execute("SELECT COUNT(*) FROM alunos") 
        total_alunos = cursor.fetchone()[0] 
        
        cursor.execute("SELECT COUNT(*) FROM relatorios") 
        total_relatorios = cursor.fetchone()[0] 
        
        cursor.execute("SELECT COUNT(DISTINCT pai_id) FROM relacao_pai_aluno") 
        total_pais = cursor.fetchone()[0] 
        
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE gravidade='grave'") 
        total_urgentes = cursor.fetchone()[0] 

        self.labelValorAlunos.setText(str(total_alunos)) 
        self.labelValorRelatorios.setText(str(total_relatorios)) 
        self.labelValorPais.setText(str(total_pais)) 
        self.labelValorUrgentes.setText(str(total_urgentes))
