import sqlite3
import hashlib

DB_NAME = "sispe.db"

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_admin_inicial():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Criação das tabelas se não existirem
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL
        );
    ''')

    cursor.execute('''
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos_pais (
            aluno_id INTEGER,
            pai_id TEXT,
            PRIMARY KEY (aluno_id, pai_id),
            FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
            FOREIGN KEY (pai_id) REFERENCES usuarios(username) ON DELETE CASCADE
        );
    ''')

    # Cria um admin inicial se não existir
    admin_user = "admin"
    admin_pass = "123"  # senha inicial
    admin_type = "secretaria"

    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (admin_user,))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, user_type) VALUES (?, ?, ?)",
            (admin_user, hash_senha(admin_pass), admin_type)
        )
        print(f"Usuário administrador '{admin_user}' criado com senha '{admin_pass}'.")
    else:
        print("Usuário administrador já existe.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    criar_admin_inicial()
