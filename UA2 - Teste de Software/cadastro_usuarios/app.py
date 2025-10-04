from flask import Flask, render_template, request, redirect, url_for
import re, sqlite3, hashlib
from datetime import date, datetime
from math import ceil

DB_PATH = "cadastro.db"

app = Flask(__name__)
app.secret_key = "dev-secret"  # troque em produção

# ---------- Filtros/formatadores Jinja ----------

@app.template_filter("mask_cpf")
def mask_cpf(value: str):
    s = re.sub(r"\D", "", value or "")
    if len(s) != 11:
        return value
    return f"{s[0:3]}.{s[3:6]}.{s[6:9]}-{s[9:11]}"

@app.template_filter("mask_tel")
def mask_tel(value: str):
    s = re.sub(r"\D", "", value or "")
    if len(s) == 10:   # (DD) 0000-0000
        return f"({s[:2]}) {s[2:6]}-{s[6:]}"
    if len(s) == 11:   # (DD) 0 0000-0000
        return f"({s[:2]}) {s[2]} {s[3:7]}-{s[7:]}"
    return value

@app.template_filter("fmt_money")
def fmt_money(v):
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return v

@app.template_filter("fmt_date")
def fmt_date(iso_str: str):
    try:
        return datetime.fromisoformat(iso_str).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return iso_str

# ---------- Utilidades de validação ----------

NAME_RE = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ ]{3,80}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CEP_RE = re.compile(r"^\d{8}$|^\d{5}-\d{3}$")
TEL_RE = re.compile(r"^\d{10,11}$")
RENDA_RE = re.compile(r"^\d+(\.\d{1,2})?$")  # ponto como separador decimal

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def validar_cpf(cpf: str) -> bool:
    nums = re.sub(r"\D", "", cpf)
    if len(nums) != 11 or nums == nums[0] * 11:
        return False
    soma = sum(int(nums[i]) * (10 - i) for i in range(9))
    d1 = (soma * 10) % 11
    d1 = 0 if d1 == 10 else d1
    if d1 != int(nums[9]):
        return False
    soma = sum(int(nums[i]) * (11 - i) for i in range(10))
    d2 = (soma * 10) % 11
    d2 = 0 if d2 == 10 else d2
    return d2 == int(nums[10])

def maior_de_idade(iso_date: str) -> bool:
    try:
        y, m, d = map(int, iso_date.split("-"))
        dn = date(y, m, d)
    except Exception:
        return False
    hoje = date.today()
    age = hoje.year - dn.year - ((hoje.month, hoje.day) < (dn.month, dn.day))
    return age >= 18

def normalizar_cep(cep: str) -> str:
    return re.sub(r"\D", "", cep)

def normalizar_tel(tel: str) -> str:
    return re.sub(r"\D", "", tel)

# ---------- DB helpers ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn, open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())

# ---------- Listagem de usuários (com busca/paginação) ----------
def buscar_usuarios(q: str | None, page: int, per_page: int = 20):
    sql = "FROM users WHERE 1=1"
    params = []
    if q:
        sql += " AND (LOWER(nome) LIKE ? OR LOWER(email) LIKE ? OR cpf LIKE ?)"
        qlike = f"%{q.lower()}%"
        params += [qlike, qlike, re.sub(r'\\D', '', q)]
    # total
    with get_conn() as conn:
        total = conn.execute(f"SELECT COUNT(*) {sql}", params).fetchone()[0]
        # paginação
        offset = (page - 1) * per_page
        rows = conn.execute(
            f"SELECT id, nome, email, cpf, data_nascimento, telefone, cep, renda_mensal, created_at "
            f"{sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params + [per_page, offset]
        ).fetchall()
    pages = max(1, ceil(total / per_page))
    return rows, total, pages

# ---------- Rotas ----------
@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("register_form"))

@app.get("/users")
def list_users():
    q = (request.args.get("q") or "").strip()
    try:
        page = max(1, int(request.args.get("page", "1")))
    except ValueError:
        page = 1
    per_page = 20
    users, total, pages = buscar_usuarios(q or None, page, per_page)
    return render_template("users.html", users=users, q=q, page=page, pages=pages, total=total)

@app.route("/register", methods=["GET"])
def register_form():
    return render_template("register.html", form={}, errors={})

@app.route("/register", methods=["POST"])
def register_submit():
    errors = {}
    form = request.form

    nome = (form.get("nome") or "").strip()
    email = (form.get("email") or "").strip()
    senha = form.get("senha") or ""
    confirmar = form.get("confirmar_senha") or ""
    cpf = (form.get("cpf") or "").strip()
    data_nascimento = (form.get("data_nascimento") or "").strip()
    telefone = (form.get("telefone") or "").strip()
    cep = (form.get("cep") or "").strip()
    renda = (form.get("renda_mensal") or "").strip()
    aceite = form.get("aceite_termos")

    # validações…
    if not NAME_RE.match(nome):
        errors["nome"] = "Nome inválido (3–80 chars, apenas letras e espaços)."
    if not EMAIL_RE.match(email):
        errors["email"] = "Formato de e-mail inválido."
    if len(senha) < 8 or len(senha) > 32 or not re.search(r"[A-Za-z]", senha) or not re.search(r"[0-9]", senha):
        errors["senha"] = "Senha deve ter 8–32 chars e conter letras e números."
    if confirmar != senha:
        errors["confirmar_senha"] = "Senhas não conferem."
    if not validar_cpf(cpf):
        errors["cpf"] = "CPF inválido."
    if not maior_de_idade(data_nascimento):
        errors["data_nascimento"] = "Idade mínima 18 anos (YYYY-MM-DD)."

    tel_norm = normalizar_tel(telefone)
    if telefone and not TEL_RE.match(tel_norm):
        errors["telefone"] = "Telefone deve ter 10 ou 11 dígitos (apenas números)."

    cep_norm = normalizar_cep(cep)
    if not CEP_RE.match(cep) and not re.match(r"^\d{8}$", cep_norm):
        errors["cep"] = "CEP deve ter 8 dígitos (00000-000 opcional)."

    if not RENDA_RE.match(renda):
        errors["renda_mensal"] = "Renda deve ser número ≥ 0 com no máximo 2 casas decimais (use ponto)."
    else:
        try:
            renda_val = float(renda)
            if renda_val < 0:
                errors["renda_mensal"] = "Renda deve ser ≥ 0."
        except ValueError:
            errors["renda_mensal"] = "Renda inválida."

    aceite_bool = 1 if aceite == "on" else 0
    if not aceite_bool:
        errors["aceite_termos"] = "É necessário aceitar os termos."

    if errors:
        return render_template("register.html", form=form, errors=errors), 400

    # Persistência
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT email, cpf FROM users WHERE email = ? OR cpf = ?",
            (email, re.sub(r"\D","",cpf))
        )
        row = cur.fetchone()
        if row:
            if row["email"] == email:
                errors["email"] = "Email já cadastrado."
            else:
                errors["cpf"] = "CPF já cadastrado."
            return render_template("register.html", form=form, errors=errors), 409

        senha_hash = hash_password(senha)
        conn.execute(
            """INSERT INTO users (nome, email, senha_hash, cpf, data_nascimento,
                                  telefone, cep, renda_mensal, aceite_termos, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                nome,
                email,
                senha_hash,
                re.sub(r"\D","",cpf),
                data_nascimento,
                tel_norm if telefone else None,
                cep_norm,
                float(renda),
                aceite_bool,
                datetime.utcnow().isoformat()
            )
        )
    return redirect(url_for("success"))

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
