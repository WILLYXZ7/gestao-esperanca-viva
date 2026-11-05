# Sistema de Gestão Comunitária de Doações e Atendimentos

[![CI - Integracao Continua e Testes Automatizados](https://github.com/WILLYXZ7/gestao-esperanca-viva/actions/workflows/ci.yml/badge.svg)](https://github.com/WILLYXZ7/gestao-esperanca-viva/actions)
![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)
![Framework](https://img.shields.io/badge/framework-Flask%203.0-lightgrey.svg)
![ODS 2](https://img.shields.io/badge/ODS-2%20Fome%20Zero-green.svg)
![WCAG AA](https://img.shields.io/badge/Acessibilidade-WCAG%202.1%20AA-orange.svg)

MVP acadêmico desenvolvido para a disciplina de **Projeto de Software (Experiência Prática III: Engenharia de Software Colaborativa)**, em atendimento à demanda real da **Associação Comunitária Esperança Viva** (Bairro São Pedro).

---

## 📌 Contexto e Problema Social

A Associação Comunitária Esperança Viva acolhe aproximadamente **120 famílias em situação de vulnerabilidade socioeconômica**. Anteriormente, o controle de entregas de cestas básicas e o estoque de alimentos doados eram gerenciados manualmente em fichas de papel e cadernos físicos. Esse modelo manual gerava:
1. **Filas extensas e tempo de espera excessivo** no balcão de atendimento;
2. **Risco de perdas de alimentos doados** por falta de monitoramento visual dos prazos de validade (comprometendo a meta do **ODS 2 — Fome Zero e Agricultura Sustentável**);
3. **Falta de equidade na distribuição**, devido à dificuldade em verificar duplicidades de entregas manuais no mesmo mês.

Esta aplicação resolve essas dores através de um fluxo ágil, seguro e acessível.

---

## 🏗️ Arquitetura e Padrão Tecnológico

O sistema adota o padrão **Monolítico em Camadas (baseado no padrão MVC)**:

* **Camada de Apresentação (View):** Templates Jinja2 com interface responsiva mobile-first construída em Bootstrap 5.3, cumprindo as diretrizes de acessibilidade **WCAG 2.1 nível AA** (áreas de toque $\ge 44 \times 44$ px, contraste mínimo de 4.5:1 e redundância visual de cor + ícone + texto).
* **Camada de Aplicação / Negócio (Controller & Services):** Rotas Flask e serviços desacoplados (`AuthService`, `AtendimentoService`, `EstoqueService`, `FamiliaService`). A trava de duplicidade mensal e o algoritmo de cálculo de validade residem exclusivamente nesta camada.
* **Camada de Persistência (Model):** Mapeamento Objeto-Relacional com SQLAlchemy 2.0, com suporte a SQLite para testes e desenvolvimento rápido e PostgreSQL para produção em nuvem.

### Estrutura de Diretórios

```text
gestao-esperanca-viva/
├── .github/
│   └── workflows/
│       └── ci.yml            # Pipeline de Integração Contínua (GitHub Actions)
├── app/
│   ├── __init__.py           # Application Factory e inicialização do banco
│   ├── models.py             # Modelos de dados (User, Familia, ItemDoacao, Atendimento)
│   ├── services.py           # Regras de negócio (trava mensal, cálculo de validade, hash)
│   ├── routes.py             # Rotas web protegidas e controllers
│   ├── static/
│   │   └── css/style.css     # Estilos acessíveis (WCAG AA, foco visível e touch targets)
│   └── templates/
│       ├── base.html         # Layout base institucional com navbar acessível
│       ├── login.html        # Tela 1: Entrada Principal e Autenticação
│       ├── atendimento.html  # Tela 2: Atendimento e Baixa de Cestas
│       └── estoque.html      # Tela 3: Monitoramento de Validades e Alertas
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Fixtures do pytest (banco em memória e cliente de teste)
│   ├── test_services.py      # Testes unitários das regras de negócio
│   └── test_routes.py        # Testes de integração das rotas e fluxos
├── .gitignore
├── requirements.txt
├── run.py                    # Ponto de entrada da aplicação
└── README.md
```

---

## 🎯 Requisitos Implementados

| Identificador | Tipo | Descrição |
|---|---|---|
| **RF01** | Funcional | Localização rápida de famílias beneficiárias por CPF ou Nome no balcão. |
| **RF02** | Funcional | Registro de entrega de cesta básica com **trava automática e impeditiva de duplicidade no mesmo mês civil**. |
| **RF03** | Funcional | Painel de controle de estoque com **alertas semânticos de validade** (crítico $\le 7$ dias, regular e vencido). |
| **RNF01** | Não Funcional | Segurança e autenticação com hash criptográfico unidirecional (sem armazenamento em texto limpo). |
| **RNA01** | Acessibilidade | Touch targets $\ge 44$ px, contraste WCAG AA, foco visual destacado e redundância semântica (cor, ícone e texto). |

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
* Python 3.10 ou superior
* Git instalado

### Passo a Passo

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/WILLYXZ7/gestao-esperanca-viva.git
   cd gestao-esperanca-viva
   ```

2. **Criar e ativar o ambiente virtual (opcional, mas recomendado):**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Executar a aplicação:**
   ```bash
   python run.py
   ```
   Acesse a aplicação no navegador em: `http://127.0.0.1:5000`

### Credenciais de Demonstração (Seed inicial):
* **E-mail:** `regina.alves@esperancaviva.org`
* **Senha:** `Esperanca@2026`

---

## 🧪 Testes Automatizados

O projeto conta com suíte de testes unitários e de integração utilizando **pytest**, cobrindo o algoritmo de trava de duplicidade, cálculo de validades e fluxos de navegação e autenticação.

Para executar todos os testes localmente:
```bash
pytest -v
```

---

## 🔄 Integração Contínua (CI)

O repositório possui uma esteira automatizada configurada via **GitHub Actions** (`.github/workflows/ci.yml`). A cada `push` ou `pull request` nos branches `main` ou `develop`, o pipeline executa:
1. Instalação limpa de dependências;
2. Análise estática de código com linter **Flake8**;
3. Execução completa da suíte de testes automatizados com **pytest**.

---

## 👥 Colaboradores e Licença

Desenvolvido para fins acadêmicos e comunitários em parceria com a **Associação Comunitária Esperança Viva**.  
Licença MIT.

