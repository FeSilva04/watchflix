from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from tmdb_movies import get_filmes_populares, buscar_filmes_por_nome, buscar_filmes_por_filtros, get_generos_filmes, get_detalhes_filme, get_trailer_filme, get_elenco_filme, get_streamings_filme, get_classificacao_indicativa_filme
from tmdb_series import get_series_populares, buscar_series_por_nome, buscar_series_por_filtros, get_generos_series, get_detalhes_serie, get_trailer_serie, get_elenco_serie, get_streamings_serie, get_classificacao_indicativa
from urllib.parse import urlencode
from functools import wraps
from builtins import range

app = Flask(__name__)
app.secret_key = 'minha_chave_secreta_1234!@#'  # obrigatório para usar sessions e flash


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash('Você precisa estar logado para acessar esta página.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = sqlite3.connect('watchflix.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()

        conn.close()

        if usuario and usuario[3] == senha:  # senha pura
            session['usuario'] = {'id': usuario[0], 'nome': usuario[1], 'email': usuario[2]}
            #flash("Login bem-sucedido!", "success")
            return redirect(url_for('home'))
        else:
            flash("Email ou senha incorretos.")

    return render_template('login.html')

# Cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']  # senha visível

        conn = sqlite3.connect('watchflix.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                           (nome, email, senha))
            conn.commit()
            flash("Cadastro feito com sucesso. Faça login.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email já cadastrado.")
        finally:
            conn.close()

    return render_template('cadastro.html')

# HOME
@app.route('/')
@login_required
def home():
    filmes_populares, total_pages = get_filmes_populares(1)
    return render_template('index.html', filmes_populares=filmes_populares)

# Sobre Nós
@app.route('/sobre_nos')
@login_required
def sobre_nos():
    return render_template('sobre_nos.html')

# ------- CONFIGURAÇÕES ---------
# PERFIL
@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    usuario = session['usuario']

    conn = sqlite3.connect('watchflix.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        novo_nome = request.form['nome']
        nova_senha = request.form['senha']

        cursor.execute("UPDATE usuarios SET nome = ?, senha = ? WHERE id = ?", (novo_nome, nova_senha, usuario['id']))
        conn.commit()
        flash('Informações atualizadas com sucesso!')

        # Atualiza o nome na sessão
        session['usuario']['nome'] = novo_nome

    cursor.execute("SELECT nome, email FROM usuarios WHERE id = ?", (usuario['id'],))
    nome, email = cursor.fetchone()
    conn.close()

    return render_template('perfil.html', nome=nome, email=email)

# Ação - Alterar nome
@app.route('/alterar_nome', methods=['POST'])
@login_required
def alterar_nome():
    novo_nome = request.form['novo_nome'].strip()
    usuario = session['usuario']

    if not novo_nome:
        flash("O nome não pode ficar vazio.", "error")
        return redirect(url_for('perfil'))

    conn = sqlite3.connect('watchflix.db')
    cursor = conn.cursor()

    cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (usuario['id'],))
    nome_atual = cursor.fetchone()[0]

    if novo_nome == nome_atual:
        flash("O novo nome é igual ao atual.", "warning")
    else:
        cursor.execute("UPDATE usuarios SET nome = ? WHERE id = ?", (novo_nome, usuario['id']))
        conn.commit()
        session['usuario']['nome'] = novo_nome
        flash("Nome alterado com sucesso!", "success")

    conn.close()
    return redirect(url_for('perfil'))

# Ação - Alterar e-mail
@app.route('/alterar_email', methods=['POST'])
@login_required
def alterar_email():
    novo_email = request.form['novo_email']
    senha_atual = request.form['senha_atual']
    usuario = session['usuario']

    conn = sqlite3.connect('watchflix.db')
    cursor = conn.cursor()
    cursor.execute("SELECT senha, email FROM usuarios WHERE id = ?", (usuario['id'],))
    resultado = cursor.fetchone()

    if not resultado:
        flash("Usuário não encontrado.", "error")
    else:
        senha_correta, email_atual = resultado
        if senha_atual != senha_correta:
            flash("Senha Incorreta.", "error")
        elif novo_email == email_atual:
            flash("O novo e-mail é igual ao atual.", "warning")
        else:
            cursor.execute("UPDATE usuarios SET email = ? WHERE id = ?", (novo_email, usuario['id']))
            conn.commit()
            session['usuario']['email'] = novo_email
            flash("E-mail alterado com sucesso!")
        
    conn.close()
    return redirect(url_for('perfil'))

# Ação - Alterar Senha
@app.route('/alterar_senha', methods=['POST'])
@login_required
def alterar_senha():
    nova_senha = request.form['nova_senha']
    confirmar_senha = request.form['confirmar_senha']
    senha_atual = request.form['senha_atual']
    usuario = session['usuario']

    conn = sqlite3.connect('watchflix.db')
    cursor = conn.cursor()
    cursor.execute("SELECT senha FROM usuarios WHERE id = ?", (usuario['id'],))
    senha_correta = cursor.fetchone()[0]

    if senha_atual != senha_correta:
        flash("Senha atual incorreta.")
    elif nova_senha != confirmar_senha:
        flash("As senhas não coincidem.")
    elif nova_senha == senha_correta:
        flash("A nova senha não pode ser igual à atual.")
    elif len(nova_senha) < 6:
        flash("A nova senha deve ter pelo menos 6 caracteres.")
    else:
        cursor.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (nova_senha, usuario['id']))
        conn.commit()
        flash("Senha alterada com sucesso!")

    conn.close()
    return redirect(url_for('perfil'))

# Ação - Excluir conta
@app.route('/excluir_conta', methods=['POST'])
@login_required
def excluir_conta():
    usuario_id = session['usuario']['id']

    conn = sqlite3.connect('watchflix.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM interacoes_filmes WHERE usuario_id = ?", (usuario_id,))
    cursor.execute("DELETE FROM interacoes_series WHERE usuario_id = ?", (usuario_id,))
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    conn.close()

    session.pop('usuario', None)
    flash('Conta excluída com sucesso!')
    return redirect(url_for('login'))

# --------- FILMES ---------
# Página Filmes
@app.route('/filmes')
@login_required
def filmes():
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    nome = request.args.get('nome', '').strip()
    genero = request.args.get('genero', '').strip()
    nota_min = request.args.get('nota_min', '').strip()
    duracao_min = request.args.get('duracao_min', '').strip()

    # Decide qual função da API usar
    if nome:
        filmes, total_pages = buscar_filmes_por_nome(nome, page)
    else:
        filmes, total_pages = buscar_filmes_por_filtros(page, genero, nota_min, duracao_min)
        # filmes, total_pages = get_filmes_populares(page)

    # Limita total de páginas a 500
    if total_pages > 500:
        total_pages = 500
    
    # Corrige se usuário tentar acessar página acima do limite
    if page > total_pages:
        page = total_pages
        if nome:
            filmes, _ = buscar_filmes_por_nome(nome, page)
        else:
            filmes, _ = get_filmes_populares(page)

    # Garante que 'filmes' seja uma lista
    if not filmes:
        filmes = []

    # Montar URLs da paginação mantendo filtros
    args = request.args.to_dict()
    args.pop('page', None)  # Remove o parâmetro 'page' atual para substituir depois
    def build_url(page_num):
        args['page'] = page_num
        return '/filmes?' + urlencode(args)

    generos = get_generos_filmes()

    return render_template('filmes.html',
                           filmes=filmes,
                           page=page,
                           total_pages=total_pages,
                           build_url=build_url,
                           generos=generos)

# Página Detalhes do filme clicado
@app.route('/filme/<int:movie_id>')
def filme_detalhes(movie_id):
    filme = get_detalhes_filme(movie_id)
    if not filme:
        return "Filme não encontrado", 404
    
    trailer = get_trailer_filme(movie_id)
    elenco = filme.get('credits', {}).get('cast', [])
    streamings = filme.get('watch/providers', {}).get('results', {}).get('BR', {}).get('flatrate', [])
    classificacao = get_classificacao_indicativa(movie_id)


    usuario_id = session['usuario']['id']
    nota_usuario = None
    ja_assistido = None
    na_lista = None

    conn = sqlite3.connect('watchflix.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nota, ja_assistido, na_lista FROM interacoes_filmes
        WHERE usuario_id = ? AND item_id = ?
    """, (usuario_id, movie_id))
    resultado = cursor.fetchone()
    if resultado is not None:
        nota_usuario = resultado[0]
        ja_assistido = resultado[1]
        na_lista = resultado[2]
    conn.close()

    return render_template('filme_detalhes.html', 
                           filme=filme, 
                           trailer=trailer, 
                           elenco=elenco, 
                           streamings=streamings,
                           classificacao=classificacao,
                           nota_usuario=nota_usuario,
                           ja_assistido=ja_assistido,
                           na_lista=na_lista,
                           range=range)

# --------- SÉRIES ---------
# Página Séries
@app.route('/series')
@login_required
def series():
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    nome = request.args.get('nome', '').strip()
    genero = request.args.get('genero', '').strip()
    nota_min = request.args.get('nota_min', '').strip()
    duracao_min = request.args.get('duracao_min', '').strip()

    # Decide qual função da API usar
    if nome:
        series, total_pages = buscar_series_por_nome(nome, page)
    else:
        series, total_pages = buscar_series_por_filtros(page, genero, nota_min, duracao_min)
        # filmes, total_pages = get_filmes_populares(page)

    # Limita total de páginas a 500
    if total_pages > 500:
        total_pages = 500
    
    # Corrige se usuário tentar acessar página acima do limite
    if page > total_pages:
        page = total_pages
        if nome:
            series, _ = buscar_series_por_nome(nome, page)
        else:
            series, _ = get_series_populares(page)

    # Garante que 'filmes' seja uma lista
    if not series:
        series = []

    # Montar URLs da paginação mantendo filtros
    args = request.args.to_dict()
    args.pop('page', None)  # Remove o parâmetro 'page' atual para substituir depois
    def build_url(page_num):
        args['page'] = page_num
        return '/series?' + urlencode(args)

    generos = get_generos_series()

    return render_template('series.html',
                           series=series,
                           page=page,
                           total_pages=total_pages,
                           build_url=build_url,
                           generos=generos)

# Página Detalhes da série clicada
@app.route('/tv/<int:serie_id>')
def serie_detalhes(serie_id):
    serie = get_detalhes_serie(serie_id)
    if not serie:
        return "Série não encontrada", 404
    
    trailer = get_trailer_serie(serie_id)
    elenco = serie.get('credits', {}).get('cast', [])
    streamings = serie.get('watch/providers', {}).get('results', {}).get('BR', {}).get('flatrate', [])
    classificacao = get_classificacao_indicativa(serie_id)


    usuario_id = session['usuario']['id']
    nota_usuario = None
    ja_assistido = None
    na_lista = None

    conn = sqlite3.connect('watchflix.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nota, ja_assistido, na_lista FROM interacoes_series
        WHERE usuario_id = ? AND item_id = ?
    """, (usuario_id, serie_id))
    resultado = cursor.fetchone()
    if resultado is not None:
        nota_usuario = resultado[0]
        ja_assistido = resultado[1]
        na_lista = resultado[2]
    conn.close()

    return render_template('serie_detalhes.html', 
                           serie=serie, 
                           trailer=trailer, 
                           elenco=elenco, 
                           streamings=streamings,
                           classificacao=classificacao,
                           nota_usuario=nota_usuario,
                           ja_assistido=ja_assistido,
                           na_lista=na_lista,
                           range=range)

# --------- INTERAÇÕES ---------
# Página Assistidos
@app.route('/assistidos')
@login_required
def assistidos():
    return "Página dos filmes assistidos"

# BOTÃO JÁ ASSISTIDO PARA FILME
@app.route('/assistido/filme/<int:filme_id>', methods=['POST'])
@login_required
def marcar_assistido_filme(filme_id):
    usuario_id = session['usuario']['id']
    conn = sqlite3.connect('watchflix.db')
    cursor = conn.cursor()

    # Verifica se já existe a interação com esse filme
    cursor.execute("""
        SELECT ja_assistido FROM interacoes_filmes
        WHERE usuario_id = ? AND item_id = ?
    """, (usuario_id, filme_id))
    resultado = cursor.fetchone()

    if resultado:
        # Já existe, então alterna o valor
        novo_valor = 0 if resultado[0] == 1 else 1
        cursor.execute("""
            UPDATE interacoes_filmes SET ja_assistido = ?
            WHERE usuario_id = ? AND filme_id = ?
        """, (novo_valor, usuario_id, filme_id))
    else:
        # Não existe, então cria a entrada com ja_assistido = 1
        cursor.execute("""
            INSERT INTO interacoes_filmes (usuario_id, filme_id, ja_assistido)
            VALUES (?, ?, 1)
        """, (usuario_id, filme_id))

    conn.commit()
    conn.close()
    return redirect(request.referrer)
    
# BOTÃO JÁ ASSISTIDO PARA SÉRIE
@app.route('/assistido/serie/<int:serie_id>', methods=['POST'])
@login_required
def marcar_assistido_serie(serie_id):
    usuario_id = session['usuario']['id']
    conn = sqlite3.connect('watchflix.db')
    cursor = conn.cursor()

    # Verifica se já existe a interação com esse filme
    cursor.execute("""
        SELECT ja_assistido FROM interacoes_series
        WHERE usuario_id = ? AND item_id = ?
    """, (usuario_id, serie_id))
    resultado = cursor.fetchone()

    if resultado:
        # Já existe, então alterna o valor
        novo_valor = 0 if resultado[0] == 1 else 1
        cursor.execute("""
            UPDATE interacoes_series SET ja_assistido = ?
            WHERE usuario_id = ? AND item_id = ?
        """, (novo_valor, usuario_id, serie_id))
    else:
        # Não existe, então cria a entrada com ja_assistido = 1
        cursor.execute("""
            INSERT INTO interacoes_series (usuario_id, item_id, ja_assistido)
            VALUES (?, ?, 1)
        """, (usuario_id, serie_id))

    conn.commit()
    conn.close()
    return redirect(request.referrer)

# Página Minha Lista
@app.route('/minha_lista')
@login_required
def minha_lista():
    return "Aqui está sua lista de filmes"

# BOTÃO MINHA LISTA PARA FILME
@app.route('/minha_lista/filme/<int:filme_id>', methods=['POST'])
@login_required
def adicionar_minha_lista_filme(filme_id):
    usuario_id = session['usuario']['id']
    conn = sqlite3.connect('watchflix.db')
    cursor = conn.cursor()

    # Verifica se já existe a interação com esse filme
    cursor.execute("""
        SELECT na_lista FROM interacoes_filmes
        WHERE usuario_id = ? AND item_id = ?
    """, (usuario_id, filme_id))
    resultado = cursor.fetchone()

    if resultado:
        # Já existe, então alterna o valor: 1 vira 0 e 0 vira 1
        novo_valor = 0 if resultado[0] == 1 else 1
        cursor.execute("""
            UPDATE interacoes_filmes SET na_lista = ?
            WHERE usuario_id = ? AND item_id = ?
        """, (novo_valor, usuario_id, filme_id))
    else:
        # Não existe, então cria a entrada com minha_lista = 1
        cursor.execute("""
            INSERT INTO interacoes_filmes (usuario_id, item_id, na_lista)
            VALUES (?, ?, 1)
        """, (usuario_id, filme_id))
    
    conn.commit()
    conn.close()
    return redirect(request.referrer)

# BOTÃO MINHA LISTA PARA SÉRIE
@app.route('/minha_lista/serie/<int:serie_id>', methods=['POST'])
@login_required
def adicionar_minha_lista_serie(serie_id):
    usuario_id = session['usuario']['id']
    conn = sqlite3.connect('watchflix.db')
    cursor = conn.cursor()

    # Verifica se já existe a interação com esse filme
    cursor.execute("""
        SELECT na_lista FROM interacoes_series
        WHERE usuario_id = ? AND item_id = ?
    """, (usuario_id, serie_id))
    resultado = cursor.fetchone()

    if resultado:
        # Já existe, então alterna o valor: 1 vira 0 e 0 vira 1
        novo_valor = 0 if resultado[0] == 1 else 1
        cursor.execute("""
            UPDATE interacoes_series SET na_lista = ?
            WHERE usuario_id = ? AND item_id = ?
        """, (novo_valor, usuario_id, serie_id))
    else:
        # Não existe, então cria a entrada com minha_lista = 1
        cursor.execute("""
            INSERT INTO interacoes_series (usuario_id, item_id, na_lista)
            VALUES (?, ?, 1)
        """, (usuario_id, serie_id))
    
    conn.commit()
    conn.close()
    return redirect(request.referrer)

# ADICIONAR NOTA FILME
@app.route('/classificar/filme/<int:filme_id>/<int:nota>', methods=['POST'])
@login_required
def classificar_filme(filme_id, nota):
    usuario_id = session['usuario']['id']
    try:
        with sqlite3.connect('watchflix.db', timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interacoes_filmes (usuario_id, item_id, nota)
                VALUES (?, ?, ?)
                ON CONFLICT(usuario_id, item_id)
                DO UPDATE SET nota = excluded.nota
            """, (usuario_id, filme_id, nota))
            conn.commit()
        return redirect(request.referrer)
    except sqlite3.Error as e:
        return f"Erro no banco de dados: {e}", 500

# ADICIONAR NOTA SÉRIE
@app.route('/classificar/serie/<int:serie_id>/<int:nota>', methods=['POST'])
@login_required
def classificar_serie(serie_id, nota):
    usuario_id = session['usuario']['id']
    try:
        with sqlite3.connect('watchflix.db', timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interacoes_series (usuario_id, item_id, nota)
                VALUES (?, ?, ?)
                ON CONFLICT(usuario_id, item_id)
                DO UPDATE SET nota = excluded.nota
            """, (usuario_id, serie_id, nota))
            conn.commit()
        return redirect(request.referrer)
    except sqlite3.Error as e:
        return f"Erro no banco de dados: {e}", 500

# REMOVER NOTA FILME
@app.route('/remover_nota/filme/<int:filme_id>', methods=['POST'])
@login_required
def remover_nota_filme(filme_id):
    usuario_id = session['usuario']['id']
    conn = sqlite3.connect('watchflix.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE interacoes_filmes
        SET nota = NULL
        WHERE usuario_id = ? AND item_id = ?
    """, (usuario_id, filme_id))

    conn.commit()
    conn.close()

    return jsonify({'success': True})

# REMOVER NOTA SÉRIE
@app.route('/remover_nota/serie/<int:serie_id>', methods=['POST'])
@login_required
def remover_nota_serie(serie_id):
    usuario_id = session['usuario']['id']
    conn = sqlite3.connect('watchflix.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE interacoes_series
        SET nota = NULL
        WHERE usuario_id = ? AND item_id = ?
    """, (usuario_id, serie_id))

    conn.commit()
    conn.close()

    return jsonify({'success': True})

# Logout
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Você saiu da conta.')
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)