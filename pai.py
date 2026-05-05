from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QTextEdit
)

class PaiScreen(QWidget):
    def __init__(self, db, app):
        super().__init__()
        self.db = db
        self.app = app

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Nome"])
        self.table.cellClicked.connect(self.carregar_relatorios)

        self.relatorios = QTextEdit()
        self.relatorios.setReadOnly(True)

        layout.addWidget(self.table)
        layout.addWidget(self.relatorios)

        self.setLayout(layout)

    def atualizar(self):
        if not self.app.usuario_logado:
            return

        dados = self.db.alunos_do_pai(self.app.usuario_logado["id"])
        self.table.setRowCount(len(dados))

        for i, (id_, nome) in enumerate(dados):
            self.table.setItem(i, 0, QTableWidgetItem(str(id_)))
            self.table.setItem(i, 1, QTableWidgetItem(nome))

    def load(self):
        dados = self.db.alunos_do_pai(self.app.usuario_logado["id"])
        self.table.setRowCount(len(dados))

        for i, (id_, nome) in enumerate(dados):
            self.table.setItem(i, 0, QTableWidgetItem(str(id_)))
            self.table.setItem(i, 1, QTableWidgetItem(nome))

    def carregar_relatorios(self, row):
        aluno_id = int(self.table.item(row, 0).text())
        rels = self.db.listar_relatorios_aluno(aluno_id)

        texto = ""
        for r in rels:
            texto += f"{r[1]}\\n{r[0]}\\n\\n"

        self.relatorios.setText(texto)