-- ============================================================================
-- PROJETO FÍSICO DE BANCO DE DADOS - SWEETBITE GOURMET (PIT II)
-- Estudante: Gustavo Marques de Almeida | RGM: 35691042
-- SGBD: SQLite 3 / Compatível com PostgreSQL e MySQL (3ª Forma Normal - 3FN)
-- ============================================================================

CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT
);

CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    preco REAL NOT NULL CHECK (preco >= 0),
    imagem_url TEXT,
    estoque INTEGER DEFAULT 20 CHECK (estoque >= 0),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_cliente TEXT NOT NULL,
    email_cliente TEXT NOT NULL,
    telefone TEXT NOT NULL,
    cep TEXT DEFAULT '',
    endereco TEXT NOT NULL,
    forma_pagamento TEXT DEFAULT 'PIX',
    cupcake_nome TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade >= 1),
    valor_total REAL NOT NULL CHECK (valor_total >= 0),
    status TEXT DEFAULT 'Recebido',
    observacao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    nome_produto TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade >= 1),
    preco_unitario REAL NOT NULL CHECK (preco_unitario >= 0),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE RESTRICT
);
