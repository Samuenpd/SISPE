"""
screens/admin.py
==================
Lógica da tela de administração (gerenciar usuários).

Este arquivo NÃO constrói nenhum widget diretamente — toda a interface
visual vive em uis/admin_ui.py (classe Ui_AdminScreen). Aqui só ficam:
validações, filtragem e chamadas ao banco (database.py). Nenhum SQL cru
fica nesta tela — tudo passa por métodos do DatabaseManager.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox

from qfluentwidgets import PushButton

from uis.admin_ui import Ui_AdminScreen
from screens.utils import mostrar_alerta


class AdminScreen(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.ui = Ui_AdminScreen()
        self.ui.setupUi(self)

        self.ui.inputBusca.textChanged.connect(self.carregar_usuarios)
        self.ui.btnCriarUsuario.clicked.connect(self.criar_usuario)

        self.atualizar()

    # ------------------------------------------------------------------ #
    # API pública — chamada por main_app_qt.py
    # ------------------------------------------------------------------ #
    def atualizar(self):
        self.carregar_usuarios()
        self.atualizar_info()

    # ------------------------------------------------------------------ #
    def atualizar_info(self):
        total = self.db.contar_usuarios()
        pais = self.db.contar_usuarios_por_tipo("pai")
        psico = self.db.contar_usuarios_por_tipo("psicologo")
        self.ui.labelInfo.setText(f"📊 Total: {total} | 👨‍👩‍👧 Responsáveis: {pais} | 🧠 Psicólogos: {psico}")

    def criar_usuario(self):
        username = self.ui.inputUsername.text().strip()
        senha = self.ui.inputSenha.text().strip()

        # Extrai o tipo sem o emoji (pega a última palavra do combo)
        tipo_com_emoji = self.ui.comboTipo.currentText()
        tipo = tipo_com_emoji.split()[-1].lower()
        if tipo == "psicólogo":
            tipo = "psicologo"

        if not username or not senha:
            mostrar_alerta(self, QMessageBox.Icon.Warning, "Erro", "Preencha todos os campos")
            return
        if self.db.usuario_existe(username):
            mostrar_alerta(self, QMessageBox.Icon.Warning, "Erro", "Usuário já existe")
            return

        self.db.criar_usuario(username, senha, tipo)
        mostrar_alerta(self, QMessageBox.Icon.Information, "Sucesso", "Usuário criado com sucesso!")
        self.ui.inputUsername.clear()
        self.ui.inputSenha.clear()
        self.atualizar()

    def carregar_usuarios(self):
        texto = self.ui.inputBusca.text().strip().lower()
        usuarios = self.db.listar_usuarios()
        if texto:
            usuarios = [u for u in usuarios if texto in u[1].lower()]

        tabela = self.ui.tabelaUsuarios
        tabela.setRowCount(len(usuarios))
        for i, (id_, user, tipo) in enumerate(usuarios):
            tabela.setItem(i, 0, QTableWidgetItem(user))
            tabela.setItem(i, 1, QTableWidgetItem(tipo))

            btn_excluir = PushButton("Excluir")
            btn_excluir.clicked.connect(lambda checked, uid=id_: self.excluir(uid))
            tabela.setCellWidget(i, 2, btn_excluir)

            tabela.item(i, 0).setData(Qt.ItemDataRole.UserRole, id_)

    def excluir(self, user_id):
        botoes = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        confirm = mostrar_alerta(self, QMessageBox.Icon.Question, "Confirmar", "Excluir usuário?", botoes)
        if confirm == QMessageBox.StandardButton.Yes:
            self.db.excluir_usuario(user_id)
            self.atualizar()
