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
            tipo TEXT
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
            return {"id": result[0], "tipo": result[2]}
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