from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QPushButton, QMessageBox, QHeaderView,
    QScrollArea, QVBoxLayout
)
from PyQt6.QtCore import Qt


class AdminScreen(QWidget):
    def __init__(self, db):
        super().__init__()
        # Carrega o UI original
        uic.loadUi("uis/admin.ui", self)

        self.db = db

        # ========== SCROLL AREA (igual ao psicólogo) ==========
        self.conteudo = QWidget()
        # Transfere o layout principal (verticalLayout) para o novo widget
        self.conteudo.setLayout(self.verticalLayout)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.conteudo)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QScrollArea.Shape.NoFrame)

        # Define um layout externo para esta tela, contendo apenas a scroll area
        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(0, 0, 0, 0)
        layout_externo.addWidget(self.scrollArea)

        # ========== CONFIGURAÇÃO DA TABELA ==========
        self.tabelaUsuarios.setColumnCount(3)
        self.tabelaUsuarios.setHorizontalHeaderLabels(["Username", "Tipo", "Ações"])
        self.tabelaUsuarios.setEditTriggers(self.tabelaUsuarios.EditTrigger.NoEditTriggers)

        # Remove a rolagem interna da tabela (a página inteira que rola)
        self.tabelaUsuarios.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabelaUsuarios.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Tabela se ajusta ao conteúdo (todas as linhas visíveis)
        self.tabelaUsuarios.setSizeAdjustPolicy(
            self.tabelaUsuarios.SizeAdjustPolicy.AdjustToContents
        )

        # Altura das linhas
        self.tabelaUsuarios.verticalHeader().setDefaultSectionSize(55)

        # Redimensionamento das colunas: Username expande, outras ajustam ao conteúdo
        header = self.tabelaUsuarios.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # Expansão vertical: frameTabela (índice 3 no verticalLayout) recebe o espaço extra
        self.verticalLayout.setStretch(3, 1)   # item 0=título,1=stats,2=criar,3=tabela
        self.frameTabela.setMinimumHeight(700)  # altura mínima para a área da tabela

        # Conexões
        self.inputBusca.textChanged.connect(self.carregar_usuarios)
        self.btnCriarUsuario.clicked.connect(self.criar_usuario)
        # Carrega dados iniciais
        self.atualizar()

    def atualizar(self):
        self.carregar_usuarios()
        self.atualizar_info()

    def atualizar_info(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='pai'")
        pais = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='psicologo'")
        psico = cursor.fetchone()[0]
        self.labelInfo.setText(f"📊 Total: {total} | 👨‍👩‍👧 Responsáveis: {pais} | 🧠 Psicólogos: {psico}")

    def criar_usuario(self):
        username = self.inputUsername.text().strip()
        senha = self.inputSenha.text().strip()
        # Extrai tipo sem emoji (pega a última palavra)
        tipo_com_emoji = self.comboTipo.currentText()
        tipo = tipo_com_emoji.split()[-1].lower()  # "pai" ou "psicólogo" -> "psicologo"
        # Ajusta se for "psicólogo" para "psicologo" (seu banco espera "psicologo")
        if tipo == "psicólogo":
            tipo = "psicologo"

        if not username or not senha:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos")
            return
        if self.db.usuario_existe(username):
            QMessageBox.warning(self, "Erro", "Usuário já existe")
            return
        self.db.criar_usuario(username, senha, tipo)
        QMessageBox.information(self, "Sucesso", "Usuário criado com sucesso!")
        self.inputUsername.clear()
        self.inputSenha.clear()
        self.atualizar()

    def carregar_usuarios(self):
        texto = self.inputBusca.text().lower()
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT id, username, tipo FROM usuarios")
        dados = cursor.fetchall()
        filtrados = [d for d in dados if texto in d[1].lower()]

        self.tabelaUsuarios.setRowCount(len(filtrados))
        for i, (id_, user, tipo) in enumerate(filtrados):
            self.tabelaUsuarios.setItem(i, 0, QTableWidgetItem(user))
            self.tabelaUsuarios.setItem(i, 1, QTableWidgetItem(tipo))
            btn_excluir = QPushButton("Excluir")
            btn_excluir.clicked.connect(lambda checked, uid=id_: self.excluir(uid))
            self.tabelaUsuarios.setCellWidget(i, 2, btn_excluir)
            # Armazena o ID no UserRole da coluna 0
            self.tabelaUsuarios.item(i, 0).setData(Qt.ItemDataRole.UserRole, id_)

    def excluir(self, user_id):
        confirm = QMessageBox.question(self, "Confirmar", "Excluir usuário?")
        if confirm == QMessageBox.StandardButton.Yes:
            cursor = self.db.conn.cursor()
            cursor.execute("DELETE FROM relacao_pai_aluno WHERE pai_id=?", (user_id,))
            cursor.execute("DELETE FROM relatorios WHERE psicologo_id=?", (user_id,))
            cursor.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
            self.db.conn.commit()
            self.atualizar()