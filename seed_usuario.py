import sqlite3

usuarios_teste = [
    {"nome": "Felipe", "email": "felipe@email.com", "senha": "123456"},
    {"nome": "Ana", "email": "ana@email.com", "senha": "senha123"},
    {"nome": "João", "email": "joao@email.com", "senha": "minhasenha"},
]

def inserir_usuarios():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()

    for u in usuarios_teste:
        try:
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                (u["nome"], u["email"], u["senha"])  # senha pura aqui
            )
        except sqlite3.IntegrityError:
            print(f"Usuário com email {u['email']} já existe. Pulando.")
    
    conn.commit()
    conn.close()
    print("Usuários de teste inseridos com senha visível.")

if __name__ == "__main__":
    inserir_usuarios()
