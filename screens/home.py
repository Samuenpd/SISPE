"""
screens/home.py
================
Lógica da tela inicial (dashboard) do SISPE.

Este arquivo NÃO constrói nenhum widget diretamente — toda a interface visual
vive em uis/home_ui.py (classe Ui_HomeScreen). Aqui só ficam: instanciar
a UI, decidir quais cards de estatística aparecem conforme o tipo de usuário
logado, e falar com o banco (database.py).

Regra de negócio dos cards de estatística:
    - admin:      vê os 4 números globais da escola inteira.
    - psicologo:  vê só os números que pertencem a ele (relatórios que ele
                  escreveu, compromissos que ele agendou).
    - qualquer outro tipo (ex: pai) ou ninguém logado: nenhum card aparece.
"""

from PyQt6.QtWidgets import QWidget

from uis.home_ui import Ui_HomeScreen
from screens.theme import CORES


class HomeScreen(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.ui = Ui_HomeScreen()
        self.ui.setupUi(self)

        # Sem usuário logado ainda (ex: primeira montagem da tela) -> sem cards
        self.ui.containerEstatisticas.setVisible(False)

    # ------------------------------------------------------------------ #
    # API pública — chamada por main_app_qt.py
    # ------------------------------------------------------------------ #
    def atualizar(self, usuario=None):
        """Atualiza a saudação personalizada e remonta os cards de
        estatística de acordo com o tipo do usuário logado."""
        if usuario:
            tipo = usuario["tipo"].capitalize()
            self.ui.labelMensagem.setText(f"Bem-vindo(a), {tipo}!")
        else:
            self.ui.labelMensagem.setText("Bem-vindo(a) ao SISPE")

        self._montar_estatisticas_para(usuario)

    def atualizar_dashboard(self, usuario=None):
        """Mantido por compatibilidade com chamadas antigas — delega para
        _montar_estatisticas_para(). Prefira usar atualizar(usuario)."""
        self._montar_estatisticas_para(usuario)

    # ------------------------------------------------------------------ #
    def _montar_estatisticas_para(self, usuario):
        self.ui.limpar_estatisticas()

        tipo = usuario["tipo"] if usuario else None

        if tipo == "admin":
            self._montar_estatisticas_admin()
        elif tipo == "psicologo":
            self._montar_estatisticas_psicologo(usuario["id"])
        else:
            # pai, ou ninguém logado -> nenhum card de estatística
            self.ui.containerEstatisticas.setVisible(False)
            return

        self.ui.containerEstatisticas.setVisible(True)

    def _montar_estatisticas_admin(self):
        """Painel global da escola inteira — só o admin vê isto."""
        stats = self.db.obter_estatisticas_dashboard()

        self.ui.criar_card_estatistica(
            "🎓", CORES["azul_escuro"], "Total de alunos"
        ).definir_valor(stats["alunos"])

        self.ui.criar_card_estatistica(
            "📝", CORES["sucesso"], "Relatórios feitos"
        ).definir_valor(stats["relatorios"])

        self.ui.criar_card_estatistica(
            "👨‍👩‍👧", CORES["azul"], "Pais vinculados"
        ).definir_valor(stats["pais"])

        self.ui.criar_card_estatistica(
            "⚠️", CORES["alerta"], "Casos urgentes"
        ).definir_valor(stats["urgentes"])

    def _montar_estatisticas_psicologo(self, psicologo_id):
        """Só os números que pertencem a este psicólogo especificamente."""
        stats = self.db.obter_estatisticas_psicologo(psicologo_id)

        self.ui.criar_card_estatistica(
            "📝", CORES["sucesso"], "Relatórios feitos por você"
        ).definir_valor(stats["relatorios"])

        self.ui.criar_card_estatistica(
            "🗓️", CORES["azul"], "Compromissos agendados"
        ).definir_valor(stats["compromissos"])
