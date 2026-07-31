import os
from PyQt6 import uic 
from PyQt6.QtWidgets import QWidget, QMessageBox 
from PyQt6.QtCore import Qt, QMarginsF 
from PyQt6.QtGui import QTextDocument, QPageLayout, QPageSize, QPdfWriter 
from screens.utils import gravidade_para_db, gravidade_para_exibir 
from screens.utils import aplicar_sombra 

class EditarAlunoScreen(QWidget): 
    def __init__(self, db, main_app): 
        super().__init__() 
        uic.loadUi("uis/editar_aluno.ui", self) 

        # Sombra suave nos cards (profundidade calma, sem exagero) 
        for card in (self.frameInfo, self.frameRelatorio): 
            aplicar_sombra(card) 

        self.db = db 
        self.main_app = main_app 
        self.aluno_id = None 

        self.btnSalvar.clicked.connect(self.salvar_aluno) 
        self.btnSalvarRelatorio.clicked.connect(self.salvar_relatorio) 
        self.btnHistorico.clicked.connect(self.abrir_historico) 
        self.btnVoltar.clicked.connect(self.voltar) 

    # ========== MÉTODO DE BLINDAGEM DOS POP-UPS ==========
    def _mostrar_alerta(self, tipo, titulo, texto):
        """Exibe uma caixa de mensagem isolando o visual de qualquer cascata preta."""
        msg = QMessageBox(None) 
        msg.setIcon(tipo)
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        msg.setStyleSheet("""
            QMessageBox { background-color: #FFFFFF; }
            QLabel { color: #26343F; background-color: transparent; font-size: 14px; }
            QPushButton { background-color: #5B84A6; color: white; border: none; border-radius: 6px; padding: 6px 16px; min-width: 75px; font-weight: 600; }
            QPushButton:hover { background-color: #2F6EA6; }
        """)
        return msg.exec()

    def carregar(self, aluno_id, nome, sala, serie, gravidade): 
        """Popula a tela com os dados do aluno selecionado.""" 
        self.aluno_id = aluno_id 
        self.inputNome.setText(nome) 
        self.inputSala.setText(sala) 
        self.inputSerie.setText(serie) 
        self.comboGravidade.setCurrentText(gravidade_para_exibir(gravidade)) 
        self.labelTitulo.setText(f"<b>Editando: {nome}</b>") 
        self.textNovoRelatorio.clear() 
        self.labelStatusPdf.setText("") 

    def salvar_aluno(self): 
        nome = self.inputNome.text().strip() 
        sala = self.inputSala.text().strip() 
        serie = self.inputSerie.text().strip() 
        gravidade = gravidade_para_db(self.comboGravidade.currentText()) 

        if not nome or not sala or not serie: 
            self._mostrar_alerta(QMessageBox.Icon.Warning, "Erro", "Preencha todos os campos") 
            return 

        self.db.atualizar_aluno(self.aluno_id, nome, sala, serie, gravidade) 
        self.labelTitulo.setText(f"<b>Editando: {nome}</b>") 
        
        self._mostrar_alerta(QMessageBox.Icon.Information, "Sucesso", "Informações do aluno atualizadas!") 
        
        if self.main_app.psico: 
            self.main_app.psico.atualizar() 

    def salvar_relatorio(self): 
        """Salva o relatório no banco e gera o PDF automaticamente na pasta Documentos/SISPE."""
        texto = self.textNovoRelatorio.toPlainText().strip() 
        if not texto: 
            self._mostrar_alerta(QMessageBox.Icon.Warning, "Erro", "Escreva o conteúdo do relatório antes de salvar.") 
            return 

        usuario_logado = self.main_app.app.usuario_logado 
        psicologo_id = usuario_logado["id"] if usuario_logado else None 
        psicologo_username = usuario_logado.get("username", "Não identificado") if usuario_logado else "Não identificado"

        # 1. Salva o registro no banco de dados SQLite
        self.db.criar_relatorio(self.aluno_id, psicologo_id, texto) 

        # Dados estruturados do aluno
        nome_aluno = self.inputNome.text().strip()
        sala_aluno = self.inputSala.text().strip()
        serie_aluno = self.inputSerie.text().strip()
        gravidade_aluno = self.comboGravidade.currentText()

        # 2. SISTEMA DE DIRETÓRIO AUTOMÁTICO (Corrigido sem tags inválidas)
        try:
            raiz_usuario = os.path.expanduser("~")
            
            # Lista de caminhos possíveis para a pasta de Documentos (tentando OneDrive primeiro)
            caminhos_possiveis = [
                os.path.join(raiz_usuario, "OneDrive", "Documentos"),
                os.path.join(raiz_usuario, "OneDrive", "Documents"),
                os.path.join(raiz_usuario, "Documentos"),
                os.path.join(raiz_usuario, "Documents")
            ]
            
            # Procura qual dessas pastas realmente existe no seu Windows
            pasta_documentos = None
            for caminho in caminhos_possiveis:
                if os.path.exists(caminho):
                    pasta_documentos = caminho
                    break
            
            # Se não encontrar nenhuma (caso raro), cria na raiz do usuário por segurança
            if not pasta_documentos:
                pasta_documentos = os.path.join(raiz_usuario, "Documentos")

            # Define a pasta SISPE dentro dos Documentos corretos
            pasta_sispe = os.path.join(pasta_documentos, "SISPE")
            
            # Cria a pasta SISPE se ela ainda não existir
            os.makedirs(pasta_sispe, exist_ok=True)
            
            # Formata o nome do arquivo automaticamente com o nome do aluno
            nome_arquivo = f"Relatorio_{nome_aluno.replace(' ', '_')}.pdf"
            caminho_pdf = os.path.join(pasta_sispe, nome_arquivo)
            
        except Exception as e:
            self._mostrar_alerta(QMessageBox.Icon.Critical, "Erro", f"Não foi possível criar o diretório automático:\n{str(e)}")
            return
        
        # 3. HTML com formatação estável baseada em pontos (pt) para ficar grande e legível
        html = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    color: #26343F; 
                    margin: 10px;
                }}
                h1 {{ 
                    color: #2F6EA6; 
                    border-bottom: 2px solid #5B84A6; 
                    padding-bottom: 8px; 
                    font-size: 24pt; 
                    margin-top: 0px;
                }}
                .meta {{ 
                    font-size: 13pt; 
                    color: #5B7285; 
                    margin-bottom: 25px; 
                    background-color: #F5F7FA; 
                    padding: 14px; 
                    border-radius: 6px; 
                    line-height: 1.5;
                }}
                .card {{ 
                    background-color: #FFFFFF; 
                    border-left: 6px solid #2F6EA6; 
                    padding: 20px; 
                    border-bottom: 1px solid #E4E9EF; 
                }}
                .titulo-sessao {{ 
                    font-weight: bold; 
                    color: #2F6EA6; 
                    font-size: 14pt; 
                    margin-bottom: 10px; 
                }}
                .texto {{ 
                    font-size: 13pt; 
                    line-height: 1.6; 
                    text-align: justify; 
                    white-space: pre-wrap;
                }}
            </style>
        </head>
        <body>
            <h1>SISPE — Registro de Evolução Psicopedagógica</h1>
            <div class="meta">
                <strong>Aluno(a):</strong> {nome_aluno}<br>
                <strong>Turma:</strong> {sala_aluno} | <strong>Série:</strong> {serie_aluno}<br>
                <strong>Status de Gravidade:</strong> {gravidade_aluno}<br>
                <strong>Profissional Responsável:</strong> {psicologo_username}
            </div>
            <div class="card">
                <div class="titulo-sessao">📝 Parecer e Observações Clínicas</div>
                <div class="texto">{texto.replace('\n', '<br>')}</div>
            </div>
        </body>
        </html>
        """

        # 4. Compila o documento físico usando o QPdfWriter do Qt6
        documento = QTextDocument()
        documento.setHtml(html)

        writer = QPdfWriter(caminho_pdf)
        margens = QMarginsF(20.0, 20.0, 20.0, 20.0) 
        layout_pagina = QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4), 
            QPageLayout.Orientation.Portrait, 
            margens
        )
        writer.setPageLayout(layout_pagina)

        documento.print(writer)

        # Atualiza a interface de forma limpa
        self.textNovoRelatorio.clear() 
        if hasattr(self, "labelStatusPdf") and self.labelStatusPdf:
            self.labelStatusPdf.setText("✅ Arquivo salvo em: Documentos/SISPE") 
        
        self._mostrar_alerta(
            QMessageBox.Icon.Information, 
            "Sucesso", 
            f"Relatório gravado com sucesso!\n\nO PDF foi gerado automaticamente em:\n{caminho_pdf}"
        ) 

    def abrir_historico(self): 
        if self.aluno_id is None: 
            return 
        self.main_app.abrir_historico(self.aluno_id, self.inputNome.text().strip()) 

    def voltar(self): 
        self.main_app.voltar_para_psico()
