from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QMessageBox


class EditarAlunoScreen(QDialog):
    def __init__(self, db, parent, aluno_id, nome, sala, serie, gravidade):
        super().__init__()
        # Carrega a interface da pasta "uis"
        uic.loadUi("uis/editar_aluno.ui", self)

        self.db = db
        self.parent = parent
        self.aluno_id = aluno_id

        # Preenche os campos com os dados atuais
        self.inputNome.setText(nome)
        self.inputSala.setText(sala)
        self.inputSerie.setText(serie)
        self.comboGravidade.setCurrentText(gravidade)

        # Conecta os botões
        self.btnSalvar.clicked.connect(self.salvar)
        self.btnRelatorios.clicked.connect(self.abrir_relatorios)

    def salvar(self):
        nome = self.inputNome.text().strip()
        sala = self.inputSala.text().strip()
        serie = self.inputSerie.text().strip()
        gravidade = self.comboGravidade.currentText()

        if not nome or not sala or not serie:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos")
            return

        self.db.atualizar_aluno(self.aluno_id, nome, sala, serie, gravidade)
        QMessageBox.information(self, "Sucesso", "Aluno atualizado com sucesso!")
        self.parent.atualizar()  # Atualiza a lista na tela do psicólogo
        self.close()

    def abrir_relatorios(self):
        from screens.relatorio import RelatorioScreen

        # O nome do aluno está no campo inputNome
        nome = self.inputNome.text()

        self.rel = RelatorioScreen(
            self.db,
            self.parent.app,      # Acesso ao app através da tela pai (psicologo)
            self.aluno_id,
            nome
        )
        self.rel.exec()