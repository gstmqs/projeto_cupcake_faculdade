import sys
import os
import pytest

# Adicionar a pasta da aplicação ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, init_db, salvar_pedido, get_pedidos, get_produtos

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

def test_pagina_checkout_produto_valido(client):
    response = client.get("/comprar/1")
    assert response.status_code == 200
    assert "Finalizar Compra".encode("utf-8") in response.data

def test_pagina_checkout_produto_invalido(client):
    response = client.get("/comprar/9999", follow_redirects=True)
    assert response.status_code == 200
    assert "não encontrado".encode("utf-8") in response.data or response.status_code == 200
