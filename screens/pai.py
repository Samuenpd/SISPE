"""
screens/pai.py
================
Lógica da tela do responsável (pai/mãe) — "Meus Filhos".

Este arquivo NÃO constrói nenhum widget diretamente — toda a interface
visual vive em uis/pai_ui.py (classe Ui_PaiScreen). Aqui só ficam: carregar
os alunos vinculados a este responsável e os relatórios do aluno
selecionado, via database.py.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QTableWidgetItem

from uis.pai_ui import Ui_PaiScreen


class PaiScreen(QWidget):
    def __init__(self, db, app):
        super().__init__()
        self.db = db
        self.app = app

        self.ui = Ui_PaiScreen()
        self.ui.setupUi(self)

        self.ui.tabelaFilhos.cellClicked.connect(self.carregar_relatorios)

    # ------------------------------------------------------------------ #
    # API pública — chamada por main_app_qt.py
    # ------------------------------------------------------------------ #
    def atualizar(self):
        """Recarrega a lista de filhos do pai logado."""
        if not self.app.usuario_logado:
            return

        dados = self.db.alunos_do_pai(self.app.usuario_logado["id"])

        tabela = self.ui.tabelaFilhos
        tabela.setRowCount(len(dados))
        for i, (id_, nome, sala, serie) in enumerate(dados):
            tabela.setItem(i, 0, QTableWidgetItem(nome))
            tabela.setItem(i, 1, QTableWidgetItem(sala))
            tabela.setItem(i, 2, QTableWidgetItem(serie))
            tabela.item(i, 0).setData(Qt.ItemDataRole.UserRole, id_)

        self.ui.labelSemFilhos.setVisible(len(dados) == 0)
        self.ui.tabelaFilhos.setVisible(len(dados) > 0)
        self.ui.textRelatorios.clear()

    # ------------------------------------------------------------------ #
    def carregar_relatorios(self, row, _column=0):
        item = self.ui.tabelaFilhos.item(row, 0)
        if not item:
            return

        aluno_id = item.data(Qt.ItemDataRole.UserRole)
        rels = self.db.listar_relatorios_aluno(aluno_id)

        if not rels:
            self.ui.textRelatorios.setText("Nenhum relatório registrado para este aluno ainda.")
            return

        texto = ""
        for conteudo, data in rels:
            texto += f"📅 {data}\n{conteudo}\n\n"

        self.ui.textRelatorios.setText(texto)
