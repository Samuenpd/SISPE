from PyQt6 import uic 
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QMarginsF
from PyQt6.QtGui import QTextDocument, QPageLayout, QPageSize, QPdfWriter
from screens.utils import aplicar_sombra 

class HistoricoRelatoriosScreen(QWidget): 
    def __init__(self, db, main_app): 
        super().__init__() 
        uic.loadUi("uis/historico_relatorios.ui", self) 

        # Sombra suave nos cards
        for card in (self.frameTabela, self.frameDetalhe): 
            aplicar_sombra(card) 

        self.db = db 
        self.main_app = main_app 
        self.aluno_id = None 
        self.nome_aluno = ""
        self._relatorios = [] 

        self.tabelaHistorico.setEditTriggers(self.tabelaHistorico.EditTrigger.NoEditTriggers) 
        self.tabelaHistorico.setSelectionBehavior(self.tabelaHistorico.SelectionBehavior.SelectRows) 
        
        header = self.tabelaHistorico.horizontalHeader() 
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) 
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) 

        # Conexões de eventos
        self.tabelaHistorico.cellClicked.connect(self.mostrar_relatorio) 
        self.btnVoltar.clicked.connect(self.voltar) 
        
        # Conecta o botão de exportar
        if hasattr(self, "btnExportarPDF"):
            self.btnExportarPDF.clicked.connect(self.exportar_para_pdf)

    # ========== MÉTODO DE BLINDAGEM DOS POP-UPS ==========
    def _mostrar_alerta(self, tipo, titulo, texto, botoes=QMessageBox.StandardButton.Ok):
        """Exibe uma caixa de mensagem isolando o visual de qualquer cascata preta."""
        msg = QMessageBox(None) # Janela independente para ignorar a cascata do .ui pai
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

    def carregar(self, aluno_id, nome_aluno): 
        self.aluno_id = aluno_id 
        self.nome_aluno = nome_aluno
        self.labelTitulo.setText(f"<b>Histórico de Relatórios — {nome_aluno}</b>") 
        self._relatorios = self.db.listar_relatorios_aluno(aluno_id) 

        self.tabelaHistorico.setRowCount(len(self._relatorios)) 
        for i, (texto, data) in enumerate(self._relatorios): 
            previa = texto if len(texto) <= 80 else texto[:80].rstrip() + "..." 
            self.tabelaHistorico.setItem(i, 0, QTableWidgetItem(str(data))) 
            self.tabelaHistorico.setItem(i, 1, QTableWidgetItem(previa)) 

        self.textRelatorioCompleto.clear() 
        if self._relatorios: 
            self.tabelaHistorico.selectRow(0) 
            self.mostrar_relatorio(0, 0) 

    def mostrar_relatorio(self, row, _column=0): 
        if row < 0 or row >= len(self._relatorios): 
            return 
        texto, data = self._relatorios[row] 
        self.textRelatorioCompleto.setText(f"📅 {data}\n\n{texto}") 

    def exportar_para_pdf(self):
        """Gera um PDF formatado em alta definição, com fontes grandes e legíveis."""
        if not self._relatorios:
            self._mostrar_alerta(QMessageBox.Icon.Warning, "Aviso", "Não há relatórios para exportar.")
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar Prontuário", f"Prontuario_{self.nome_aluno.replace(' ', '_')}.pdf", "Arquivos PDF (*.pdf)"
        )
        
        if not caminho:
            return  

        # Estrutura HTML com fontes aumentadas e em unidades escaláveis (pt) para impressão
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
                    font-size: 14pt; 
                    color: #5B7285; 
                    margin-bottom: 25px; 
                    background-color: #F5F7FA; 
                    padding: 12px; 
                    border-radius: 6px; 
                }}
                .card {{ 
                    background-color: #FFFFFF; 
                    border-left: 5px solid #5B84A6; 
                    margin-bottom: 20px; 
                    padding: 15px; 
                    border-bottom: 1px solid #E4E9EF; 
                }}
                .data {{ 
                    font-weight: bold; 
                    color: #2F6EA6; 
                    font-size: 13pt; 
                    margin-bottom: 6px; 
                }}
                .texto {{ 
                    font-size: 13pt; 
                    line-height: 1.5; 
                    text-align: justify; 
                }}
            </style>
        </head>
        <body>
            <h1>SISPE — Prontuário Clínico</h1>
            <div class="meta">
                <strong>Aluno(a):</strong> {self.nome_aluno}<br>
                <strong>Total de Registros:</strong> {len(self._relatorios)} relatórios acumulados.
            </div>
        """
        
        for texto, data in self._relatorios:
            texto_formatado = texto.replace('\n', '<br>')
            html += f"""
            <div class="card">
                <div class="data">📅 Registro em: {data}</div>
                <div class="texto">{texto_formatado}</div>
            </div>
            """
        
        html += "</body></html>"

        # 1. Configura o dispositivo de escrita do PDF
        writer = QPdfWriter(caminho)
        
        # Define margens físicas generosas de 20mm diretamente na página do PDF
        from PyQt6.QtCore import QMarginsF
        margens = QMarginsF(20.0, 20.0, 20.0, 20.0)
        layout_pagina = QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4), 
            QPageLayout.Orientation.Portrait, 
            margens
        )
        writer.setPageLayout(layout_pagina)

        # 2. Configura o documento de texto de forma limpa
        documento = QTextDocument()
        
        # Deixamos o Qt gerir a largura de página ideal baseada no layout físico da página
        # Alterámos o CSS para usar pontos ('pt') em vez de pixels ('px') para garantir proporção perfeita
        documento.setHtml(html)

        # 3. Executa a impressão direta para o arquivo PDF
        documento.print(writer)
        
        self._mostrar_alerta(QMessageBox.Icon.Information, "Sucesso", "Prontuário exportado em PDF com sucesso!")

    # ========== CORREÇÃO: RETORNADO MÉTODO DE NAVEGAÇÃO APAGADO ENQUANTO CORRIGÍAMOS O PDF ==========
    def voltar(self): 
        """Retorna o fluxo de telas para a interface de edição do aluno correspondente."""
        self.main_app.voltar_para_editar_aluno()
