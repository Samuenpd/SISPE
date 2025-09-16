import sqlite3
import hashlib
import os

# Aqui você precisa da classe DatabaseManager para garantir que a lógica seja a mesma.
# Em um projeto maior, esta classe estaria em um módulo separado.
class DatabaseManager:
    def __init__(self, db_name="sispe.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Pega a pasta do script
        db_path = os.path.join(base_dir, db_name) 
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def _hash_senha(self, senha):
        """Método privado para gerar o hash da senha."""
        return hashlib.sha256(senha.encode()).hexdigest()

    def add_user(self, username, password, user_type): # Modificado para receber a senha sem hash
        password_hash = self._hash_senha(password) # Gera o hash aqui
        try:
            self.cursor.execute("INSERT INTO usuarios (username, password_hash, user_type) VALUES (?, ?, ?)", (username, password_hash, user_type))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        
    def create_tables(self):
        """Cria as tabelas do banco de dados se elas não existirem."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                user_type TEXT NOT NULL
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                sala INTEGER NOT NULL,
                serie INTEGER NOT NULL,
                gravidade TEXT NOT NULL,
                observacoes TEXT,
                user_id TEXT,
                FOREIGN KEY (user_id) REFERENCES usuarios(username) ON DELETE CASCADE
            );
        ''')
        # nova tabela para relacionar pais e alunos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alunos_pais (
                aluno_id INTEGER,
                pai_id TEXT,
                PRIMARY KEY (aluno_id, pai_id),
                FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
                FOREIGN KEY (pai_id) REFERENCES usuarios(username) ON DELETE CASCADE
            );
        ''')
        self.conn.commit()

    def get_user(self, username):
        self.cursor.execute("SELECT password_hash, user_type FROM usuarios WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        return result if result else None

    def add_aluno(self, nome, sala, serie, gravidade, user_id):
        self.cursor.execute(
            "INSERT INTO alunos (nome, sala, serie, gravidade, observacoes, user_id) VALUES (?, ?, ?, ?, ?, ?)",
            (nome, sala, serie, gravidade, "", user_id)
        )
        self.conn.commit()

    def get_alunos_by_user(self, user_id):
        self.cursor.execute("SELECT id, nome, sala, serie, gravidade, observacoes FROM alunos WHERE user_id = ?", (user_id,))
        alunos_data = self.cursor.fetchall()
        return [Aluno(nome=data[1], sala=data[2], serie=data[3], gravidade=data[4], observacoes=data[5], id=data[0]) for data in alunos_data]

    def get_aluno_by_id(self, aluno_id):
        self.cursor.execute('SELECT id, nome, sala, serie, gravidade, observacoes FROM alunos WHERE id = ?', (aluno_id,))
        data = self.cursor.fetchone()
        if data:
            return Aluno(nome=data[1], sala=data[2], serie=data[3], gravidade=data[4], observacoes=data[5], id=data[0])
        return None
    
    # eu criei uma parte pra salvar registor sobre os alunos
    def aluno_observação(self, aluno_id, observacao):
        self.cursor.execute(
            'UPDATE alunos SET observacoes = ? WHERE id = ?',
            (observacao, aluno_id)
        )
        self.conn.commit()

    def update_aluno(self, aluno_id, nome, sala, serie, gravidade):
        self.cursor.execute(
            "UPDATE alunos SET nome = ?, sala = ?, serie = ?, gravidade = ? WHERE id = ?",
            (nome, sala, serie, gravidade, aluno_id)
        )
        self.conn.commit()
    # acaba aqui

    def delete_aluno(self, aluno_id):
        self.cursor.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
        self.conn.commit()

    def close(self):
        # Fecha a conexão com o banco de dados
        self.conn.close()

    def delete_user(self, username):
        # Exclui a conta do usuário
        self.cursor.execute("DELETE FROM usuarios WHERE username = ?", (username,))
        self.conn.commit()

    def vincular_pai_aluno(self, aluno_id, pai_username):
        try:
            self.cursor.execute(
                "INSERT INTO alunos_pais (aluno_id, pai_id) VALUES (?, ?)",
                (aluno_id, pai_username)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Esse vínculo já existe.")


    def get_alunos_by_pai(self, pai_username):
        self.cursor.execute('''
            SELECT a.id, a.nome, a.sala, a.serie, a.gravidade, a.observacoes
            FROM alunos a
            JOIN alunos_pais ap ON a.id = ap.aluno_id
            WHERE ap.pai_id = ?
        ''', (pai_username,))
        alunos_data = self.cursor.fetchall()
        return [Aluno(nome=d[1], sala=d[2], serie=d[3], gravidade=d[4], observacoes=d[5], id=d[0]) for d in alunos_data]

    def get_pais(self):
        self.cursor.execute("SELECT username FROM usuarios WHERE user_type = 'pai'")
        return [row[0] for row in self.cursor.fetchall()]

    def get_psicologas(self):
        self.cursor.execute("SELECT username FROM usuarios WHERE user_type = 'psicologa'")
        return [row[0] for row in self.cursor.fetchall()]

def configurar_banco_dados():
    db = DatabaseManager()
    username = "admin"
    password = "123"
    user_type = "secretaria"
    
    if db.add_user(username, password, user_type):
        print(f"Usuário '{username}' criado com sucesso.")
    else:
        print(f"Usuário '{username}' já existe.")

if __name__ == "__main__":
    configurar_banco_dados()
