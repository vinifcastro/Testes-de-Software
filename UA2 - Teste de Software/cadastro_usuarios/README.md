# Cadastro de Usuários — UA2 (Plano de Teste Funcional)

Sistema web simples (Flask + SQLite) para **Cadastro de Usuários** com validações server-side e **roteiro de testes CT1..CT20**. Este projeto atende à **UA2**: elaborar um **Plano de Teste Funcional** com execução baseada em **integridade de atributos** e **classes de equivalência**, além de prover um sistema executável para realizar os testes.

---

## 🎯 Objetivo da Atividade

1. **Plano de Teste Funcional** (CT1..CT20) cobrindo:
   - `nome`, `email`, `senha`, `confirmar_senha`, `cpf`, `data_nascimento`, `telefone`, `cep`, `renda_mensal`, `aceite_termos`.
   - Casos **válidos**, **inválidos** e **limites**, com **Saída Esperada** e campos para **Saída Obtida** e **Status**.
2. **Implementação do Sistema** para executar o plano:
   - Formulário com validação por campo (borda vermelha + mensagem).
   - Persistência em **SQLite** (dados permanecem após encerrar).
   - **Listagem** com busca e paginação.
   - **Launcher cross-platform** (`run.py`) para rodar em Windows e Linux/macOS.

---

## 🧱 Estrutura do Projeto

```
cadastro_usuarios/
├─ app.py                # App Flask (rotas, validação, persistência)
├─ run.py                # Launcher cross-platform (instala deps, cria DB e roda)
├─ requirements.txt      # Dependências do Python
├─ schema.sql            # Esquema do banco (tabela users)
├─ templates/
│  ├─ base.html          # Layout base (Bootstrap + seu CSS)
│  ├─ register.html      # Formulário de cadastro (erros por campo)
│  ├─ success.html       # Tela de sucesso
│  └─ users.html         # Listagem com busca e paginação
└─ static/
   └─ styles.css         # Estilos complementares ao Bootstrap
```

---

## ⚙️ Instalação e Execução

> Requisitos: **Python 3.10+**.

### ⭐ Modo recomendado (launcher único)
```bash
# (opcional) ambiente virtual
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

# Executar o launcher
python run.py
```

O `run.py`:
1) identifica o SO (Windows / Linux/macOS),
2) atualiza/instala deps do `requirements.txt`,
3) cria/atualiza o banco via `schema.sql`,
4) inicia o servidor Flask.

Acesse:
- **Cadastro:** http://127.0.0.1:5000/register  
- **Usuários:** http://127.0.0.1:5000/users

### Alternativa manual
```bash
pip install -r requirements.txt
python -c "import app; app.init_db()"
python app.py
```

---

## 🧪 Plano de Testes (CT1..CT20)

O plano cobre as 10 regras funcionais:

| Regra | Campo             | Validação (resumo)                                                                 |
|------:|-------------------|-------------------------------------------------------------------------------------|
| R1    | nome              | Obrigatório; **3–80** chars; letras (com acentos) e espaços                        |
| R2    | email             | Formato de e-mail válido                                                           |
| R3    | senha             | **8–32** chars; deve conter **letras e números**                                   |
| R4    | confirmar_senha   | Igual à senha                                                                      |
| R5    | cpf               | 11 dígitos; **válido por dígitos verificadores**                                   |
| R6    | data_nascimento   | Usuário **≥ 18 anos**                                                              |
| R7    | telefone (opc.)   | Se informado, **10–11 dígitos**                                                    |
| R8    | cep               | **8 dígitos** (com ou sem máscara `00000-000`)                                     |
| R9    | renda_mensal      | Número **≥ 0** com **até 2 casas decimais** (ponto como separador)                 |
| R10   | aceite_termos     | Obrigatório (checkbox marcado)                                                     |

> O documento **ua2_vinicius_202103783.md** (ou o PDF gerado) contém **CT1..CT20** com **Dados de Entrada, Passos e Saída Esperada**.
> Durante a execução, preencha **Saída Obtida** e **Status (OK/ERRO)** e anexe **prints** como evidência.

---

## 🧩 Como o Código Está Organizado

### Rotas principais (`app.py`)
- `GET /` → redireciona para `/register`
- `GET /register` → formulário de cadastro
- `POST /register` → valida campos e **insere** no SQLite; erros por campo com `.is-invalid`
- `GET /success` → confirmação de cadastro
- `GET /users` → listagem com **busca** (`?q=` nome/email/CPF) e **paginação** (`?page=`)

### Validações (server-side)
- Regex e funções utilitárias (`NAME_RE`, `EMAIL_RE`, `CEP_RE`, `TEL_RE`, `RENDA_RE`).
- `validar_cpf()` implementa o **cálculo dos dígitos**.
- `maior_de_idade()` calcula a idade (≥ 18).
- Erros são retornados ao template como dict `errors` e exibidos com **Bootstrap** (`.is-invalid` + `.invalid-feedback`).

### Persistência (SQLite)
- Banco: `cadastro.db` (arquivo local, **persiste** após encerrar).
- Esquema: `schema.sql` (CREATE TABLE IF NOT EXISTS).
- **Unicidade** de `email` e `cpf`.

### Listagem (`/users`)
- Busca por nome/email/CPF.
- Paginação (20 por página).
- Filtros Jinja para formatar **CPF, telefone, valor monetário e data**.

---

## 🔍 Testando os Casos

1. Abra `/register`, preencha conforme cada **CT** (ex.: CPF inválido, senha sem números, etc.).
2. Verifique a **mensagem de erro** por campo (borda vermelha + texto) ou sucesso.
3. Registre no seu **Plano de Teste** a **Saída Obtida** e marque **Status**.
4. Use `/users` para confirmar cadastros válidos gravados.

---

## 🧰 Dicas e Solução de Problemas

- **404 em `/base`**  
  `base.html` é um **layout**, não uma rota. Use `/register` ou `/users`.
- **Porta ocupada**  
  Troque a porta:
  ```bash
  # Linux/macOS
  FLASK_RUN_PORT=5050 python app.py
  # Windows
  set FLASK_RUN_PORT=5050 && python app.py
  ```
- **Resetar a base**  
  Apague o arquivo `cadastro.db` ou rode:
  ```sql
  DELETE FROM users;
  VACUUM;
  ```
- **Segurança (nota didática)**  
  Senhas estão com **SHA-256** simples (suficiente para a atividade). Em produção, use **bcrypt/argon2** com salt e custo; adicione CSRF e validação client-side.

---

## ✅ Entregáveis Sugeridos

- `README.md` (este arquivo)  
- `ua2_vinicius_202103783.md` (o plano em Markdown com CT1..CT20)  
- Código completo (`app.py`, `templates/`, `static/`, `schema.sql`, `run.py`)  
- PDF do Plano de Teste

---

## 📄 Licença
Uso acadêmico/educacional. Ajuste conforme sua necessidade.
