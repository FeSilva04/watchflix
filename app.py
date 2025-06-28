from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from tmdb import get_filmes_populares, buscar_filmes_por_nome, buscar_filmes_por_filtros, get_generos, get_detalhes_filme, get_trailer_filme, get_elenco_filme, get_streamings_filme, get_classificacao_indicativa
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

        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()

        conn.close()

        if usuario and usuario[3] == senha:  # senha pura
            session['usuario'] = {'id': usuario[0], 'nome': usuario[1]}
            flash("Login bem-sucedido!")
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

        conn = sqlite3.connect('usuarios.db')
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

# CONFIGURAÇÕES
@app.route('/configuracoes')
@login_required
def configuracoes():
    return "Página de configurações (alterar e-mail/senha)"

# Filmes
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

    generos = get_generos()

    return render_template('filmes.html',
                           filmes=filmes,
                           page=page,
                           total_pages=total_pages,
                           build_url=build_url,
                           generos=generos)

# Rota de detalhes do filme clicado
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

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nota FROM interacoes
        WHERE usuario_id = ? AND filme_id = ?
    """, (usuario_id, movie_id))
    resultado = cursor.fetchone()
    if resultado and resultado[0] is not None:
        nota_usuario = resultado[0]
    conn.close()

    return render_template('filme_detalhes.html', 
                           filme=filme, 
                           trailer=trailer, 
                           elenco=elenco, 
                           streamings=streamings,
                           classificacao=classificacao,
                           nota_usuario=nota_usuario,
                           range=range)

# ASSISTIDOS
@app.route('/assistidos')
@login_required
def assistidos():
    return "Página dos filmes assistidos"

@app.route('/assistido/<int:filme_id>', methods=['POST'])
@login_required
def marcar_assistido(filme_id):
    usuario_id = session['usuario']['id']
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    # Verifica se já existe a interação com esse filme
    cursor.execute("""
        SELECT ja_assistido FROM interacoes
        WHERE usuario_id = ? AND filme_id = ?
    """, (usuario_id, filme_id))
    resultado = cursor.fetchone()

    if resultado:
        # Já existe, então alterna o valor
        novo_valor = 0 if resultado[0] == 1 else 1
        cursor.execute("""
            UPDATE interacoes SET ja_assistido = ?
            WHERE usuario_id = ? AND filme_id = ?
        """, (novo_valor, usuario_id, filme_id))
    else:
        # Não existe, então cria a entrada com ja_assistido = 1
        cursor.execute("""
            INSERT INTO interacoes (usuario_id, filme_id, ja_assistido)
            VALUES (?, ?, 1)
        """, (usuario_id, filme_id))

    conn.commit()
    conn.close()
    return redirect(request.referrer)
    
# MINHA LISTA
@app.route('/minha_lista')
@login_required
def minha_lista():
    return "Aqui está sua lista de filmes"

@app.route('/minha_lista/<int:filme_id>', methods=['POST'])
@login_required
def adicionar_minha_lista(filme_id):
    usuario_id = session['usuario']['id']
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    # Verifica se já existe a interação com esse filme
    cursor.execute("""
        SELECT na_lista FROM interacoes
        WHERE usuario_id = ? AND filme_id = ?
    """, (usuario_id, filme_id))
    resultado = cursor.fetchone()

    if resultado:
        # Já existe, então alterna o valor: 1 vira 0 e 0 vira 1
        novo_valor = 0 if resultado[0] == 1 else 1
        cursor.execute("""
            UPDATE interacoes SET na_lista = ?
            WHERE usuario_id = ? AND filme_id = ?
        """, (novo_valor, usuario_id, filme_id))
    else:
        # Não existe, então cria a entrada com minha_lista = 1
        cursor.execute("""
            INSERT INTO interacoes (usuario_id, filme_id, na_lista)
            VALUES (?, ?, 1)
        """, (usuario_id, filme_id))
    
    conn.commit()
    conn.close()
    return redirect(request.referrer)

# CLASSIFICAÇÃO
@app.route('/classificar/<int:filme_id>/<int:nota>', methods=['POST'])
@login_required
def classificar(filme_id, nota):
    usuario_id = session['usuario']['id']
    try:
        with sqlite3.connect('usuarios.db', timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interacoes (usuario_id, filme_id, nota)
                VALUES (?, ?, ?)
                ON CONFLICT(usuario_id, filme_id)
                DO UPDATE SET nota = excluded.nota
            """, (usuario_id, filme_id, nota))
            conn.commit()
        return redirect(request.referrer)
    except sqlite3.Error as e:
        return f"Erro no banco de dados: {e}", 500

# REMOVER NOTA
@app.route('/remover_nota/<int:filme_id>', methods=['POST'])
@login_required
def remover_nota(filme_id):
    usuario_id = session['usuario']['id']
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE interacoes
        SET nota = NULL
        WHERE usuario_id = ? AND filme_id = ?
    """, (usuario_id, filme_id))

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