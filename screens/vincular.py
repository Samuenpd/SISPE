"""
screens/vincular.py
=====================
Lógica da tela de vínculo entre responsável (pai) e aluno.

Este arquivo NÃO constrói nenhum widget diretamente — toda a interface
visual vive em uis/vincular_ui.py (classe Ui_VincularScreen). Aqui só
ficam: conexões de sinal, validações e chamadas ao banco (database.py).
Nenhum SQL cru fica nesta tela — tudo passa por métodos do DatabaseManager.
"""

from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox

from qfluentwidgets import PushButton

from uis.vincular_ui import Ui_VincularScreen
from screens.utils import mostrar_alerta


class VincularScreen(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.ui = Ui_VincularScreen()
        self.ui.setupUi(self)

        self.ui.btnVincular.clicked.connect(self.vincular)

        self.atualizar()

    # ------------------------------------------------------------------ #
    # API pública — chamada por main_app_qt.py
    # ------------------------------------------------------------------ #
    def atualizar(self):
        self.carregar_combos()
        self.carregar_vinculos()

    # ------------------------------------------------------------------ #
    def carregar_combos(self):
        """Popula os comboboxes de pais e alunos disponíveis, preservando
        a seleção atual quando possível (ex: depois de criar um vínculo)."""
        pai_atual = self.ui.comboPai.currentData()
        aluno_atual = self.ui.comboAluno.currentData()

        # IMPORTANTE: o ComboBox do PyQt6-Fluent-Widgets tem a assinatura
        # addItem(text, icon=None, userData=None) — diferente do QComboBox
        # puro. Passar o id como segundo argumento posicional faz ele cair
        # no parâmetro "icon" (e quebrar ao abrir o dropdown). Por isso
        # userData vai sempre por nome aqui.
        self.ui.comboPai.clear()
        for pai_id, username in self.db.listar_pais():
            self.ui.comboPai.addItem(username, userData=pai_id)

        self.ui.comboAluno.clear()
        for aluno_id, nome, sala, serie, gravidade in self.db.listar_alunos():
            self.ui.comboAluno.addItem(f"{nome} ({sala} - {serie})", userData=aluno_id)

        if pai_atual is not None:
            idx = self.ui.comboPai.findData(pai_atual)
            if idx >= 0:
                self.ui.comboPai.setCurrentIndex(idx)
        if aluno_atual is not None:
            idx = self.ui.comboAluno.findData(aluno_atual)
            if idx >= 0:
                self.ui.comboAluno.setCurrentIndex(idx)

    def carregar_vinculos(self):
        vinculos = self.db.listar_vinculos()
        tabela = self.ui.tabelaVinculos
        tabela.setRowCount(len(vinculos))

        for i, (vinculo_id, pai_username, aluno_id, aluno_nome) in enumerate(vinculos):
            tabela.setItem(i, 0, QTableWidgetItem(pai_username))
            tabela.setItem(i, 1, QTableWidgetItem(aluno_nome))

            btn_desvincular = PushButton("Desvincular")
            btn_desvincular.clicked.connect(lambda checked, vid=vinculo_id: self.desvincular(vid))
            tabela.setCellWidget(i, 2, btn_desvincular)

        self.ui.labelInfo.setText(f"🔗 Vínculos ativos: {len(vinculos)}")

    def vincular(self):
        if self.ui.comboPai.count() == 0:
            mostrar_alerta(
                self, QMessageBox.Icon.Warning, "Erro",
                "Nenhum responsável (pai) cadastrado ainda. "
                "Crie um usuário do tipo 'pai' na tela de usuários."
            )
            return
        if self.ui.comboAluno.count() == 0:
            mostrar_alerta(
                self, QMessageBox.Icon.Warning, "Erro",
                "Nenhum aluno cadastrado ainda. "
                "Cadastre um aluno na tela do psicólogo."
            )
            return

        pai_id = self.ui.comboPai.currentData()
        aluno_id = self.ui.comboAluno.currentData()

        if self.db.vinculo_existe(pai_id, aluno_id):
            mostrar_alerta(self, QMessageBox.Icon.Warning, "Erro", "Este vínculo já existe.")
            return

        self.db.vincular_pai(pai_id, aluno_id)
        mostrar_alerta(self, QMessageBox.Icon.Information, "Sucesso", "Vínculo criado com sucesso!")
        self.carregar_vinculos()

    def desvincular(self, vinculo_id):
        botoes = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        confirm = mostrar_alerta(
            self, QMessageBox.Icon.Question, "Confirmar", "Remover este vínculo?", botoes
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.db.desvincular(vinculo_id)
            self.carregar_vinculos()
