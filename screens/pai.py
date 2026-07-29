from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QHeaderView


class PaiScreen(QWidget):
    def __init__(self, db, app):
        super().__init__()
        uic.loadUi("uis/pai.ui", self)

        self.db = db
        self.app = app

        # Configuração da tabela de filhos (o widget vem do pai.ui, ajustes aqui)
        self.tabelaFilhos.setColumnCount(2)
        self.tabelaFilhos.setHorizontalHeaderLabels(["ID", "Nome"])
        self.tabelaFilhos.setEditTriggers(self.tabelaFilhos.EditTrigger.NoEditTriggers)
        self.tabelaFilhos.setSelectionBehavior(self.tabelaFilhos.SelectionBehavior.SelectRows)
        header = self.tabelaFilhos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.tabelaFilhos.cellClicked.connect(self.carregar_relatorios)

    def atualizar(self):
        """Recarrega a lista de filhos do pai logado."""
        if not self.app.usuario_logado:
            return

        dados = self.db.alunos_do_pai(self.app.usuario_logado["id"])
        self.tabelaFilhos.setRowCount(len(dados))

        for i, (id_, nome) in enumerate(dados):
            self.tabelaFilhos.setItem(i, 0, QTableWidgetItem(str(id_)))
            self.tabelaFilhos.setItem(i, 1, QTableWidgetItem(nome))

        self.textRelatorios.clear()

    def carregar_relatorios(self, row, _column=0):
        item = self.tabelaFilhos.item(row, 0)
        if not item:
            return
        aluno_id = int(item.text())
        rels = self.db.listar_relatorios_aluno(aluno_id)

        if not rels:
            self.textRelatorios.setText("Nenhum relatório registrado para este aluno ainda.")
            return

        texto = ""
        for conteudo, data in rels:
            texto += f"📅 {data}\n{conteudo}\n\n"

        self.textRelatorios.setText(texto)
