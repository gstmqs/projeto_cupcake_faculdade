"""
SweetBite Gourmet - Sistema E-Commerce de Cupcakes
Projeto Integrador Transdisciplinar em Engenharia de Software II (PIT II)
Estudante: Gustavo Marques de Almeida (RGM: 35691042)
Arquitetura: MVC (Model-View-Controller)
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
import json

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
        estoque INTEGER DEFAULT 20,
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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER NOT NULL,
        produto_id INTEGER NOT NULL,
        nome_produto TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        preco_unitario REAL NOT NULL,
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
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

def salvar_pedido_multiplo(nome, email, telefone, endereco, itens, valor_total, observacao=""):
    """Salva pedido com múltiplos itens e suas respectivas quantidades"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criar descrição resumida ex: "2x Red Velvet Cremoso, 3x Chocolatudo Belga"
    descricao_itens = ", ".join([f"{item['quantidade']}x {item['nome']}" for item in itens])
    qtd_total = sum(item['quantidade'] for item in itens)
    
    cursor.execute("""
    INSERT INTO pedidos (nome_cliente, email_cliente, telefone, endereco, cupcake_nome, quantidade, valor_total, observacao)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, email, telefone, endereco, descricao_itens, qtd_total, valor_total, observacao))
    pedido_id = cursor.lastrowid
    
    for item in itens:
        cursor.execute("""
        INSERT INTO itens_pedido (pedido_id, produto_id, nome_produto, quantidade, preco_unitario)
        VALUES (?, ?, ?, ?, ?)
        """, (pedido_id, item['produto_id'], item['nome'], item['quantidade'], item['preco']))
        
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

@app.route("/checkout", methods=["GET", "POST"])
def checkout_carrinho():
    produtos = get_produtos()
    produtos_dict = {p["id"]: p for p in produtos}
    
    if request.method == "POST":
        # Se for o POST final de confirmação de compra
        if "confirmar_compra" in request.form:
            nome = request.form.get("nome")
            email = request.form.get("email")
            telefone = request.form.get("telefone")
            endereco = request.form.get("endereco")
            observacao = request.form.get("observacao", "")
            itens_json = request.form.get("itens_json")
            
            if not itens_json:
                flash("Carrinho vazio! Selecione ao menos um produto.", "warning")
                return redirect(url_for("index"))
                
            try:
                itens = json.loads(itens_json)
            except Exception:
                itens = []
                
            if not itens:
                flash("Nenhum item selecionado!", "warning")
                return redirect(url_for("index"))
                
            valor_total = sum(item["quantidade"] * item["preco"] for item in itens)
            pedido_id = salvar_pedido_multiplo(nome, email, telefone, endereco, itens, valor_total, observacao)
            flash("Pedido realizado com sucesso! Seus cupcakes já estão sendo preparados.", "success")
            return redirect(url_for("rastreio", pedido_id=pedido_id))
            
        # Se for o POST vindo do catálogo (seleção de quantidades)
        itens = []
        for p in produtos:
            qtd_str = request.form.get(f"qtd_{p['id']}", "0")
            try:
                qtd = int(qtd_str)
            except ValueError:
                qtd = 0
                
            if qtd > 0:
                itens.append({
                    "produto_id": p["id"],
                    "nome": p["nome"],
                    "descricao": p["descricao"],
                    "preco": p["preco"],
                    "imagem_url": p["imagem_url"],
                    "quantidade": qtd,
                    "subtotal": round(qtd * p["preco"], 2)
                })
                
        if not itens:
            flash("Por favor, selecione ao menos 1 unidade de algum cupcake antes de continuar!", "warning")
            return redirect(url_for("index"))
            
        valor_total = sum(item["subtotal"] for item in itens)
        return render_template("checkout.html", itens=itens, valor_total=valor_total, itens_json=json.dumps(itens))
        
    return redirect(url_for("index"))

@app.route("/comprar/<int:produto_id>", methods=["GET", "POST"])
def comprar(produto_id):
    """Permite comprar um produto específico individualmente ou ajustar sua quantidade"""
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
            itens = [{
                "produto_id": produto["id"],
                "nome": produto["nome"],
                "descricao": produto["descricao"],
                "preco": produto["preco"],
                "imagem_url": produto["imagem_url"],
                "quantidade": quantidade,
                "subtotal": round(quantidade * produto["preco"], 2)
            }]
            return render_template("checkout.html", itens=itens, valor_total=round(quantidade * produto["preco"], 2), itens_json=json.dumps(itens))
            
        valor_total = round(quantidade * produto["preco"], 2)
        pedido_id = salvar_pedido(nome, email, telefone, endereco, produto["nome"], quantidade, valor_total, observacao)
        flash("Pedido realizado com sucesso! Agradecemos a preferência.", "success")
        return redirect(url_for("rastreio", pedido_id=pedido_id))
        
    # GET: monta a lista de itens com 1 unidade por padrão
    itens = [{
        "produto_id": produto["id"],
        "nome": produto["nome"],
        "descricao": produto["descricao"],
        "preco": produto["preco"],
        "imagem_url": produto["imagem_url"],
        "quantidade": 1,
        "subtotal": produto["preco"]
    }]
    return render_template("checkout.html", itens=itens, valor_total=produto["preco"], itens_json=json.dumps(itens))

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
