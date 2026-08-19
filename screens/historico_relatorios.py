"""
screens/historico_relatorios.py
=================================
Lógica da tela de histórico de relatórios de um aluno.

Este arquivo NÃO constrói nenhum widget diretamente — toda a interface
visual vive em uis/historico_relatorios_ui.py (classe
Ui_HistoricoRelatoriosScreen). Aqui só ficam: exportação em PDF, navegação
e chamadas ao banco (database.py).
"""

from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QFileDialog, QMessageBox
from PyQt6.QtCore import QMarginsF
from PyQt6.QtGui import QTextDocument, QPageLayout, QPageSize, QPdfWriter

from uis.historico_relatorios_ui import Ui_HistoricoRelatoriosScreen
from screens.utils import mostrar_alerta


class HistoricoRelatoriosScreen(QWidget):
    def __init__(self, db, main_app):
        super().__init__()
        self.db = db
        self.main_app = main_app
        self.aluno_id = None
        self.nome_aluno = ""
        self._relatorios = []

        self.ui = Ui_HistoricoRelatoriosScreen()
        self.ui.setupUi(self)

        self.ui.tabelaHistorico.cellClicked.connect(self.mostrar_relatorio)
        self.ui.btnVoltar.clicked.connect(self.voltar)
        self.ui.btnExportarPDF.clicked.connect(self.exportar_para_pdf)

    # ------------------------------------------------------------------ #
    # API pública — chamada por main_app_qt.py
    # ------------------------------------------------------------------ #
    def carregar(self, aluno_id, nome_aluno):
        self.aluno_id = aluno_id
        self.nome_aluno = nome_aluno
        self.ui.labelTitulo.setText(f"Histórico — {nome_aluno}")
        self._relatorios = self.db.listar_relatorios_aluno(aluno_id)

        tabela = self.ui.tabelaHistorico
        tabela.setRowCount(len(self._relatorios))
        for i, (texto, data) in enumerate(self._relatorios):
            previa = texto if len(texto) <= 80 else texto[:80].rstrip() + "..."
            tabela.setItem(i, 0, QTableWidgetItem(str(data)))
            tabela.setItem(i, 1, QTableWidgetItem(previa))

        self.ui.textRelatorioCompleto.clear()
        if self._relatorios:
            tabela.selectRow(0)
            self.mostrar_relatorio(0, 0)

    # ------------------------------------------------------------------ #
    def mostrar_relatorio(self, row, _column=0):
        if row < 0 or row >= len(self._relatorios):
            return
        texto, data = self._relatorios[row]
        self.ui.textRelatorioCompleto.setText(f"📅 {data}\n\n{texto}")

    def exportar_para_pdf(self):
        """Gera um PDF com todo o histórico de relatórios do aluno."""
        if not self._relatorios:
            mostrar_alerta(self, QMessageBox.Icon.Warning, "Aviso", "Não há relatórios para exportar.")
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar Prontuário", f"Prontuario_{self.nome_aluno.replace(' ', '_')}.pdf",
            "Arquivos PDF (*.pdf)"
        )
        if not caminho:
            return

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #26343F; margin: 10px; }}
                h1 {{ color: #2F6EA6; border-bottom: 2px solid #5B84A6; padding-bottom: 8px; font-size: 24pt; margin-top: 0px; }}
                .meta {{ font-size: 14pt; color: #5B7285; margin-bottom: 25px; background-color: #F5F7FA; padding: 12px; border-radius: 6px; }}
                .card {{ background-color: #FFFFFF; border-left: 5px solid #5B84A6; margin-bottom: 20px; padding: 15px; border-bottom: 1px solid #E4E9EF; }}
                .data {{ font-weight: bold; color: #2F6EA6; font-size: 13pt; margin-bottom: 6px; }}
                .texto {{ font-size: 13pt; line-height: 1.5; text-align: justify; }}
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
            texto_formatado = texto.replace("\n", "<br>")
            html += f"""
            <div class="card">
                <div class="data">📅 Registro em: {data}</div>
                <div class="texto">{texto_formatado}</div>
            </div>
            """

        html += "</body></html>"

        writer = QPdfWriter(caminho)
        margens = QMarginsF(20.0, 20.0, 20.0, 20.0)
        layout_pagina = QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4), QPageLayout.Orientation.Portrait, margens
        )
        writer.setPageLayout(layout_pagina)

        documento = QTextDocument()
        documento.setHtml(html)
        documento.print(writer)

        mostrar_alerta(self, QMessageBox.Icon.Information, "Sucesso", "Prontuário exportado em PDF com sucesso!")

    def voltar(self):
        self.main_app.voltar_para_editar_aluno()
