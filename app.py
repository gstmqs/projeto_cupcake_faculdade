"""
SweetBite Gourmet - Sistema E-Commerce de Cupcakes
Projeto Integrador Transdisciplinar em Engenharia de Software II (PIT II)
Estudante: Gustavo Marques de Almeida (RGM: 35691042)
Arquitetura: MVC (Model-View-Controller)
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import json
import re

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
        cep TEXT DEFAULT '',
        endereco TEXT NOT NULL,
        forma_pagamento TEXT DEFAULT 'PIX',
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

    # Garantir colunas novas caso o banco já existisse de versão anterior
    cursor.execute("PRAGMA table_info(pedidos)")
    colunas_pedidos = [col[1] for col in cursor.fetchall()]
    if "cep" not in colunas_pedidos:
        cursor.execute("ALTER TABLE pedidos ADD COLUMN cep TEXT DEFAULT ''")
    if "forma_pagamento" not in colunas_pedidos:
        cursor.execute("ALTER TABLE pedidos ADD COLUMN forma_pagamento TEXT DEFAULT 'PIX'")

    # Inserir categorias e cupcakes iniciais
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        categorias_iniciais = [
            ("Clássicos", "Linha tradicional gourmet com receitas consagradas"),
            ("Especiais", "Ingredientes nobres, importados e combinações autorais"),
            ("Veganos", "100% origem vegetal, zero lactose e sem ingredientes de origem animal")
        ]
        cursor.executemany("INSERT INTO categorias (nome, descricao) VALUES (?, ?)", categorias_iniciais)

    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        cupcakes_iniciais = [
            (1, "Red Velvet Cremoso", "Massa aveludada de cacau com recheio e cobertura de cream cheese artesanal", 14.50, "https://images.unsplash.com/photo-1614707267537-b85aaf00c4b7?w=400", 25),
            (1, "Chocolatudo Belga", "Massa 70% cacau recheada com ganache de chocolate belga e brigadeiro", 15.00, "https://images.unsplash.com/photo-1576618148400-f54bed99fcfd?w=400", 30),
            (2, "Pistache & Framboesa", "Pão de ló leve com brigadeiro de pistache iraniano e geleia artesanal de framboesa", 17.50, "https://images.unsplash.com/photo-1587668178277-295251f900ce?w=400", 15),
            (2, "Doce de Leite com Nozes", "Massa fofa de especiarias com doce de leite argentino e nozes caramelizadas", 13.90, "https://images.unsplash.com/photo-1599785209707-a456fc1337bb?w=400", 20),
            (3, "Cacau & Coco Vegano", "Massa funcional de cacau orgânico com leite de coco e ganache vegana zero lactose", 16.00, "https://images.unsplash.com/photo-1550617931-e17a7b70dce2?w=400", 18)
        ]
        cursor.executemany(
            "INSERT INTO produtos (categoria_id, nome, descricao, preco, imagem_url, estoque) VALUES (?, ?, ?, ?, ?, ?)",
            cupcakes_iniciais
        )
    else:
        # Garantir que a categoria Veganos e o 5º cupcake existam se o banco foi criado antes
        cursor.execute("SELECT id FROM categorias WHERE nome = 'Veganos'")
        cat_veg = cursor.fetchone()
        if not cat_veg:
            cursor.execute("INSERT INTO categorias (nome, descricao) VALUES ('Veganos', '100% origem vegetal e zero lactose')")
            cat_veg_id = cursor.lastrowid
        else:
            cat_veg_id = cat_veg[0]

        cursor.execute("SELECT COUNT(*) FROM produtos WHERE nome = 'Cacau & Coco Vegano'")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO produtos (categoria_id, nome, descricao, preco, imagem_url, estoque) VALUES (?, ?, ?, ?, ?, ?)",
                (cat_veg_id, "Cacau & Coco Vegano", "Massa funcional de cacau orgânico com leite de coco e ganache vegana zero lactose", 16.00, "https://images.unsplash.com/photo-1550617931-e17a7b70dce2?w=400", 18)
            )

    conn.commit()
    conn.close()


def get_categorias():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categorias ORDER BY id")
    categorias = cursor.fetchall()
    conn.close()
    return categorias


def get_produtos(categoria_id=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if categoria_id:
        cursor.execute("""
            SELECT p.*, c.nome as categoria_nome
            FROM produtos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.categoria_id = ?
            ORDER BY p.id
        """, (categoria_id,))
    else:
        cursor.execute("""
            SELECT p.*, c.nome as categoria_nome
            FROM produtos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            ORDER BY p.id
        """)
    produtos = cursor.fetchall()
    conn.close()
    return produtos


def get_produto_por_id(p_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, c.nome as categoria_nome
        FROM produtos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.id = ?
    """, (p_id,))
    produto = cursor.fetchone()
    conn.close()
    return produto


