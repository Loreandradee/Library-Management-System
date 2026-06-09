# 📚 Library Management System

Sistema de Gerenciamento de Biblioteca com interface gráfica moderna em Python usando Tkinter e SQLite.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Funcionalidades

| Módulo | Funcionalidades |
|--------|-----------------|
| 📚 **Livros** | Adicionar, editar, excluir, buscar, gerenciar cópias |
| 👥 **Empréstimos** | Emprestar, devolver, cálculo de multa (R$2/dia) |
| 📊 **Estatísticas** | Total de livros, cópias, emprestados, disponíveis |
| 🎨 **Interface** | Modo claro/escuro, notificações toast, cards modernos |
| ⌨️ **Atalhos** | Teclas de atalho para todas as ações principais |

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/Library-Management-System.git
cd Library-Management-System

# 2. Instale as dependências
pip install bcrypt pytest pillow

# 3. Execute o sistema
python trinity.py
```
## 📦 Dependências
```bash
bcrypt==4.0.1    # Criptografia de senhas
pytest==7.4.0    # Testes automatizados
pillow==10.0.0   # Processamento de imagens
```

## 🔐 Credenciais de Acesso

| Usuário | Senha |
|--------|-----------------|
| lorena | 1234 |
| Prakarsha | root |

## ⌨️ Atalhos de Teclado
``` bash
Atalho	Ação
Ctrl + B	Abrir Gerenciamento de Livros
Ctrl + E	Abrir Gerenciamento de Empréstimos
Ctrl + L	Voltar para Tela de Login
Ctrl + S	Abrir Configurações
Ctrl + D	Alternar Tema (Claro/Escuro)
Delete	Excluir livro selecionado
F1	Abrir Ajuda
```

## 📁 Estrutura do Projeto
``` bash
Library-Management-System/
│
├── 📄 trinity.py              # Aplicação principal (interface completa)
├── 📄 service.py              # Camada de serviços/lógica de negócio
├── 📄 repository.py           # Camada de acesso ao banco de dados
│
├── 🧪 test_service.py         # Testes unitários
├── 🧪 test_integration.py     # Testes de integração
├── 🧪 conftest.py             # Configuração dos testes
│
├── 🗄️ test.db                 # Banco de dados principal (automático)
├── 🗄️ python1.db              # Banco de dados de login (automático)
├── ⚙️ settings.json           # Configurações do usuário
│
├── 📦 requirements.txt        # Dependências do projeto
├── 📁 screenshots/            # Imagens da demonstração
│
└── 📄 README.md               # Este arquivo
```

## 🧪 Executando os Testes
```bash
# Executar todos os testes
pytest -v

# Executar testes unitários apenas
pytest test_service.py -v

# Executar testes de integração apenas
pytest test_integration.py -v

# Executar com relatório detalhado
pytest -v --tb=short
```

## 🚀 Telas antes de qualquer alteração

| Login | Dashboard |
|-------|-----------|
| ![Login](screenshots/1.jpg) | ![Home](screenshots/2.jpg) |

| Livros | Empréstimos |
|--------|-------------|
| ![Books](screenshots/3.jpg) | ![Loans](screenshots/5.jpg) |
| ![Books Table](screenshots/4.jpg) | ![Activity](screenshots/6.jpg) |


OBS: Estavamos usando a conta da Vanu, porque não estava dando certo na minha conta para subir os commits. A maioria dos códicos foi desenvollvido no VS Code e posteriormente integrado ao Git

