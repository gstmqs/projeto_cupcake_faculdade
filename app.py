"""
SweetBite Gourmet - Sistema E-Commerce de Cupcakes
Projeto Integrador Transdisciplinar em Engenharia de Software II (PIT II)
Estudante: Gustavo Marques de Almeida (RGM: 35691042)
Arquitetura: MVC (Model-View-Controller)
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "sweetbite_secret_key_pit2"
DB_PATH = os.path.join(os.path.dirname(__file__), "sweetbite.db")

# ==================== MODEL ====================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria_id INTEGER,
        nome TEXT NOT NULL,
        descricao TEXT NOT NULL,
        preco REAL NOT NULL,
        imagem_url TEXT,
        estoque INTEGER DEFAULT 10,
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cliente TEXT NOT NULL,
        email_cliente TEXT NOT NULL,
        telefone TEXT NOT NULL,
        endereco TEXT NOT NULL,
        cupcake_nome TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        valor_total REAL NOT NULL,
        status TEXT DEFAULT 'Recebido',
        observacao TEXT,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Inserir dados padrão de cupcakes caso esteja vazio
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO categorias (nome, descricao) VALUES ('Clássicos', 'Linha tradicional gourmet')")
        cursor.execute("INSERT INTO categorias (nome, descricao) VALUES ('Especiais', 'Ingredientes nobres e importados')")
        
        cupcakes_iniciais = [
            (1, "Red Velvet Cremoso", "Massa aveludada de cacau com recheio de cream cheese suave", 14.50, "https://images.unsplash.com/photo-1614707267537-b85aaf00c4b7?w=400", 25),
            (1, "Chocolatudo Belga", "Massa 70% cacau recheada com ganache de chocolate belga e brigadeiro", 15.00, "https://images.unsplash.com/photo-1576618148400-f54bed99fcfd?w=400", 30),
            (2, "Pistache & Framboesa", "Pão de ló leve com brigadeiro de pistache iraniano e geleia de framboesa", 17.50, "https://images.unsplash.com/photo-1587668178277-295251f900ce?w=400", 15),
            (2, "Doce de Leite com Nozes", "Massa fofa de canela com recheio de doce de leite artesanal argentino", 13.90, "https://images.unsplash.com/photo-1599785209707-a456fc1337bb?w=400", 20)
        ]
        cursor.executemany("INSERT INTO produtos (categoria_id, nome, descricao, preco, imagem_url, estoque) VALUES (?, ?, ?, ?, ?, ?)", cupcakes_iniciais)
        
    conn.commit()
    conn.close()

def get_produtos():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def get_produto_por_id(p_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (p_id,))
    produto = cursor.fetchone()
    conn.close()
    return produto

def salvar_pedido(nome, email, telefone, endereco, cupcake_nome, quantidade, valor_total, observacao=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO pedidos (nome_cliente, email_cliente, telefone, endereco, cupcake_nome, quantidade, valor_total, observacao)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, email, telefone, endereco, cupcake_nome, quantidade, valor_total, observacao))
    pedido_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return pedido_id

def get_pedidos():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos ORDER BY id DESC")
    pedidos = cursor.fetchall()
    conn.close()
    return pedidos

# ==================== CONTROLLER ====================
@app.route("/")
def index():
    produtos = get_produtos()
    return render_template("index.html", produtos=produtos)

@app.route("/comprar/<int:produto_id>", methods=["GET", "POST"])
def comprar(produto_id):
    produto = get_produto_por_id(produto_id)
    if not produto:
        flash("Produto não encontrado!", "danger")
        return redirect(url_for("index"))
        
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        telefone = request.form.get("telefone")
        endereco = request.form.get("endereco")
        quantidade = int(request.form.get("quantidade", 1))
        observacao = request.form.get("observacao", "")
        
        if not nome or not email or not endereco:
            flash("Por favor, preencha todos os campos obrigatórios!", "warning")
            return render_template("checkout.html", produto=produto)
            
        valor_total = quantidade * produto["preco"]
        pedido_id = salvar_pedido(nome, email, telefone, endereco, produto["nome"], quantidade, valor_total, observacao)
        flash("Pedido realizado com sucesso! Agradecemos a preferência.", "success")
        return redirect(url_for("rastreio", pedido_id=pedido_id))
        
    return render_template("checkout.html", produto=produto)

@app.route("/rastreio/<int:pedido_id>")
def rastreio(pedido_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
    pedido = cursor.fetchone()
    conn.close()
    return render_template("rastreio.html", pedido=pedido)

@app.route("/admin/pedidos")
def admin_pedidos():
    pedidos = get_pedidos()
    return render_template("admin.html", pedidos=pedidos)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
