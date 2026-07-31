import sqlite3
import bcrypt

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
            senha BLOB,
            tipo TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            sala TEXT,
            serie TEXT,
            gravidade TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS relacao_pai_aluno (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pai_id INTEGER,
            aluno_id INTEGER
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS relatorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER,
            psicologo_id INTEGER,
            texto TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS compromissos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            psicologo_id INTEGER,
            titulo TEXT,
            data TEXT,
            hora TEXT,
            cor TEXT,
            descricao TEXT
        )
        """)

        # Migração: bancos criados antes de existir 'data_criacao' não têm a coluna
        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = [c[1] for c in cursor.fetchall()]
        if "data_criacao" not in colunas:
            cursor.execute(
                "ALTER TABLE usuarios ADD COLUMN data_criacao TIMESTAMP"
            )

            cursor.execute("""
            UPDATE usuarios
            SET data_criacao = CURRENT_TIMESTAMP
            WHERE data_criacao IS NULL
            """)

        cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
        if not cursor.fetchone():
            senha = bcrypt.hashpw("123".encode(), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO usuarios (username, senha, tipo) VALUES (?, ?, ?)",
                ("admin", senha, "admin")
            )

        self.conn.commit()

    # LOGIN
    def login(self, user, senha):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, senha, tipo FROM usuarios WHERE username=?", (user,))
        result = cursor.fetchone()

        if result and bcrypt.checkpw(senha.encode(), result[1]):
            return {"id": result[0], "tipo": result[2], "username": user}
        return None

    # USUÁRIOS
    def criar_usuario(self, username, senha, tipo):
        cursor = self.conn.cursor()
        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO usuarios (username, senha, tipo) VALUES (?, ?, ?)",
            (username, senha_hash, tipo)
        )
        self.conn.commit()
    
    def usuario_existe(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM usuarios WHERE username=?", (username,))
        return cursor.fetchone() is not None

    # ALUNOS (AGORA COMPLETO)
    def adicionar_aluno(self, nome, sala, serie, gravidade):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO alunos (nome, sala, serie, gravidade) VALUES (?, ?, ?, ?)",
            (nome, sala, serie, gravidade)
        )
        self.conn.commit()

    def listar_alunos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, sala, serie, gravidade FROM alunos")
        return cursor.fetchall()
    
    def aluno_existe(self, nome, sala, serie):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT 1 FROM alunos
        WHERE nome=? AND sala=? AND serie=?
        """, (nome, sala, serie))
        return cursor.fetchone() is not None
    
    def atualizar_aluno(self, aluno_id, nome, sala, serie, gravidade):
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE alunos
        SET nome=?, sala=?, serie=?, gravidade=?
        WHERE id=?
        """, (nome, sala, serie, gravidade, aluno_id))
        self.conn.commit()

    def excluir_aluno(self, aluno_id):
        cursor = self.conn.cursor()

        # remove vínculos
        cursor.execute("DELETE FROM relacao_pai_aluno WHERE aluno_id=?", (aluno_id,))

        # remove relatórios
        cursor.execute("DELETE FROM relatorios WHERE aluno_id=?", (aluno_id,))

        # remove aluno
        cursor.execute("DELETE FROM alunos WHERE id=?", (aluno_id,))

        self.conn.commit()

    # RELAÇÃO
    def vincular_pai(self, pai_id, aluno_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO relacao_pai_aluno (pai_id, aluno_id) VALUES (?, ?)",
            (pai_id, aluno_id)
        )
        self.conn.commit()

    def alunos_do_pai(self, pai_id):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT alunos.id, alunos.nome
        FROM alunos
        JOIN relacao_pai_aluno ON alunos.id = relacao_pai_aluno.aluno_id
        WHERE relacao_pai_aluno.pai_id=?
        """, (pai_id,))
        return cursor.fetchall()

    def listar_pais(self):
        """Retorna (id, username) de todos os usuários do tipo 'pai'."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, username FROM usuarios WHERE tipo='pai' ORDER BY username")
        return cursor.fetchall()

    def vinculo_existe(self, pai_id, aluno_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT 1 FROM relacao_pai_aluno WHERE pai_id=? AND aluno_id=?",
            (pai_id, aluno_id)
        )
        return cursor.fetchone() is not None

    def listar_vinculos(self):
        """Retorna (vinculo_id, pai_username, aluno_id, aluno_nome) de todos os vínculos."""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT relacao_pai_aluno.id, usuarios.username, alunos.id, alunos.nome
        FROM relacao_pai_aluno
        JOIN usuarios ON usuarios.id = relacao_pai_aluno.pai_id
        JOIN alunos ON alunos.id = relacao_pai_aluno.aluno_id
        ORDER BY usuarios.username
        """)
        return cursor.fetchall()

    def desvincular(self, vinculo_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM relacao_pai_aluno WHERE id=?", (vinculo_id,))
        self.conn.commit()

    # RELATÓRIOS
    def criar_relatorio(self, aluno_id, psicologo_id, texto):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO relatorios (aluno_id, psicologo_id, texto) VALUES (?, ?, ?)",
            (aluno_id, psicologo_id, texto)
        )
        self.conn.commit()

    def listar_relatorios_aluno(self, aluno_id):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT texto, data FROM relatorios
        WHERE aluno_id=?
        ORDER BY data DESC
        """, (aluno_id,))
        return cursor.fetchall()

    # PERFIL
    def obter_usuario(self, user_id):
        """Retorna dict com username, tipo e data_criacao de um usuário."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT username, tipo, data_criacao FROM usuarios WHERE id=?", (user_id,)
        )
        result = cursor.fetchone()
        if not result:
            return None
        return {"username": result[0], "tipo": result[1], "data_criacao": result[2]}

    # AGENDA (compromissos do psicólogo)
    def criar_compromisso(self, psicologo_id, titulo, data, hora, cor, descricao=""):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO compromissos (psicologo_id, titulo, data, hora, cor, descricao)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (psicologo_id, titulo, data, hora, cor, descricao))
        self.conn.commit()

    def listar_compromissos(self, psicologo_id):
        """Retorna (id, titulo, data, hora, cor, descricao) ordenados por data/hora."""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, titulo, data, hora, cor, descricao
        FROM compromissos
        WHERE psicologo_id=?
        ORDER BY data ASC, hora ASC
        """, (psicologo_id,))
        return cursor.fetchall()

    def compromissos_por_data(self, psicologo_id, data):

        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                id,
                titulo,
                hora,
                cor,
                descricao
            FROM compromissos
            WHERE psicologo_id=?
            AND data=?
            ORDER BY hora
        """, (psicologo_id, data))

        return cursor.fetchall()

    def datas_com_compromissos(self, psicologo_id):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT DISTINCT data
            FROM compromissos
            WHERE psicologo_id=?
        """, (psicologo_id,))

        return [linha[0] for linha in cursor.fetchall()]

    def excluir_compromisso(self, compromisso_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM compromissos WHERE id=?", (compromisso_id,))
        self.conn.commit()

    def atualizar_compromisso(self, compromisso_id, titulo, data, hora, cor, descricao=""):
        """Atualiza um compromisso existente."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE compromissos
            SET titulo=?, data=?, hora=?, cor=?, descricao=?
            WHERE id=?
            """,
            (titulo, data, hora, cor, descricao, compromisso_id)
        )
        self.conn.commit()