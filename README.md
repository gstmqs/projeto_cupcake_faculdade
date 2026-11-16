# 🧁 SweetBite Gourmet - Sistema E-Commerce de Cupcakes
> **Projeto Integrador Transdisciplinar em Engenharia de Software II (PIT II - 7º Período)**  
> **Estudante:** Gustavo Marques de Almeida  
> **RGM:** 35691042  
> **Instituição:** Universidade Cruzeiro do Sul Virtual  

---

## 📖 Sobre o Projeto
O **SweetBite Gourmet** é uma plataforma e-commerce especializada em cupcakes gourmet e artesanais. Este projeto representa a evolução técnica e a implementação funcional do planejamento iniciado no PIT I (6º período), que contemplou elicitação ágil de requisitos e backlog Scrum.

Nesta etapa (PIT II), o sistema foi desenvolvido seguindo:
- **Padrão Arquitetural MVC (Model-View-Controller)**;
- **Persistência de Dados Relacional Normalizada** (SQLite / PostgreSQL);
- **Interface Responsiva Mobile-First** em HTML5, CSS3 e Bootstrap 5;
- **Desenvolvimento Orientado a Testes** com suíte de testes automatizados (`pytest`).

---

## 🏛️ Arquitetura do Sistema (MVC)

```text
app_sweetbite/
├── app.py                  # Controller (Rotas Flask) e Model (Consultas e Persistência)
├── requirements.txt        # Dependências do projeto
├── templates/              # View (Telas HTML dinâmicas com Jinja2)
│   ├── index.html          # Catálogo de cupcakes
│   ├── checkout.html       # Formulário de pedido e entrega
│   ├── rastreio.html       # Confirmação e acompanhamento de status
│   └── admin.html          # Painel do confeiteiro para gestão de pedidos
└── tests/                  # Suíte de Testes Automatizados
    └── test_cupcake_app.py # Testes unitários com PyTest
```

---

## 🚀 Como Executar o Projeto Localmente

### 1. Pré-requisitos
- Python 3.10 ou superior instalado;
- Gerenciador de pacotes `pip`.

### 2. Instalação das dependências
No terminal, dentro da pasta do projeto:
```bash
pip install -r requirements.txt
```

### 3. Iniciar a aplicação
```bash
python app.py
```
Acesse no seu navegador:
- **Loja de Cupcakes:** [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Painel Administrativo:** [http://127.0.0.1:5000/admin/pedidos](http://127.0.0.1:5000/admin/pedidos)

---

## 🧪 Execução dos Testes Automatizados

Para executar os testes unitários automatizados e validar as regras de negócio:
```bash
python -m pytest tests/test_cupcake_app.py -v
```

---

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python
- **Framework Web:** Flask (Microframework MVC)
- **Front-end:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco de Dados:** SQLite Relacional
- **Testes de Software:** PyTest
- **Controle de Versão:** Git / GitHub
