from flask import Blueprint, request, render_template_string, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from .models import db, Order, StorageCell, User, OperationLog

bp = Blueprint("main", __name__)

PAGE = """<!doctype html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Управление ПВЗ</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #f3f5f8;
    margin: 0;
    padding: 30px;
    color: #263238;
}
.container {
    max-width: 1100px;
    margin: auto;
}
h1 { color: #263b58; }
.card {
    background: white;
    padding: 22px;
    margin: 20px 0;
    border-radius: 10px;
    box-shadow: 0 2px 8px #00000012;
}
label {
    display: block;
    margin: 12px 0;
}
input, select {
    padding: 9px;
    width: 250px;
    border: 1px solid #ccd2da;
    border-radius: 5px;
}
button {
    padding: 11px 22px;
    background: #315b91;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}
button:hover { background: #24466f; }
table {
    width: 100%;
    border-collapse: collapse;
    background: white;
}
th, td {
    padding: 13px;
    border-bottom: 1px solid #e1e5eb;
    text-align: left;
}
th { background: #eaf0f7; }
.message {
    padding: 12px;
    background: #e8f3e9;
    border-radius: 5px;
    margin-bottom: 15px;
}
.status {
    color: #267443;
    font-weight: bold;
}
</style>
</head>
<body>
<div class="container">

<h1>Управление ПВЗ</h1>
<p>Информационная система учёта и обработки заказов</p>

<div class="card">
<h2>Приёмка товара</h2>

{% with messages = get_flashed_messages() %}
{% for m in messages %}
<div class="message">{{ m }}</div>
{% endfor %}
{% endwith %}

<form method="post" action="/accept">

<label>Трек-номер
<input name="tracking_number" required>
</label>

<label>Маркетплейс
<select name="marketplace">
<option>Ozon</option>
<option>Wildberries</option>
<option>Другое</option>
</select>
</label>

<label>Ячейка хранения
<select name="cell_id">
{% for c in cells %}
<option value="{{ c.id }}">{{ c.code }}</option>
{% endfor %}
</select>
</label>

<label>Сотрудник
<select name="user_id">
{% for u in users %}
<option value="{{ u.id }}">{{ u.full_name }}</option>
{% endfor %}
</select>
</label>

<label>Комментарий
<input name="note">
</label>

<button type="submit">Принять заказ</button>
</form>
</div>

<div class="card">
<h2>Заказы на ПВЗ</h2>

<table>
<tr>
<th>Трек-номер</th>
<th>Площадка</th>
<th>Статус</th>
<th>Ячейка</th>
<th>Время приёмки</th>
</tr>

{% for o in orders %}
<tr>
<td>{{ o.tracking_number }}</td>
<td>{{ o.marketplace }}</td>
<td class="status">
{% if o.status == 'awaiting_issue' %}
Ожидает выдачи
{% else %}
{{ o.status }}
{% endif %}
</td>
<td>{{ o.cell.code if o.cell else '—' }}</td>
<td>{{ o.accepted_at.strftime('%d.%m.%Y %H:%M') if o.accepted_at else '—' }}</td>
</tr>
{% endfor %}
</table>
</div>

</div>
</body>
</html>"""

@bp.get("/")
def index():
    return render_template_string(PAGE, cells=StorageCell.query.filter_by(is_active=True, zone="storage").all(), users=User.query.all(), orders=Order.query.order_by(Order.id.desc()).all())

@bp.post("/accept")
def accept():
    tracking = request.form.get("tracking_number", "").strip()
    if not tracking:
        flash("Введите трек-номер."); return redirect(url_for("main.index"))
    if Order.query.filter_by(tracking_number=tracking).first():
        flash("Такой трек-номер уже зарегистрирован. Повторная приёмка запрещена."); return redirect(url_for("main.index"))
    cell = db.session.get(StorageCell, int(request.form["cell_id"]))
    user = db.session.get(User, int(request.form["user_id"]))
    if not cell or not user or cell.zone != "storage" or not cell.is_active:
        flash("Выбрана недоступная ячейка или сотрудник."); return redirect(url_for("main.index"))
    if Order.query.filter_by(cell_id=cell.id, status="awaiting_issue").first():
        flash("Ячейка занята. Выберите свободную."); return redirect(url_for("main.index"))
    order = Order(tracking_number=tracking, marketplace=request.form["marketplace"], cell=cell, operator=user, note=request.form.get("note"))
    db.session.add(order); db.session.flush()
    db.session.add(OperationLog(order_id=order.id, user_id=user.id, operation="accept", details=f"Приёмка в ячейку {cell.code}"))
    try:
        db.session.commit(); flash("Заказ принят и размещён.")
    except IntegrityError:
        db.session.rollback(); flash("Не удалось сохранить заказ: проверьте уникальность трек-номера.")
    return redirect(url_for("main.index"))
