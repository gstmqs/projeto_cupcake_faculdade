# 🧁 SweetBite Gourmet - Sistema E-Commerce de Cupcakes
> **Projeto Integrador Transdisciplinar em Engenharia de Software II (PIT II - 7º Período)**  
> **Estudante:** Gustavo Marques de Almeida  
> **RGM:** 35691042  
> **Instituição:** Universidade Cruzeiro do Sul Virtual  

---

## 📖 Sobre o Projeto
O **SweetBite Gourmet** é uma plataforma e-commerce especializada em cupcakes gourmet e artesanais. Este projeto representa a evolução técnica (Kaizen) e a implementação funcional do planejamento iniciado no PIT I (6º período), que contemplou elicitação ágil de requisitos e backlog Scrum.

Nesta etapa (PIT II), o sistema foi desenvolvido seguindo:
- **Padrão Arquitetural MVC (Model-View-Controller)**;
- **Persistência de Dados Relacional Normalizada (3FN)** em SQLite / SQL DDL ([`docs/schema.sql`](docs/schema.sql));
- **Documentação Técnica e Modelagem UML/Dados** ([`docs/DOCUMENTACAO_PIT_II.md`](docs/DOCUMENTACAO_PIT_II.md));
- **Interface Responsiva Mobile-First** em HTML5, CSS3, JavaScript e Bootstrap 5;
- **Funcionalidades Completas:**
  - Filtro dinâmico por categorias (*Todos os Sabores*, *Clássicos*, *Especiais* e *Veganos*);
  - Seleção de múltiplas unidades de cada sabor diretamente no catálogo (`+` / `−`) com cálculo de subtotal e barra flutuante do carrinho em tempo real;
  - Checkout com validação de CEP (8 dígitos), preservação de dados preenchidos, proteção contra clique duplo e campo para *Instruções Especiais / Cartão de Presente*;
  - Rastreamento do pedido em tempo real (*Recebido -> Em Produção -> Saiu para Entrega -> Entregue*);
  - Painel do Confeiteiro (`/admin/pedidos`) com gestão de pedidos e atualização de status;
- **Desenvolvimento Orientado a Testes** com 8 testes unitários e de integração automatizados (`pytest`).

---

## 🏛️ Arquitetura do Sistema (MVC)

```text
app_sweetbite/
├── app.py                        # Controller (Rotas Flask) e Model (Consultas e Persistência)
├── requirements.txt              # Dependências do projeto
├── docs/                         # Documentação de Engenharia de Software (Desafio 1)
│   ├── DOCUMENTACAO_PIT_II.md    # Escopo Kaizen, Diagramas UML e Dicionário de Dados
│   └── schema.sql                # Script Físico DDL do Banco de Dados Relacional
├── templates/                    # View (Telas HTML dinâmicas com Jinja2)
│   ├── index.html                # Catálogo com filtros por categoria e seleção de unidades
│   ├── checkout.html             # Resumo multi-itens, validação de CEP e conclusão
│   ├── rastreio.html             # Confirmação e linha do tempo de status do pedido
│   └── admin.html                # Painel do confeiteiro com alteração de status
└── tests/                        # Suíte de Testes Automatizados
    └── test_cupcake_app.py       # 8 testes automatizados com PyTest
```

---

## 🚀 Como Executar o Projeto Localmente

### 1. Instalação das dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar a aplicação
```bash
python app.py
```
Acesse no navegador:
- **Loja de Cupcakes:** [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Painel do Confeiteiro:** [http://127.0.0.1:5000/admin/pedidos](http://127.0.0.1:5000/admin/pedidos)

---

## 🧪 Execução dos Testes Automatizados

```bash
python -m pytest tests/test_cupcake_app.py -v
```
*(8 testes automatizados validando catálogo, filtro de categorias, cálculo de múltiplos produtos, validação de CEP, atualização de status no painel administrativo e tratamento de exceções).*
