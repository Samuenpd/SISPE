"""
screens/editar_aluno.py
=========================
Lógica da tela de edição de aluno + geração de relatório em PDF.

Este arquivo NÃO constrói nenhum widget diretamente — toda a interface
visual vive em uis/editar_aluno_ui.py (classe Ui_EditarAlunoScreen). Aqui só
ficam: validações, geração do PDF e chamadas ao banco (database.py).
"""

import os

from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import QMarginsF
from PyQt6.QtGui import QTextDocument, QPageLayout, QPageSize, QPdfWriter

from uis.editar_aluno_ui import Ui_EditarAlunoScreen
from screens.utils import gravidade_para_db, gravidade_para_exibir, mostrar_alerta


class EditarAlunoScreen(QWidget):
    def __init__(self, db, main_app):
        super().__init__()
        self.db = db
        self.main_app = main_app
        self.aluno_id = None

        self.ui = Ui_EditarAlunoScreen()
        self.ui.setupUi(self)

        self.ui.btnSalvar.clicked.connect(self.salvar_aluno)
        self.ui.btnSalvarRelatorio.clicked.connect(self.salvar_relatorio)
        self.ui.btnHistorico.clicked.connect(self.abrir_historico)
        self.ui.btnVoltar.clicked.connect(self.voltar)

    # ------------------------------------------------------------------ #
    # API pública — chamada por main_app_qt.py
    # ------------------------------------------------------------------ #
    def carregar(self, aluno_id, nome, sala, serie, gravidade):
        """Popula a tela com os dados do aluno selecionado."""
        self.aluno_id = aluno_id
        self.ui.inputNome.setText(nome)
        self.ui.inputSala.setText(sala)
        self.ui.inputSerie.setText(serie)
        self.ui.comboGravidade.setCurrentText(gravidade_para_exibir(gravidade))
        self.ui.labelTitulo.setText(f"Editando: {nome}")
        self.ui.textNovoRelatorio.clear()
        self.ui.labelStatusPdf.setText("")

    # ------------------------------------------------------------------ #
    def salvar_aluno(self):
        nome = self.ui.inputNome.text().strip()
        sala = self.ui.inputSala.text().strip()
        serie = self.ui.inputSerie.text().strip()
        gravidade = gravidade_para_db(self.ui.comboGravidade.currentText())

        if not nome or not sala or not serie:
            mostrar_alerta(self, QMessageBox.Icon.Warning, "Erro", "Preencha todos os campos")
            return

        self.db.atualizar_aluno(self.aluno_id, nome, sala, serie, gravidade)
        self.ui.labelTitulo.setText(f"Editando: {nome}")
        mostrar_alerta(self, QMessageBox.Icon.Information, "Sucesso", "Informações do aluno atualizadas!")

        if self.main_app.psico:
            self.main_app.psico.atualizar()

    def salvar_relatorio(self):
        """Salva o relatório no banco e gera o PDF automaticamente na pasta
        Documentos/SISPE do usuário (não confundir com o banco de dados do
        app, que agora fica no AppData — ver database.py)."""
        texto = self.ui.textNovoRelatorio.toPlainText().strip()
        if not texto:
            mostrar_alerta(self, QMessageBox.Icon.Warning, "Erro",
                            "Escreva o conteúdo do relatório antes de salvar.")
            return

        usuario_logado = self.main_app.app.usuario_logado
        psicologo_id = usuario_logado["id"] if usuario_logado else None
        psicologo_username = (
            usuario_logado.get("username", "Não identificado") if usuario_logado else "Não identificado"
        )

        # 1. Salva o registro no banco de dados
        self.db.criar_relatorio(self.aluno_id, psicologo_id, texto)

        nome_aluno = self.ui.inputNome.text().strip()
        sala_aluno = self.ui.inputSala.text().strip()
        serie_aluno = self.ui.inputSerie.text().strip()
        gravidade_aluno = self.ui.comboGravidade.currentText()

        # 2. Localiza (ou cria) a pasta Documentos/SISPE do usuário
        try:
            raiz_usuario = os.path.expanduser("~")
            caminhos_possiveis = [
                os.path.join(raiz_usuario, "OneDrive", "Documentos"),
                os.path.join(raiz_usuario, "OneDrive", "Documents"),
                os.path.join(raiz_usuario, "Documentos"),
                os.path.join(raiz_usuario, "Documents"),
            ]
            pasta_documentos = next((c for c in caminhos_possiveis if os.path.exists(c)), None)
            if not pasta_documentos:
                pasta_documentos = os.path.join(raiz_usuario, "Documentos")

            pasta_sispe = os.path.join(pasta_documentos, "SISPE")
            os.makedirs(pasta_sispe, exist_ok=True)

            nome_arquivo = f"Relatorio_{nome_aluno.replace(' ', '_')}.pdf"
            caminho_pdf = os.path.join(pasta_sispe, nome_arquivo)
        except Exception as e:
            mostrar_alerta(self, QMessageBox.Icon.Critical, "Erro",
                            f"Não foi possível criar o diretório automático:\n{str(e)}")
            return

        # 3. Monta o HTML do PDF (texto pré-formatado fora do f-string, para
        # não depender de versão do Python que aceite "\" dentro de {})
        texto_html = texto.replace("\n", "<br>")
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #26343F; margin: 10px; }}
                h1 {{ color: #2F6EA6; border-bottom: 2px solid #5B84A6; padding-bottom: 8px; font-size: 24pt; margin-top: 0px; }}
                .meta {{ font-size: 13pt; color: #5B7285; margin-bottom: 25px; background-color: #F5F7FA; padding: 14px; border-radius: 6px; line-height: 1.5; }}
                .card {{ background-color: #FFFFFF; border-left: 6px solid #2F6EA6; padding: 20px; border-bottom: 1px solid #E4E9EF; }}
                .titulo-sessao {{ font-weight: bold; color: #2F6EA6; font-size: 14pt; margin-bottom: 10px; }}
                .texto {{ font-size: 13pt; line-height: 1.6; text-align: justify; white-space: pre-wrap; }}
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
                <div class="texto">{texto_html}</div>
            </div>
        </body>
        </html>
        """

        # 4. Compila o PDF via QPdfWriter
        documento = QTextDocument()
        documento.setHtml(html)

        writer = QPdfWriter(caminho_pdf)
        margens = QMarginsF(20.0, 20.0, 20.0, 20.0)
        layout_pagina = QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4), QPageLayout.Orientation.Portrait, margens
        )
        writer.setPageLayout(layout_pagina)
        documento.print(writer)

        self.ui.textNovoRelatorio.clear()
        self.ui.labelStatusPdf.setText("✅ Arquivo salvo em: Documentos/SISPE")

        mostrar_alerta(
            self, QMessageBox.Icon.Information, "Sucesso",
            f"Relatório gravado com sucesso!\n\nO PDF foi gerado automaticamente em:\n{caminho_pdf}"
        )

    def abrir_historico(self):
        if self.aluno_id is None:
            return
        self.main_app.abrir_historico(self.aluno_id, self.ui.inputNome.text().strip())

    def voltar(self):
        self.main_app.voltar_para_psico()
