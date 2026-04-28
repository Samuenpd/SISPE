from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QPushButton, QMessageBox, QHeaderView,
    QSizePolicy, QScrollArea, QVBoxLayout
)
from PyQt6.QtCore import Qt
from screens.editar_aluno import EditarAlunoScreen


class PsicologoScreen(QWidget):
    def __init__(self, db, app):
        super().__init__()
        uic.loadUi("uis/psicologo.ui", self)

        self.db = db
        self.app = app

        self.conteudo = QWidget()
        self.conteudo.setLayout(self.verticalLayout)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.conteudo)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QScrollArea.Shape.NoFrame)

        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(0, 0, 0, 0)
        layout_externo.addWidget(self.scrollArea)

        self.tabelaAlunos.setColumnCount(6)
        self.tabelaAlunos.setHorizontalHeaderLabels(
            ["Nome", "Sala", "Série", "Gravidade", "Data", "Ações"]
        )
        self.tabelaAlunos.setEditTriggers(self.tabelaAlunos.EditTrigger.NoEditTriggers)
        self.tabelaAlunos.setSelectionBehavior(self.tabelaAlunos.SelectionBehavior.SelectRows)

        self.tabelaAlunos.verticalHeader().setDefaultSectionSize(55)

        self.tabelaAlunos.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabelaAlunos.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.tabelaAlunos.setSizeAdjustPolicy(
            self.tabelaAlunos.SizeAdjustPolicy.AdjustToContents
        )

        header = self.tabelaAlunos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, 6):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        self.btnCadastrar.clicked.connect(self.cadastrar_aluno)
        self.btnLimpar.clicked.connect(self.limpar_tudo)
        self.inputBusca.textChanged.connect(self.filtrar_alunos)
        self.tabelaAlunos.cellDoubleClicked.connect(self.abrir_relatorio)

        self.frameTabela.setMinimumHeight(800)
        self.verticalLayout.setStretch(2, 1)

        self.atualizar()

    # ========== MÉTODOS (inalterados, exceto por pequenas adaptações) ==========
    def atualizar(self):
        self.filtrar_alunos()

    def filtrar_alunos(self):
        texto = self.inputBusca.text().strip().lower()
        alunos = self.db.listar_alunos()
        if texto:
            alunos = [a for a in alunos if texto in a[1].lower()]

        self.tabelaAlunos.setRowCount(len(alunos))
        for i, (id_, nome, sala, serie, gravidade) in enumerate(alunos):
            self.tabelaAlunos.setItem(i, 0, QTableWidgetItem(nome))
            self.tabelaAlunos.setItem(i, 1, QTableWidgetItem(sala))
            self.tabelaAlunos.setItem(i, 2, QTableWidgetItem(serie))
            self.tabelaAlunos.setItem(i, 3, QTableWidgetItem(gravidade))

            ultima_data = self.obter_ultima_data_relatorio(id_)
            self.tabelaAlunos.setItem(i, 4, QTableWidgetItem(ultima_data))

            btn_excluir = QPushButton("Excluir")
            btn_excluir.clicked.connect(lambda checked, id=id_: self.excluir_aluno(id))
            self.tabelaAlunos.setCellWidget(i, 5, btn_excluir)

            self.tabelaAlunos.item(i, 0).setData(Qt.ItemDataRole.UserRole, id_)

    def obter_ultima_data_relatorio(self, aluno_id):
        relatorios = self.db.listar_relatorios_aluno(aluno_id)
        if relatorios:
            return relatorios[0][1]  # data
        return "---"

    def cadastrar_aluno(self):
        nome = self.inputNome.text().strip()
        sala = self.inputSala.text().strip()
        serie = self.inputSerie.text().strip()
        gravidade = self.comboGravidade.currentText().split()[-1].lower()

        if not nome or not sala or not serie:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos")
            return
        if self.db.aluno_existe(nome, sala, serie):
            QMessageBox.warning(self, "Erro", "Aluno já cadastrado")
            return

        self.db.adicionar_aluno(nome, sala, serie, gravidade)
        QMessageBox.information(self, "Sucesso", "Aluno cadastrado!")
        self.limpar_campos_cadastro()
        self.atualizar()

    def excluir_aluno(self, aluno_id):
        confirm = QMessageBox.question(
            self, "Confirmar", "Excluir aluno e todos os relatórios?"
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.db.excluir_aluno(aluno_id)
            self.atualizar()

    def abrir_relatorio(self, row, column):
        item_nome = self.tabelaAlunos.item(row, 0)
        if not item_nome:
            return
        aluno_id = item_nome.data(Qt.ItemDataRole.UserRole)
        nome = item_nome.text()
        sala = self.tabelaAlunos.item(row, 1).text()
        serie = self.tabelaAlunos.item(row, 2).text()
        gravidade = self.tabelaAlunos.item(row, 3).text()

        self.janela = EditarAlunoScreen(
            self.db, self, aluno_id, nome, sala, serie, gravidade
        )
        self.janela.show()

    def limpar_campos_cadastro(self):
        self.inputNome.clear()
        self.inputSala.clear()
        self.inputSerie.clear()
        self.comboGravidade.setCurrentIndex(0)

    def limpar_tudo(self):
        self.limpar_campos_cadastro()
        self.inputBusca.clear()