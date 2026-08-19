"""
screens/psicologo.py
=====================
Lógica da tela de cadastro de alunos (psicólogo).

Este arquivo NÃO constrói nenhum widget diretamente — toda a interface
visual vive em screens/psicologo_ui.py (classe Ui_PsicologoScreen). Aqui só
ficam: conexões de sinal, validações e chamadas ao banco (database.py).
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QWidget

from qfluentwidgets import PushButton

from uis.psicologo_ui import Ui_PsicologoScreen
from screens.utils import gravidade_para_db, gravidade_para_exibir, mostrar_alerta


class PsicologoScreen(QWidget):
    def __init__(self, db, app, main_app):
        super().__init__()
        self.db = db
        self.app = app
        self.main_app = main_app

        self.ui = Ui_PsicologoScreen()
        self.ui.setupUi(self)

        self.ui.btnCadastrar.clicked.connect(self.cadastrar_aluno)
        self.ui.btnLimpar.clicked.connect(self.limpar_tudo)
        self.ui.inputBusca.textChanged.connect(self.filtrar_alunos)
        self.ui.tabelaAlunos.cellDoubleClicked.connect(self.abrir_edicao)

        self.atualizar()

    # ------------------------------------------------------------------ #
    # API pública — chamada por main_app_qt.py
    # ------------------------------------------------------------------ #
    def atualizar(self):
        self.filtrar_alunos()

    # ------------------------------------------------------------------ #
    def filtrar_alunos(self):
        texto = self.ui.inputBusca.text().strip().lower()
        alunos = self.db.listar_alunos()
        if texto:
            alunos = [a for a in alunos if texto in a[1].lower()]

        tabela = self.ui.tabelaAlunos
        tabela.setRowCount(len(alunos))
        for i, (id_, nome, sala, serie, gravidade) in enumerate(alunos):
            tabela.setItem(i, 0, QTableWidgetItem(nome))
            tabela.setItem(i, 1, QTableWidgetItem(sala))
            tabela.setItem(i, 2, QTableWidgetItem(serie))
            tabela.setItem(i, 3, QTableWidgetItem(gravidade_para_exibir(gravidade)))
            tabela.setItem(i, 4, QTableWidgetItem(self._obter_ultima_data_relatorio(id_)))

            btn_excluir = PushButton("Excluir")
            btn_excluir.clicked.connect(lambda checked, aid=id_: self.excluir_aluno(aid))
            tabela.setCellWidget(i, 5, btn_excluir)

            tabela.item(i, 0).setData(Qt.ItemDataRole.UserRole, id_)

    def _obter_ultima_data_relatorio(self, aluno_id):
        relatorios = self.db.listar_relatorios_aluno(aluno_id)
        return relatorios[0][1] if relatorios else "---"

    def cadastrar_aluno(self):
        nome = self.ui.inputNome.text().strip()
        sala = self.ui.inputSala.text().strip()
        serie = self.ui.inputSerie.text().strip()
        gravidade = gravidade_para_db(self.ui.comboGravidade.currentText())

        if not nome or not sala or not serie:
            mostrar_alerta(self, QMessageBox.Icon.Warning, "Erro", "Preencha todos os campos")
            return

        if self.db.aluno_existe(nome, sala, serie):
            mostrar_alerta(self, QMessageBox.Icon.Warning, "Erro", "Aluno já cadastrado")
            return

        self.db.adicionar_aluno(nome, sala, serie, gravidade)
        mostrar_alerta(self, QMessageBox.Icon.Information, "Sucesso", "Aluno cadastrado!")
        self.limpar_campos_cadastro()
        self.atualizar()

    def excluir_aluno(self, aluno_id):
        botoes = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        confirm = mostrar_alerta(
            self, QMessageBox.Icon.Question, "Confirmar",
            "Excluir aluno e todos os relatórios?", botoes
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.db.excluir_aluno(aluno_id)
            self.atualizar()

    def abrir_edicao(self, row, _column):
        item_nome = self.ui.tabelaAlunos.item(row, 0)
        if not item_nome:
            return
        self.abrir_edicao_por_id(item_nome.data(Qt.ItemDataRole.UserRole))

    def abrir_edicao_por_id(self, aluno_id):
        alunos = self.db.listar_alunos()
        aluno = next((a for a in alunos if a[0] == aluno_id), None)
        if not aluno:
            return
        _, nome, sala, serie, gravidade = aluno
        self.main_app.abrir_editar_aluno(aluno_id, nome, sala, serie, gravidade)

    def limpar_campos_cadastro(self):
        self.ui.inputNome.clear()
        self.ui.inputSala.clear()
        self.ui.inputSerie.clear()
        self.ui.comboGravidade.setCurrentIndex(0)

    def limpar_tudo(self):
        self.limpar_campos_cadastro()
        self.ui.inputBusca.clear()
