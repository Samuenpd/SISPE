import sys
import sqlite3
import bcrypt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QStackedWidget
)

# ===================== BANCO =====================
class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("sispe.db")
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            senha TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            turma TEXT
        )
        """)

        # cria usuário padrão
        cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
        if not cursor.fetchone():
            senha_hash = bcrypt.hashpw("123".encode(), bcrypt.gensalt())
            cursor.execute("INSERT INTO usuarios (username, senha) VALUES (?, ?)", ("admin", senha_hash))

        self.conn.commit()

    def verificar_login(self, username, senha):
        cursor = self.conn.cursor()
        cursor.execute("SELECT senha FROM usuarios WHERE username=?", (username,))
        result = cursor.fetchone()

        if result and bcrypt.checkpw(senha.encode(), result[0]):
            return True
        return False

    def adicionar_aluno(self, nome, turma):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO alunos (nome, turma) VALUES (?, ?)", (nome, turma))
        self.conn.commit()

    def listar_alunos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, turma FROM alunos")
        return cursor.fetchall()

    def deletar_aluno(self, aluno_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM alunos WHERE id=?", (aluno_id,))
        self.conn.commit()

# ===================== LOGIN =====================
class LoginScreen(QWidget):
    def __init__(self, app_ref, db):
        super().__init__()
        self.app_ref = app_ref
        self.db = db

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Login SISPE"))

        self.user = QLineEdit()
        self.user.setPlaceholderText("Usuário")
        layout.addWidget(self.user)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Senha")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        btn = QPushButton("Entrar")
        btn.clicked.connect(self.login)
        layout.addWidget(btn)

        self.setLayout(layout)

    def login(self):
        if self.db.verificar_login(self.user.text(), self.password.text()):
            self.app_ref.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Erro", "Login inválido")

# ===================== DASHBOARD =====================
class Dashboard(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Cadastro de Alunos"))

        form = QHBoxLayout()

        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Nome")
        form.addWidget(self.nome)

        self.turma = QLineEdit()
        self.turma.setPlaceholderText("Turma")
        form.addWidget(self.turma)

        layout.addLayout(form)

        btn_add = QPushButton("Adicionar")
        btn_add.clicked.connect(self.add_aluno)
        layout.addWidget(btn_add)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Turma"])
        layout.addWidget(self.tabela)

        btn_refresh = QPushButton("Atualizar")
        btn_refresh.clicked.connect(self.load_data)
        layout.addWidget(btn_refresh)

        btn_delete = QPushButton("Excluir Selecionado")
        btn_delete.clicked.connect(self.delete_selected)
        layout.addWidget(btn_delete)

        self.setLayout(layout)
        self.load_data()

    def add_aluno(self):
        nome = self.nome.text()
        turma = self.turma.text()

        if nome and turma:
            self.db.adicionar_aluno(nome, turma)
            self.load_data()
        else:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos")

    def load_data(self):
        dados = self.db.listar_alunos()
        self.tabela.setRowCount(len(dados))

        for i, (id_, nome, turma) in enumerate(dados):
            self.tabela.setItem(i, 0, QTableWidgetItem(str(id_)))
            self.tabela.setItem(i, 1, QTableWidgetItem(nome))
            self.tabela.setItem(i, 2, QTableWidgetItem(turma))

    def delete_selected(self):
        row = self.tabela.currentRow()
        if row >= 0:
            aluno_id = int(self.tabela.item(row, 0).text())
            self.db.deletar_aluno(aluno_id)
            self.load_data()

# ===================== APP =====================
class App(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()

        self.login = LoginScreen(self, self.db)
        self.dashboard = Dashboard(self.db)

        self.addWidget(self.login)
        self.addWidget(self.dashboard)

# ===================== MAIN =====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.setWindowTitle("SISPE COMPLETO - PyQt6")
    window.resize(700, 500)
    window.show()
    sys.exit(app.exec())