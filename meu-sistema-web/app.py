from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'segredo123'

# CRIAR BANCO
def criar_banco():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # TABELA PRODUTOS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        preco REAL
    )
    ''')

    # TABELA VENDAS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        valor REAL
    )
    ''')

    # TABELA USUARIOS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    ''')

    cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (username, password) VALUES ('admin', '123')")

    conn.commit()
    conn.close()

criar_banco()

# LOGIN
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        senha = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (user, senha))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            session['user'] = user
            return redirect('/dashboard')

    return render_template('login.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT vendas.id, produtos.nome, vendas.valor
    FROM vendas
    JOIN produtos ON vendas.produto_id = produtos.id
    """)
    vendas = cursor.fetchall()

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    labels = [v[1] for v in vendas]
    valores = [v[2] for v in vendas]

    conn.close()

    return render_template('dashboard.html',
                           vendas=vendas,
                           produtos=produtos,
                           labels=labels,
                           valores=valores)

# CADASTRAR PRODUTO
@app.route('/produto', methods=['GET', 'POST'])
def produto():
    if request.method == 'POST':
        nome = request.form['nome']
        preco = request.form['preco']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)", (nome, preco))

        conn.commit()
        conn.close()

        return redirect('/produto')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()

    return render_template('produto.html', produtos=produtos)

# ADICIONAR VENDA
@app.route('/add', methods=['POST'])
def add():
    produto_id = request.form['produto']
    valor = request.form['valor']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO vendas (produto_id, valor) VALUES (?, ?)", (produto_id, valor))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# EXCLUIR
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM vendas WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

# EDITAR
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        valor = request.form['valor']
        cursor.execute("UPDATE vendas SET valor=? WHERE id=?", (valor, id))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    cursor.execute("""
    SELECT vendas.id, produtos.nome, vendas.valor
    FROM vendas
    JOIN produtos ON vendas.produto_id = produtos.id
    WHERE vendas.id=?
    """, (id,))
    
    venda = cursor.fetchone()
    conn.close()

    return render_template('editar.html', venda=venda)

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)