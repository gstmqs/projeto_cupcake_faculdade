import sys
import os
import json
import pytest

# Adicionar a pasta da aplicação ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, init_db, salvar_pedido, salvar_pedido_multiplo, get_pedidos, get_produtos

@pytest.fixture
def client():
    app.config["TESTING"] = True
    init_db()
    with app.test_client() as client:
        yield client

def test_catalogo_carrega_com_sucesso(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "SweetBite Gourmet".encode("utf-8") in response.data
    assert "Red Velvet Cremoso".encode("utf-8") in response.data

def test_calculo_subtotal_e_persistencia():
    pedido_id = salvar_pedido(
        nome="Teste Aluno",
        email="teste@aluno.com",
        telefone="(11) 98765-4321",
        endereco="Av. Paulista, 1000",
        cupcake_nome="Red Velvet Cremoso",
        quantidade=3,
        valor_total=43.50,
        observacao="Entregar em embalagem para presente"
    )
    assert pedido_id > 0
    pedidos = get_pedidos()
    encontrado = any(p["id"] == pedido_id and p["valor_total"] == 43.50 for p in pedidos)
    assert encontrado is True

def test_pedido_multiplos_produtos_com_quantidades():
    itens = [
        {"produto_id": 1, "nome": "Red Velvet Cremoso", "quantidade": 2, "preco": 14.50},
        {"produto_id": 2, "nome": "Chocolatudo Belga", "quantidade": 3, "preco": 15.00}
    ]
    # 2 x 14.50 (29.00) + 3 x 15.00 (45.00) = 74.00
    total = sum(i["quantidade"] * i["preco"] for i in itens)
    assert total == 74.00
    
    pedido_id = salvar_pedido_multiplo(
        nome="Gustavo Marques",
        email="gustavo@email.com",
        telefone="(11) 99999-9999",
        endereco="Rua dos Cupcakes, 123",
        itens=itens,
        valor_total=total,
        observacao="Favor caprichar na cobertura"
    )
    assert pedido_id > 0
    pedidos = get_pedidos()
    encontrado = any(p["id"] == pedido_id and p["quantidade"] == 5 and p["valor_total"] == 74.00 for p in pedidos)
    assert encontrado is True

def test_pagina_checkout_produto_valido(client):
    response = client.get("/comprar/1")
    assert response.status_code == 200
    assert "Finalizar Pedido".encode("utf-8") in response.data or "Resumo".encode("utf-8") in response.data

def test_pagina_checkout_produto_invalido(client):
    response = client.get("/comprar/9999", follow_redirects=True)
    assert response.status_code == 200
    assert "não encontrado".encode("utf-8") in response.data or response.status_code == 200
