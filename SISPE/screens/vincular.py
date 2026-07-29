from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QPushButton, QMessageBox, QHeaderView,
    QScrollArea, QVBoxLayout
)
from PyQt6.QtCore import Qt
from screens.utils import aplicar_sombra


class VincularScreen(QWidget):
    def __init__(self, db):
        super().__init__()
        uic.loadUi("uis/vincular.ui", self)

        # Sombra suave nos cards (profundidade calma, sem exagero)
        for card in (self.frameStats, self.frameVincular, self.frameTabela):
            aplicar_sombra(card)

        self.db = db

        # ========== SCROLL AREA (mesmo padrão das outras telas) ==========
        self.conteudo = QWidget()
        self.conteudo.setLayout(self.verticalLayout)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.conteudo)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QScrollArea.Shape.NoFrame)

        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(0, 0, 0, 0)
        layout_externo.addWidget(self.scrollArea)

        # ========== CONFIGURAÇÃO DA TABELA ==========
        self.tabelaVinculos.setColumnCount(3)
        self.tabelaVinculos.setHorizontalHeaderLabels(["Responsável", "Aluno", "Ações"])
        self.tabelaVinculos.setEditTriggers(self.tabelaVinculos.EditTrigger.NoEditTriggers)
        self.tabelaVinculos.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabelaVinculos.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tabelaVinculos.verticalHeader().setDefaultSectionSize(55)

        header = self.tabelaVinculos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        self.verticalLayout.setStretch(3, 1)
        self.frameTabela.setMinimumHeight(500)

        # Conexões
        self.btnVincular.clicked.connect(self.vincular)

        self.atualizar()

    def atualizar(self):
        self.carregar_combos()
        self.carregar_vinculos()

    def carregar_combos(self):
        """Popula os comboboxes de pais e alunos disponíveis."""
        pai_atual = self.comboPai.currentData()
        aluno_atual = self.comboAluno.currentData()

        self.comboPai.clear()
        for pai_id, username in self.db.listar_pais():
            self.comboPai.addItem(username, pai_id)

        self.comboAluno.clear()
        for aluno_id, nome, sala, serie, gravidade in self.db.listar_alunos():
            self.comboAluno.addItem(f"{nome} ({sala} - {serie})", aluno_id)

        # Restaura seleção anterior, se ainda existir
        if pai_atual is not None:
            idx = self.comboPai.findData(pai_atual)
            if idx >= 0:
                self.comboPai.setCurrentIndex(idx)
        if aluno_atual is not None:
            idx = self.comboAluno.findData(aluno_atual)
            if idx >= 0:
                self.comboAluno.setCurrentIndex(idx)

    def carregar_vinculos(self):
        vinculos = self.db.listar_vinculos()
        self.tabelaVinculos.setRowCount(len(vinculos))

        for i, (vinculo_id, pai_username, aluno_id, aluno_nome) in enumerate(vinculos):
            self.tabelaVinculos.setItem(i, 0, QTableWidgetItem(pai_username))
            self.tabelaVinculos.setItem(i, 1, QTableWidgetItem(aluno_nome))

            btn_desvincular = QPushButton("Desvincular")
            btn_desvincular.clicked.connect(lambda checked, vid=vinculo_id: self.desvincular(vid))
            self.tabelaVinculos.setCellWidget(i, 2, btn_desvincular)

        self.labelInfo.setText(f"<b>🔗 Vínculos ativos: {len(vinculos)}</b>")

    def vincular(self):
        if self.comboPai.count() == 0:
            QMessageBox.warning(self, "Erro", "Nenhum responsável (pai) cadastrado ainda. "
                                               "Crie um usuário do tipo 'pai' na tela de usuários.")
            return
        if self.comboAluno.count() == 0:
            QMessageBox.warning(self, "Erro", "Nenhum aluno cadastrado ainda. "
                                               "Cadastre um aluno na tela do psicólogo.")
            return

        pai_id = self.comboPai.currentData()
        aluno_id = self.comboAluno.currentData()

        if self.db.vinculo_existe(pai_id, aluno_id):
            QMessageBox.warning(self, "Erro", "Este vínculo já existe.")
            return

        self.db.vincular_pai(pai_id, aluno_id)
        QMessageBox.information(self, "Sucesso", "Vínculo criado com sucesso!")
        self.carregar_vinculos()

    def desvincular(self, vinculo_id):
        confirm = QMessageBox.question(self, "Confirmar", "Remover este vínculo?")
        if confirm == QMessageBox.StandardButton.Yes:
            self.db.desvincular(vinculo_id)
            self.carregar_vinculos()
