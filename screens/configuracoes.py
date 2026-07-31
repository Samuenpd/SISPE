from PyQt6 import uic 
from PyQt6.QtWidgets import ( 
    QWidget, QMessageBox, QTableWidgetItem, QPushButton, QHeaderView, 
    QScrollArea, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QRadioButton
) 
from PyQt6.QtCore import (Qt, QDate, QLocale, QTime) 
from screens.utils import aplicar_sombra 
from PyQt6.QtGui import QTextCharFormat, QColor 

class ConfiguracoesScreen(QWidget): 
    def __init__(self, db): 
        super().__init__() 
        uic.loadUi("uis/configuracoes.ui", self) 

        locale = QLocale(QLocale.Language.Portuguese, QLocale.Country.Brazil) 
        QLocale.setDefault(locale) 
        self.calendarAgenda.setLocale(locale) 
        
        self.db = db 
        self.usuario = None 
        self.editando_compromisso = None 
        self.cor_selecionada = "#5B84A6" # Cor padrão inicial

        # CORREÇÃO DO CALENDÁRIO: Força o fundo branco e fontes limpas
        self.calendarAgenda.setStyleSheet("""
            QCalendarWidget { background-color: #FFFFFF; border-radius: 8px; }
            QCalendarWidget QTableView { background-color: #FFFFFF !important; color: #26343F !important; }
            QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #5B84A6; }
            QCalendarWidget QToolButton { color: white !important; }
            QCalendarWidget QHeaderView::section { background-color: #F1F5F9; color: #5B7285; }
        """)

        # Adiciona a barra de seleção de cores de forma dinâmica no formulário
        self._construir_seletor_de_cores()

        for card in (self.framePerfil, self.frameFilhos, self.frameAgenda): 
            aplicar_sombra(card) 

        self.conteudo = QWidget() 
        self.conteudo.setLayout(self.verticalLayout) 
        self.scrollArea = QScrollArea() 
        self.scrollArea.setWidget(self.conteudo) 
        self.scrollArea.setWidgetResizable(True) 
        self.scrollArea.setFrameShape(QScrollArea.Shape.NoFrame) 
        
        layout = QVBoxLayout(self) 
        layout.setContentsMargins(0, 0, 0, 0) 
        layout.addWidget(self.scrollArea) 

        self.calendarAgenda.selectionChanged.connect(self.carregar_agenda) 
        self.frameNovoCompromisso.hide() 
        self.btnNovoCompromisso.clicked.connect(lambda: self.frameNovoCompromisso.show()) 
        self.btnSalvarCompromisso.clicked.connect(self.adicionar_compromisso) 
        self.btnCancelarCompromisso.clicked.connect(self.cancelar_compromisso) 

    def _construir_seletor_de_cores(self):
        """Cria os botões de seleção de cor dentro do painel de novo compromisso."""
        self.layout_cores = QHBoxLayout()
        self.layout_cores.setSpacing(12)
        
        # Paleta acolhedora para os cards de compromisso
        self.lista_cores = [
            ("#5B84A6", "Azul"),
            ("#E0A458", "Laranja"),
            ("#D9736C", "Vermelho"),
            ("#4FA37B", "Verde"),
            ("#7D74B3", "Roxo")
        ]
        
        self.botoes_cor = {}
        for hex_color, nome in self.lista_cores:
            btn = QRadioButton()
            btn.setToolTip(nome)
            btn.setStyleSheet(f"""
                QRadioButton::indicator {{
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    background-color: {hex_color};
                    border: 2px solid transparent;
                }}
                QRadioButton::indicator:checked {{
                    border: 2px solid #26343F;
                }}
            """)
            btn.clicked.connect(lambda checked, c=hex_color: self._mudar_cor_ativa(c))
            self.layout_cores.addWidget(btn)
            self.botoes_cor[hex_color] = btn
            
        # Marca o primeiro botão (azul) como padrão
        self.botoes_cor["#5B84A6"].setChecked(True)
        
        # Injeta o layout de cores logo acima dos botões de Salvar/Cancelar
        # Procurando o layout do formulário
        self.layoutNovoCompromisso.insertLayout(3, self.layout_cores)

    def _mudar_cor_ativa(self, cor_hex):
        self.cor_selecionada = cor_hex

    def _mostrar_alerta(self, tipo, titulo, texto, botoes=QMessageBox.StandardButton.Ok):
        msg = QMessageBox(self)
        msg.setIcon(tipo)
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        msg.setStandardButtons(botoes)
        msg.setStyleSheet("""
            QMessageBox { background-color: #FFFFFF; }
            QLabel { color: #26343F; background-color: transparent; font-size: 14px; }
            QPushButton { background-color: #5B84A6; color: white; border: none; border-radius: 6px; padding: 6px 16px; min-width: 75px; font-weight: 600; }
            QPushButton:hover { background-color: #2F6EA6; }
        """)
        return msg.exec()

    def criar_card(self, id_, titulo, hora, cor, descricao): 
        card = QFrame() 
        card.setStyleSheet(f"QFrame {{ background: #FFFFFF; border-left: 8px solid {cor}; border-radius: 10px; }}") 
        
        layout = QVBoxLayout(card) 
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        lblHora = QLabel(hora) 
        lblHora.setStyleSheet("color: #5B7285; font-size: 12px; font-weight: 600;")
        
        lblTitulo = QLabel(titulo) 
        lblTitulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #2E3A46;") 
        
        lblDescricao = QLabel(descricao) 
        lblDescricao.setStyleSheet("color: #7C93A3; font-size: 13px;")
        
        layout.addWidget(lblHora) 
        layout.addWidget(lblTitulo) 
        layout.addWidget(lblDescricao) 
        
        botoes = QHBoxLayout() 
        botoes.setContentsMargins(0, 8, 0, 0)
        
        editar = QPushButton("Editar") 
        excluir = QPushButton("Excluir") 
        
        estilo_bnt = "padding: 4px 12px; min-height: 28px; font-size: 12px;"
        editar.setStyleSheet(estilo_bnt)
        excluir.setStyleSheet(estilo_bnt)
        
        excluir.clicked.connect(lambda: self.excluir_compromisso(id_)) 
        editar.clicked.connect(lambda id_=id_, t=titulo, h=hora, d=descricao: self.editar_compromisso(id_, t, h, d)) 
        
        botoes.addStretch() 
        botoes.addWidget(editar) 
        botoes.addWidget(excluir) 
        layout.addLayout(botoes) 
        return card 

    def carregar(self, usuario): 
        self.usuario = usuario 
        self.carregar_perfil() 
        self.carregar_tela() 
        self.frameNovoCompromisso.hide() 

    def carregar_perfil(self): 
        dados = self.db.obter_usuario(self.usuario["id"]) 
        self.labelUsername.setText(dados["username"]) 
        self.labelTipo.setText(dados["tipo"].capitalize()) 
        self.labelDataCriacao.setText(f"Membro desde {dados['data_criacao']}") 

    def carregar_tela(self): 
        tipo = self.usuario["tipo"] 
        self.frameAgenda.show() 
        self.frameFilhos.show() 
        if tipo == "pai": 
            self.frameAgenda.hide() 
        elif tipo == "psicologo": 
            self.frameFilhos.hide() 
            self.carregar_agenda() 
        else: 
            self.frameAgenda.hide() 
            self.frameFilhos.hide() 

    def atualizar_calendario(self): 
        formato = QTextCharFormat() 
        inicio = QDate(2000, 1, 1) 
        fim = QDate(2100, 12, 31) 
        data = inicio 
        while data <= fim: 
            self.calendarAgenda.setDateTextFormat(data, formato) 
            data = data.addDays(1) 

        cursor = self.db.conn.cursor() 
        cursor.execute("SELECT DISTINCT data FROM compromissos WHERE psicologo_id=?", (self.usuario["id"],)) 
        
        formato = QTextCharFormat() 
        formato.setBackground(QColor("#5B84A6")) 
        formato.setForeground(QColor("white")) 
        
        for (data_str,) in cursor.fetchall(): 
            try:
                dia, mes, ano = map(int, data_str.split("/")) 
                self.calendarAgenda.setDateTextFormat(QDate(ano, mes, dia), formato) 
            except Exception:
                pass

    def carregar_agenda(self): 
        locale = QLocale(QLocale.Language.Portuguese, QLocale.Country.Brazil) 
        data = self.calendarAgenda.selectedDate().toString("dd/MM/yyyy") 
        self.labelDia.setText(locale.toString(self.calendarAgenda.selectedDate(), "dddd, dd 'de' MMMM 'de' yyyy")) 
        
        compromissos = self.db.compromissos_por_data(self.usuario["id"], data) 
        
        while self.layoutCompromissos.count(): 
            item = self.layoutCompromissos.takeAt(0) 
            if item.widget(): 
                item.widget().deleteLater() 
                
        for id_, titulo, hora, cor, descricao in compromissos: 
            card = self.criar_card(id_, titulo, hora, cor, descricao) 
            self.layoutCompromissos.addWidget(card) 
            
        self.layoutCompromissos.addStretch() 
        self.atualizar_calendario() 

    def adicionar_compromisso(self): 
        titulo = self.inputTitulo.text().strip() 
        if not titulo: 
            self._mostrar_alerta(QMessageBox.Icon.Warning, "Erro", "Informe um título.")
            return 
            
        data = self.calendarAgenda.selectedDate().toString("dd/MM/yyyy") 
        hora = self.inputHora.time().toString("HH:mm") 
        descricao = self.inputDescricao.text().strip() 
        
        # CORREÇÃO: Usa a cor armazenada pelo clique do usuário
        cor = self.cor_selecionada 
        
        if self.editando_compromisso is not None: 
            self.db.atualizar_compromisso(self.editando_compromisso, titulo, data, hora, cor, descricao) 
            self.editando_compromisso = None 
            try: self.btnSalvarCompromisso.setText("Salvar") 
            except Exception: pass 
        else: 
            self.db.criar_compromisso(self.usuario["id"], titulo, data, hora, cor, descricao) 
            
        self.inputTitulo.clear() 
        self.inputDescricao.clear() 
        self.frameNovoCompromisso.hide() 
        self.carregar_agenda()
        self.atualizar_calendario()

    def excluir_compromisso(self, compromisso_id): 
        botoes = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        confirm = self._mostrar_alerta(QMessageBox.Icon.Question, "Confirmar", "Excluir compromisso?", botoes)
        if confirm == QMessageBox.StandardButton.Yes: 
            self.db.excluir_compromisso(compromisso_id) 
            self.carregar_agenda() 
            self.atualizar_calendario() 

    def editar_compromisso(self, compromisso_id, titulo, hora, descricao): 
        try: self.inputTitulo.setText(titulo) 
        except Exception: pass 
        
        t = QTime.fromString(hora, "HH:mm") 
        if t.isValid(): 
            try: self.inputHora.setTime(t) 
            except Exception: pass 
            
        try: self.inputDescricao.setText(descricao) 
        except Exception: pass 
        
        self.editando_compromisso = compromisso_id 
        try: self.btnSalvarCompromisso.setText("Atualizar") 
        except Exception: pass 
        self.frameNovoCompromisso.show() 

    def cancelar_compromisso(self): 
        try: 
            self.inputTitulo.clear() 
            self.inputDescricao.clear() 
        except Exception: pass 
        self.editando_compromisso = None 
        try: self.btnSalvarCompromisso.setText("Salvar") 
        except Exception: pass 
        self.frameNovoCompromisso.hide()
