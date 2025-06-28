import sqlite3

def criar_banco():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("Banco criado com sucesso.")

if __name__ == "__main__":
    criar_banco()