def validar_cep(cep_str):
    """Valida se o CEP possui exatamente 8 dígitos numéricos (com ou sem hífen)"""
    if not cep_str:
        return True  # Opcional se o endereço já contiver o CEP, mas se preenchido deve ter 8 dígitos
    apenas_digitos = re.sub(r"\D", "", cep_str)
    return len(apenas_digitos) == 8


def salvar_pedido(nome, email, telefone, endereco, cupcake_nome, quantidade, valor_total, observacao="", cep="", forma_pagamento="PIX"):
    if int(quantidade) < 1:
        raise ValueError("A quantidade deve ser de no mínimo 1 unidade.")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO pedidos (nome_cliente, email_cliente, telefone, cep, endereco, forma_pagamento, cupcake_nome, quantidade, valor_total, observacao)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, email, telefone, cep, endereco, forma_pagamento, cupcake_nome, int(quantidade), round(float(valor_total), 2), observacao))
    pedido_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return pedido_id


def salvar_pedido_multiplo(nome, email, telefone, endereco, itens, valor_total, observacao="", cep="", forma_pagamento="PIX"):
    """Salva pedido com múltiplos itens e suas respectivas quantidades"""
    itens_validos = [i for i in itens if int(i.get("quantidade", 0)) >= 1]
    if not itens_validos:
        raise ValueError("O pedido deve conter ao menos 1 item com quantidade positiva.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    descricao_itens = ", ".join([f"{item['quantidade']}x {item['nome']}" for item in itens_validos])
    qtd_total = sum(int(item["quantidade"]) for item in itens_validos)

    cursor.execute("""
    INSERT INTO pedidos (nome_cliente, email_cliente, telefone, cep, endereco, forma_pagamento, cupcake_nome, quantidade, valor_total, observacao)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, email, telefone, cep, endereco, forma_pagamento, descricao_itens, qtd_total, round(float(valor_total), 2), observacao))
    pedido_id = cursor.lastrowid

    for item in itens_validos:
        cursor.execute("""
        INSERT INTO itens_pedido (pedido_id, produto_id, nome_produto, quantidade, preco_unitario)
        VALUES (?, ?, ?, ?, ?)
        """, (pedido_id, item["produto_id"], item["nome"], int(item["quantidade"]), float(item["preco"])))

    conn.commit()
    conn.close()
    return pedido_id


def atualizar_status_pedido(pedido_id, novo_status):
    status_permitidos = ["Recebido", "Em Produção", "Saiu para Entrega", "Entregue", "Cancelado"]
    if novo_status not in status_permitidos:
        raise ValueError("Status inválido.")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    conn.commit()
    conn.close()


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
    categoria_id = request.args.get("categoria", type=int)
    categorias = get_categorias()
    produtos = get_produtos(categoria_id=categoria_id)
    return render_template("index.html", produtos=produtos, categorias=categorias, categoria_selecionada=categoria_id)


@app.route("/checkout", methods=["GET", "POST"])
def checkout_carrinho():
    produtos = get_produtos()

    if request.method == "POST":
        # POST final de confirmação de compra com dados do cliente
        if "confirmar_compra" in request.form:
            nome = request.form.get("nome", "").strip()
            email = request.form.get("email", "").strip()
            telefone = request.form.get("telefone", "").strip()
            cep = request.form.get("cep", "").strip()
            endereco = request.form.get("endereco", "").strip()
            forma_pagamento = request.form.get("forma_pagamento", "PIX")
            observacao = request.form.get("observacao", "").strip()
            itens_json = request.form.get("itens_json", "[]")

            try:
                itens = json.loads(itens_json)
            except Exception:
                itens = []

            if not itens:
                flash("Carrinho vazio! Selecione ao menos um cupcake.", "warning")
                return redirect(url_for("index"))

            valor_total = round(sum(int(item["quantidade"]) * float(item["preco"]) for item in itens), 2)
            dados_form = {
                "nome": nome,
                "email": email,
                "telefone": telefone,
                "cep": cep,
                "endereco": endereco,
                "forma_pagamento": forma_pagamento,
                "observacao": observacao
            }

            if not nome or not email or not endereco:
                flash("Por favor, preencha todos os campos obrigatórios de entrega!", "danger")
                return render_template("checkout.html", itens=itens, valor_total=valor_total, itens_json=json.dumps(itens), form_data=dados_form)

            if cep and not validar_cep(cep):
                flash("CEP inválido! Informe um CEP válido com 8 dígitos (ex: 01310-100). Seus dados foram mantidos.", "danger")
                return render_template("checkout.html", itens=itens, valor_total=valor_total, itens_json=json.dumps(itens), form_data=dados_form)

            pedido_id = salvar_pedido_multiplo(
                nome, email, telefone, endereco, itens, valor_total,
                observacao=observacao, cep=cep, forma_pagamento=forma_pagamento
            )
            flash("Pedido realizado com sucesso! Seus cupcakes já estão sendo preparados.", "success")
            return redirect(url_for("rastreio", pedido_id=pedido_id))

        # POST vindo do catálogo com as quantidades selecionadas
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

        valor_total = round(sum(item["subtotal"] for item in itens), 2)
        return render_template("checkout.html", itens=itens, valor_total=valor_total, itens_json=json.dumps(itens), form_data={})

    return redirect(url_for("index"))


@app.route("/comprar/<int:produto_id>", methods=["GET", "POST"])
def comprar(produto_id):
    """Permite comprar um produto específico ou iniciar o checkout com 1 unidade selecionada"""
    produto = get_produto_por_id(produto_id)
    if not produto:
        flash("Produto não encontrado!", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        telefone = request.form.get("telefone", "").strip()
        cep = request.form.get("cep", "").strip()
        endereco = request.form.get("endereco", "").strip()
        forma_pagamento = request.form.get("forma_pagamento", "PIX")
        observacao = request.form.get("observacao", "").strip()
        try:
            quantidade = int(request.form.get("quantidade", 1))
        except ValueError:
            quantidade = 0

        if quantidade < 1:
            flash("A quantidade deve ser de no mínimo 1 unidade!", "danger")
            return redirect(url_for("comprar", produto_id=produto_id))

        itens = [{
            "produto_id": produto["id"],
            "nome": produto["nome"],
            "descricao": produto["descricao"],
            "preco": produto["preco"],
            "imagem_url": produto["imagem_url"],
            "quantidade": quantidade,
            "subtotal": round(quantidade * produto["preco"], 2)
        }]
        valor_total = round(quantidade * produto["preco"], 2)
        dados_form = {
            "nome": nome, "email": email, "telefone": telefone,
            "cep": cep, "endereco": endereco, "forma_pagamento": forma_pagamento, "observacao": observacao
        }

        if not nome or not email or not endereco:
            flash("Por favor, preencha todos os campos obrigatórios!", "warning")
            return render_template("checkout.html", itens=itens, valor_total=valor_total, itens_json=json.dumps(itens), form_data=dados_form)

        if cep and not validar_cep(cep):
            flash("CEP inválido! Informe um CEP com 8 dígitos numéricos.", "danger")
            return render_template("checkout.html", itens=itens, valor_total=valor_total, itens_json=json.dumps(itens), form_data=dados_form)

        pedido_id = salvar_pedido(
            nome, email, telefone, endereco, produto["nome"], quantidade, valor_total,
            observacao=observacao, cep=cep, forma_pagamento=forma_pagamento
        )
        flash("Pedido realizado com sucesso! Agradecemos a preferência.", "success")
        return redirect(url_for("rastreio", pedido_id=pedido_id))

    itens = [{
        "produto_id": produto["id"],
        "nome": produto["nome"],
        "descricao": produto["descricao"],
        "preco": produto["preco"],
        "imagem_url": produto["imagem_url"],
        "quantidade": 1,
        "subtotal": produto["preco"]
    }]
    return render_template("checkout.html", itens=itens, valor_total=produto["preco"], itens_json=json.dumps(itens), form_data={})


@app.route("/rastreio/<int:pedido_id>")
def rastreio(pedido_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
    pedido = cursor.fetchone()
    conn.close()
    if not pedido:
        flash("Pedido não localizado!", "warning")
        return redirect(url_for("index"))
    return render_template("rastreio.html", pedido=pedido)


@app.route("/admin/pedidos")
def admin_pedidos():
    pedidos = get_pedidos()
    return render_template("admin.html", pedidos=pedidos)


@app.route("/admin/pedido/<int:pedido_id>/status", methods=["POST"])
def admin_alterar_status(pedido_id):
    novo_status = request.form.get("status", "Recebido")
    try:
        atualizar_status_pedido(pedido_id, novo_status)
        flash(f"Status do pedido #{pedido_id} atualizado para '{novo_status}'!", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin_pedidos"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
