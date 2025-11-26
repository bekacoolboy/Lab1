from flask import Flask, request, redirect, url_for, render_template_string, session
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"  # для сессий

# "База данных" в памяти
users = {}  # {phone: {"password": hash, "balance": int}}

# Нормализация номера: оставляем только цифры
def normalize_phone(phone: str) -> str:
    return re.sub(r"\D", "", (phone or "").strip())

# Базовый layout с Bootstrap
base_layout = """
<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Бека Банк</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <a class="navbar-brand" href="{{ url_for('home') }}">Бека Банк</a>
        <div class="ms-auto">
          {% if session.get('phone') %}
            <span class="navbar-text me-3">Вы: {{ session.get('phone') }}</span>
            <a class="btn btn-outline-light btn-sm" href="{{ url_for('logout') }}">Выйти</a>
          {% else %}
            <a class="btn btn-outline-light btn-sm me-2" href="{{ url_for('register') }}">Регистрация</a>
            <a class="btn btn-light btn-sm" href="{{ url_for('login') }}">Вход</a>
          {% endif %}
        </div>
      </div>
    </nav>
    <main class="container py-4">
      <div class="row justify-content-center">
        <div class="col-12 col-md-8 col-lg-6">
          {{ content|safe }}
        </div>
      </div>
    </main>
  </body>
</html>
"""

def page(content_html):
    return render_template_string(base_layout, content=content_html)

# Страницы (формы)
register_form = """
<h2 class="mb-3">Регистрация</h2>
<form method="post" class="card card-body">
  <div class="mb-3">
    <label class="form-label">Телефон</label>
    <input type="text" class="form-control" name="phone" placeholder="87001234567" required>
  </div>
  <div class="mb-3">
    <label class="form-label">Пароль</label>
    <input type="password" class="form-control" name="password" required>
  </div>
  <button type="submit" class="btn btn-primary">Зарегистрироваться</button>
</form>
"""

login_form = """
<h2 class="mb-3">Вход</h2>
<form method="post" class="card card-body">
  <div class="mb-3">
    <label class="form-label">Телефон</label>
    <input type="text" class="form-control" name="phone" required>
  </div>
  <div class="mb-3">
    <label class="form-label">Пароль</label>
    <input type="password" class="form-control" name="password" required>
  </div>
  <button type="submit" class="btn btn-success">Войти</button>
</form>
"""

@app.route("/")
def home():
    content = """
    <div class="text-center">
      <h1 class="mb-3">Добро пожаловать в Бека Банк!</h1>
      <p class="mb-4">Регистрация, вход, баланс, пополнение и переводы.</p>
      <div class="d-flex justify-content-center gap-2">
        <a class="btn btn-primary" href="/register">Регистрация</a>
        <a class="btn btn-success" href="/login">Вход</a>
      </div>
    </div>
    """
    return page(content)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        phone = normalize_phone(request.form.get("phone", ""))
        password = (request.form.get("password") or "").strip()

        if not phone or not password:
            return page("<div class='alert alert-danger'>Ошибка: заполните телефон и пароль.</div>" + register_form)

        if phone in users:
            return page("<div class='alert alert-warning'>Ошибка: такой номер уже зарегистрирован.</div>" + register_form)
        
        users[phone] = {
            "password": generate_password_hash(password),
            "balance": 1000
        }
        return redirect(url_for("login"))
    return page(register_form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = normalize_phone(request.form.get("phone", ""))
        password = (request.form.get("password") or "").strip()

        user = users.get(phone)
        if user and check_password_hash(user["password"], password):
            session["phone"] = phone
            return redirect(url_for("dashboard"))
        else:
            return page("<div class='alert alert-danger'>Ошибка: неправильный номер или пароль.</div>" + login_form)
    return page(login_form)

@app.route("/dashboard")
def dashboard():
    phone = session.get("phone")
    if not phone:
        return redirect(url_for("login"))
    balance = users[phone]["balance"]
    content = f"""
    <div class="card">
      <div class="card-body">
        <h2 class="card-title">Личный кабинет</h2>
        <p class="card-text mb-1"><strong>Телефон:</strong> {phone}</p>
        <p class="card-text"><strong>Баланс:</strong> {balance} ₸</p>
        <div class="d-flex gap-2">
          <a class="btn btn-primary" href="{url_for('deposit')}">Пополнить баланс</a>
          <a class="btn btn-warning" href="{url_for('transfer')}">Перевести средства</a>
          <a class="btn btn-outline-secondary" href="{url_for('logout')}">Выйти</a>
        </div>
      </div>
    </div>
    """
    return page(content)

@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    phone = session.get("phone")
    if not phone:
        return redirect(url_for("login"))
    if request.method == "POST":
        amount_raw = (request.form.get("amount") or "").strip()
        if not amount_raw.isdigit():
            return page("<div class='alert alert-danger'>Ошибка: введите целое число.</div>" + deposit_form())
        amount = int(amount_raw)
        if amount <= 0:
            return page("<div class='alert alert-warning'>Ошибка: сумма должна быть больше нуля.</div>" + deposit_form())
        users[phone]["balance"] += amount
        return redirect(url_for("dashboard"))
    return page(deposit_form())

def deposit_form():
    return """
    <h2 class="mb-3">Пополнение баланса</h2>
    <form method="post" class="card card-body">
      <div class="mb-3">
        <label class="form-label">Сумма</label>
        <input type="number" class="form-control" name="amount" min="1" step="1" required>
      </div>
      <button type="submit" class="btn btn-primary">Пополнить</button>
      <a class="btn btn-link" href="/dashboard">Назад</a>
    </form>
    """

@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    phone = session.get("phone")
    if not phone:
        return redirect(url_for("login"))
    if request.method == "POST":
        to_phone = normalize_phone(request.form.get("to_phone", ""))
        amount_raw = (request.form.get("amount") or "").strip()

        if not to_phone:
            return page("<div class='alert alert-danger'>Ошибка: укажите номер получателя.</div>" + transfer_form())
        if to_phone == phone:
            return page("<div class='alert alert-warning'>Ошибка: нельзя переводить самому себе.</div>" + transfer_form())
        if not amount_raw.isdigit():
            return page("<div class='alert alert-danger'>Ошибка: введите целое число.</div>" + transfer_form())
        amount = int(amount_raw)
        if amount <= 0:
            return page("<div class='alert alert-warning'>Ошибка: сумма должна быть больше нуля.</div>" + transfer_form())

        if to_phone not in users:
            return page(f"<div class='alert alert-danger'>Ошибка: номер получателя не найден ({to_phone}).</div>" + transfer_form())
        if users[phone]["balance"] < amount:
            return page("<div class='alert alert-danger'>Ошибка: недостаточно средств.</div>" + transfer_form())

        users[phone]["balance"] -= amount
        users[to_phone]["balance"] += amount
        return redirect(url_for("dashboard"))
    return page(transfer_form())

def transfer_form():
    return """
    <h2 class="mb-3">Перевод средств</h2>
    <form method="post" class="card card-body">
      <div class="mb-3">
        <label class="form-label">Номер получателя</label>
        <input type="text" class="form-control" name="to_phone" placeholder="8700..." required>
      </div>
      <div class="mb-3">
        <label class="form-label">Сумма</label>
        <input type="number" class="form-control" name="amount" min="1" step="1" required>
      </div>
      <button type="submit" class="btn btn-warning">Перевести</button>
      <a class="btn btn-link" href="/dashboard">Назад</a>
    </form>
    """

@app.route("/logout")
def logout():
    session.pop("phone", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
