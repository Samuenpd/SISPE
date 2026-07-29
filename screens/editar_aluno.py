from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QMessageBox

from screens.utils import gravidade_para_db, gravidade_para_exibir, gerar_pdf_relatorio
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
            QMessageBox.warning(self, "Erro", "Preencha todos os campos")
            return

        self.db.atualizar_aluno(self.aluno_id, nome, sala, serie, gravidade)
        self.labelTitulo.setText(f"<b>Editando: {nome}</b>")
        QMessageBox.information(self, "Sucesso", "Informações do aluno atualizadas!")

        if self.main_app.psico:
            self.main_app.psico.atualizar()

    def salvar_relatorio(self):
        texto = self.textNovoRelatorio.toPlainText().strip()
        if not texto:
            QMessageBox.warning(self, "Erro", "Escreva o conteúdo do relatório antes de salvar.")
            return

        usuario_logado = self.main_app.app.usuario_logado
        psicologo_id = usuario_logado["id"] if usuario_logado else None

        # Salva no banco
        self.db.criar_relatorio(self.aluno_id, psicologo_id, texto)

        # Gera o PDF do relatório mais recente
        aluno_info = {
            "nome": self.inputNome.text().strip(),
            "sala": self.inputSala.text().strip(),
            "serie": self.inputSerie.text().strip(),
            "gravidade": self.comboGravidade.currentText(),
        }
        psicologo_username = usuario_logado.get("username") if usuario_logado else None
        caminho_pdf = gerar_pdf_relatorio(aluno_info, texto, psicologo_username)

        self.textNovoRelatorio.clear()
        self.labelStatusPdf.setText(f"✅ PDF salvo em: {caminho_pdf}")
        QMessageBox.information(
            self, "Sucesso",
            f"Relatório salvo!\n\nPDF gerado em:\n{caminho_pdf}"
        )

    def abrir_historico(self):
        if self.aluno_id is None:
            return
        self.main_app.abrir_historico(self.aluno_id, self.inputNome.text().strip())

    def voltar(self):
        self.main_app.voltar_para_psico()
