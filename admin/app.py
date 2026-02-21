"""
Админ-панель High Five Coffee — управление меню.
Запуск: python -m admin.app   (из корня проекта)
"""

import os
import sys
import functools

# Гарантируем, что корень проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, g,
)
from admin.database import get_db, init_db, seed_db

app = Flask(__name__)
app.secret_key = os.environ.get('ADMIN_SECRET_KEY', 'hfc-admin-secret-key-change-me')

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'highfive2024')


# ── Авторизация ────────────────────────────────────────────────────

def login_required(view):
    """Декоратор: перенаправляет на /login, если пользователь не авторизован."""
    @functools.wraps(view)
    def wrapped(**kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Вы вошли в панель управления', 'success')
            return redirect(url_for('dashboard'))
        flash('Неверный пароль', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из панели управления', 'info')
    return redirect(url_for('login'))


# ── Дашборд ────────────────────────────────────────────────────────

@app.route('/')
@login_required
def dashboard():
    db = get_db()
    stats = {
        'categories': db.execute("SELECT COUNT(*) c FROM categories").fetchone()['c'],
        'drinks': db.execute("SELECT COUNT(*) c FROM drinks").fetchone()['c'],
        'summer_categories': db.execute("SELECT COUNT(*) c FROM summer_categories").fetchone()['c'],
        'summer_drinks': db.execute("SELECT COUNT(*) c FROM summer_drinks").fetchone()['c'],
        'syrups': db.execute("SELECT COUNT(*) c FROM syrups").fetchone()['c'],
        'dopings': db.execute("SELECT COUNT(*) c FROM dopings").fetchone()['c'],
        'tea_types': db.execute("SELECT COUNT(*) c FROM tea_types").fetchone()['c'],
        'alt_milk': db.execute("SELECT COUNT(*) c FROM alt_milk_types").fetchone()['c'],
    }
    db.close()
    return render_template('dashboard.html', stats=stats)


# ══════════════════════════════════════════════════════════════════
#  ОСНОВНОЕ МЕНЮ — Категории
# ══════════════════════════════════════════════════════════════════

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    db = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'add':
                name = request.form['name'].strip()
                if name:
                    max_order = db.execute("SELECT COALESCE(MAX(sort_order),0) m FROM categories").fetchone()['m']
                    db.execute("INSERT INTO categories (name, sort_order) VALUES (?, ?)", (name, max_order + 1))
                    db.commit()
                    flash(f'Категория «{name}» добавлена', 'success')
            elif action == 'edit':
                cat_id = request.form['id']
                name = request.form['name'].strip()
                if name:
                    db.execute("UPDATE categories SET name = ? WHERE id = ?", (name, cat_id))
                    db.commit()
                    flash('Категория обновлена', 'success')
            elif action == 'delete':
                cat_id = request.form['id']
                db.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
                db.commit()
                flash('Категория и все её напитки удалены', 'success')
        except Exception as e:
            flash(f'Ошибка: {e}', 'danger')
        db.close()
        return redirect(url_for('categories'))

    cats = db.execute("""
        SELECT c.*, COUNT(d.id) AS drink_count
        FROM categories c
        LEFT JOIN drinks d ON d.category_id = c.id
        GROUP BY c.id
        ORDER BY c.sort_order
    """).fetchall()
    db.close()
    return render_template('categories.html', categories=cats, is_summer=False)


# ══════════════════════════════════════════════════════════════════
#  ОСНОВНОЕ МЕНЮ — Напитки
# ══════════════════════════════════════════════════════════════════

@app.route('/categories/<int:cat_id>/drinks')
@login_required
def category_drinks(cat_id):
    db = get_db()
    category = db.execute("SELECT * FROM categories WHERE id = ?", (cat_id,)).fetchone()
    if not category:
        db.close()
        flash('Категория не найдена', 'danger')
        return redirect(url_for('categories'))

    drinks = db.execute(
        "SELECT * FROM drinks WHERE category_id = ? ORDER BY sort_order", (cat_id,)
    ).fetchall()

    # Подгружаем размеры для каждого напитка
    drinks_with_sizes = []
    for d in drinks:
        sizes = db.execute(
            "SELECT * FROM drink_sizes WHERE drink_id = ? ORDER BY sort_order", (d['id'],)
        ).fetchall()
        drinks_with_sizes.append({'drink': d, 'sizes': sizes})

    db.close()
    return render_template(
        'drinks.html',
        category=category,
        drinks=drinks_with_sizes,
        is_summer=False,
    )


@app.route('/categories/<int:cat_id>/drinks/add', methods=['GET', 'POST'])
@login_required
def add_drink(cat_id):
    db = get_db()
    category = db.execute("SELECT * FROM categories WHERE id = ?", (cat_id,)).fetchone()
    if not category:
        db.close()
        flash('Категория не найдена', 'danger')
        return redirect(url_for('categories'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Введите название напитка', 'danger')
            db.close()
            return redirect(url_for('add_drink', cat_id=cat_id))
        try:
            max_order = db.execute(
                "SELECT COALESCE(MAX(sort_order),0) m FROM drinks WHERE category_id = ?", (cat_id,)
            ).fetchone()['m']
            db.execute(
                "INSERT INTO drinks (category_id, name, sort_order) VALUES (?, ?, ?)",
                (cat_id, name, max_order + 1),
            )
            drink_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

            size_sort = {"S": 0, "M": 1, "L": 2}
            for sz in ["S", "M", "L"]:
                enabled = request.form.get(f'size_{sz}_enabled')
                price = request.form.get(f'size_{sz}_price', '').strip()
                if enabled and price and price.isdigit():
                    db.execute(
                        "INSERT INTO drink_sizes (drink_id, size, price, sort_order) VALUES (?, ?, ?, ?)",
                        (drink_id, sz, int(price), size_sort[sz]),
                    )

            db.commit()
            flash(f'Напиток «{name}» добавлен', 'success')
        except Exception as e:
            flash(f'Ошибка: {e}', 'danger')
        db.close()
        return redirect(url_for('category_drinks', cat_id=cat_id))

    db.close()
    return render_template('drink_form.html', category=category, drink=None, sizes={})


@app.route('/drinks/<int:drink_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_drink(drink_id):
    db = get_db()
    drink = db.execute("SELECT * FROM drinks WHERE id = ?", (drink_id,)).fetchone()
    if not drink:
        db.close()
        flash('Напиток не найден', 'danger')
        return redirect(url_for('categories'))

    category = db.execute("SELECT * FROM categories WHERE id = ?", (drink['category_id'],)).fetchone()

    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Введите название напитка', 'danger')
            db.close()
            return redirect(url_for('edit_drink', drink_id=drink_id))
        try:
            db.execute("UPDATE drinks SET name = ? WHERE id = ?", (name, drink_id))
            db.execute("DELETE FROM drink_sizes WHERE drink_id = ?", (drink_id,))

            size_sort = {"S": 0, "M": 1, "L": 2}
            for sz in ["S", "M", "L"]:
                enabled = request.form.get(f'size_{sz}_enabled')
                price = request.form.get(f'size_{sz}_price', '').strip()
                if enabled and price and price.isdigit():
                    db.execute(
                        "INSERT INTO drink_sizes (drink_id, size, price, sort_order) VALUES (?, ?, ?, ?)",
                        (drink_id, sz, int(price), size_sort[sz]),
                    )

            db.commit()
            flash(f'Напиток «{name}» обновлён', 'success')
        except Exception as e:
            flash(f'Ошибка: {e}', 'danger')
        db.close()
        return redirect(url_for('category_drinks', cat_id=drink['category_id']))

    existing_sizes = db.execute(
        "SELECT * FROM drink_sizes WHERE drink_id = ? ORDER BY sort_order", (drink_id,)
    ).fetchall()
    sizes = {s['size']: s['price'] for s in existing_sizes}
    db.close()
    return render_template('drink_form.html', category=category, drink=drink, sizes=sizes)


@app.route('/drinks/<int:drink_id>/delete', methods=['POST'])
@login_required
def delete_drink(drink_id):
    db = get_db()
    drink = db.execute("SELECT * FROM drinks WHERE id = ?", (drink_id,)).fetchone()
    if drink:
        cat_id = drink['category_id']
        db.execute("DELETE FROM drinks WHERE id = ?", (drink_id,))
        db.commit()
        flash('Напиток удалён', 'success')
    else:
        cat_id = None
        flash('Напиток не найден', 'danger')
    db.close()
    if cat_id:
        return redirect(url_for('category_drinks', cat_id=cat_id))
    return redirect(url_for('categories'))


# ══════════════════════════════════════════════════════════════════
#  ЛЕТНЕЕ МЕНЮ — Категории
# ══════════════════════════════════════════════════════════════════

@app.route('/summer', methods=['GET', 'POST'])
@login_required
def summer_categories():
    db = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'add':
                name = request.form['name'].strip()
                if name:
                    max_order = db.execute("SELECT COALESCE(MAX(sort_order),0) m FROM summer_categories").fetchone()['m']
                    db.execute("INSERT INTO summer_categories (name, sort_order) VALUES (?, ?)", (name, max_order + 1))
                    db.commit()
                    flash(f'Категория «{name}» добавлена', 'success')
            elif action == 'edit':
                cat_id = request.form['id']
                name = request.form['name'].strip()
                if name:
                    db.execute("UPDATE summer_categories SET name = ? WHERE id = ?", (name, cat_id))
                    db.commit()
                    flash('Категория обновлена', 'success')
            elif action == 'delete':
                cat_id = request.form['id']
                db.execute("DELETE FROM summer_categories WHERE id = ?", (cat_id,))
                db.commit()
                flash('Категория и все её напитки удалены', 'success')
        except Exception as e:
            flash(f'Ошибка: {e}', 'danger')
        db.close()
        return redirect(url_for('summer_categories'))

    cats = db.execute("""
        SELECT c.*, COUNT(d.id) AS drink_count
        FROM summer_categories c
        LEFT JOIN summer_drinks d ON d.category_id = c.id
        GROUP BY c.id
        ORDER BY c.sort_order
    """).fetchall()
    db.close()
    return render_template('categories.html', categories=cats, is_summer=True)


# ══════════════════════════════════════════════════════════════════
#  ЛЕТНЕЕ МЕНЮ — Напитки
# ══════════════════════════════════════════════════════════════════

@app.route('/summer/<int:cat_id>/drinks')
@login_required
def summer_drinks(cat_id):
    db = get_db()
    category = db.execute("SELECT * FROM summer_categories WHERE id = ?", (cat_id,)).fetchone()
    if not category:
        db.close()
        flash('Категория не найдена', 'danger')
        return redirect(url_for('summer_categories'))

    drinks = db.execute(
        "SELECT * FROM summer_drinks WHERE category_id = ? ORDER BY sort_order", (cat_id,)
    ).fetchall()

    drinks_with_sizes = []
    for d in drinks:
        sizes = db.execute(
            "SELECT * FROM summer_drink_sizes WHERE drink_id = ? ORDER BY sort_order", (d['id'],)
        ).fetchall()
        drinks_with_sizes.append({'drink': d, 'sizes': sizes})

    db.close()
    return render_template(
        'drinks.html',
        category=category,
        drinks=drinks_with_sizes,
        is_summer=True,
    )


@app.route('/summer/<int:cat_id>/drinks/add', methods=['GET', 'POST'])
@login_required
def add_summer_drink(cat_id):
    db = get_db()
    category = db.execute("SELECT * FROM summer_categories WHERE id = ?", (cat_id,)).fetchone()
    if not category:
        db.close()
        flash('Категория не найдена', 'danger')
        return redirect(url_for('summer_categories'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Введите название напитка', 'danger')
            db.close()
            return redirect(url_for('add_summer_drink', cat_id=cat_id))
        try:
            max_order = db.execute(
                "SELECT COALESCE(MAX(sort_order),0) m FROM summer_drinks WHERE category_id = ?", (cat_id,)
            ).fetchone()['m']
            db.execute(
                "INSERT INTO summer_drinks (category_id, name, sort_order) VALUES (?, ?, ?)",
                (cat_id, name, max_order + 1),
            )
            drink_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

            size_mls = request.form.getlist('size_ml')
            size_prices = request.form.getlist('size_price')
            for idx, (ml, price) in enumerate(zip(size_mls, size_prices)):
                ml = ml.strip()
                price = price.strip()
                if ml and price and price.isdigit():
                    db.execute(
                        "INSERT INTO summer_drink_sizes (drink_id, size_ml, price, sort_order) VALUES (?, ?, ?, ?)",
                        (drink_id, ml, int(price), idx),
                    )

            db.commit()
            flash(f'Напиток «{name}» добавлен', 'success')
        except Exception as e:
            flash(f'Ошибка: {e}', 'danger')
        db.close()
        return redirect(url_for('summer_drinks', cat_id=cat_id))

    db.close()
    return render_template('summer_drink_form.html', category=category, drink=None, sizes=[])


@app.route('/summer/drinks/<int:drink_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_summer_drink(drink_id):
    db = get_db()
    drink = db.execute("SELECT * FROM summer_drinks WHERE id = ?", (drink_id,)).fetchone()
    if not drink:
        db.close()
        flash('Напиток не найден', 'danger')
        return redirect(url_for('summer_categories'))

    category = db.execute("SELECT * FROM summer_categories WHERE id = ?", (drink['category_id'],)).fetchone()

    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Введите название напитка', 'danger')
            db.close()
            return redirect(url_for('edit_summer_drink', drink_id=drink_id))
        try:
            db.execute("UPDATE summer_drinks SET name = ? WHERE id = ?", (name, drink_id))
            db.execute("DELETE FROM summer_drink_sizes WHERE drink_id = ?", (drink_id,))

            size_mls = request.form.getlist('size_ml')
            size_prices = request.form.getlist('size_price')
            for idx, (ml, price) in enumerate(zip(size_mls, size_prices)):
                ml = ml.strip()
                price = price.strip()
                if ml and price and price.isdigit():
                    db.execute(
                        "INSERT INTO summer_drink_sizes (drink_id, size_ml, price, sort_order) VALUES (?, ?, ?, ?)",
                        (drink_id, ml, int(price), idx),
                    )

            db.commit()
            flash(f'Напиток «{name}» обновлён', 'success')
        except Exception as e:
            flash(f'Ошибка: {e}', 'danger')
        db.close()
        return redirect(url_for('summer_drinks', cat_id=drink['category_id']))

    existing_sizes = db.execute(
        "SELECT * FROM summer_drink_sizes WHERE drink_id = ? ORDER BY sort_order", (drink_id,)
    ).fetchall()
    db.close()
    return render_template('summer_drink_form.html', category=category, drink=drink, sizes=existing_sizes)


@app.route('/summer/drinks/<int:drink_id>/delete', methods=['POST'])
@login_required
def delete_summer_drink(drink_id):
    db = get_db()
    drink = db.execute("SELECT * FROM summer_drinks WHERE id = ?", (drink_id,)).fetchone()
    if drink:
        cat_id = drink['category_id']
        db.execute("DELETE FROM summer_drinks WHERE id = ?", (drink_id,))
        db.commit()
        flash('Напиток удалён', 'success')
    else:
        cat_id = None
        flash('Напиток не найден', 'danger')
    db.close()
    if cat_id:
        return redirect(url_for('summer_drinks', cat_id=cat_id))
    return redirect(url_for('summer_categories'))


# ══════════════════════════════════════════════════════════════════
#  СИРОПЫ
# ══════════════════════════════════════════════════════════════════

@app.route('/syrups', methods=['GET', 'POST'])
@login_required
def syrups():
    db = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'add':
                name = request.form['name'].strip()
                if name:
                    max_order = db.execute("SELECT COALESCE(MAX(sort_order),0) m FROM syrups").fetchone()['m']
                    db.execute("INSERT INTO syrups (name, sort_order) VALUES (?, ?)", (name, max_order + 1))
                    db.commit()
                    flash(f'Сироп «{name}» добавлен', 'success')
            elif action == 'edit':
                item_id = request.form['id']
                name = request.form['name'].strip()
                if name:
                    db.execute("UPDATE syrups SET name = ? WHERE id = ?", (name, item_id))
                    db.commit()
                    flash('Сироп обновлён', 'success')
            elif action == 'delete':
                item_id = request.form['id']
                db.execute("DELETE FROM syrups WHERE id = ?", (item_id,))
                db.commit()
                flash('Сироп удалён', 'success')
        except Exception as e:
            flash(f'Ошибка: {e}', 'danger')
        db.close()
        return redirect(url_for('syrups'))

    items = db.execute("SELECT * FROM syrups ORDER BY sort_order").fetchall()
    db.close()
    return render_template(
        'simple_list.html',
        items=items,
        title='Сиропы',
        item_label='сироп',
        route_name='syrups',
    )


# ══════════════════════════════════════════════════════════════════
#  ДОБАВКИ (ДОПИНГИ)
# ══════════════════════════════════════════════════════════════════

@app.route('/dopings', methods=['GET', 'POST'])
@login_required
def dopings():
    db = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'add':
                name = request.form['name'].strip()
                price_s = int(request.form.get('price_s', 0) or 0)
                price_m = int(request.form.get('price_m', 0) or 0)
                price_l = int(request.form.get('price_l', 0) or 0)
                if name:
                    max_order = db.execute("SELECT COALESCE(MAX(sort_order),0) m FROM dopings").fetchone()['m']
                    db.execute(
                        "INSERT INTO dopings (name, price_s, price_m, price_l, sort_order) VALUES (?, ?, ?, ?, ?)",
                        (name, price_s, price_m, price_l, max_order + 1),
                    )
                    db.commit()
                    flash(f'Добавка «{name}» добавлена', 'success')
            elif action == 'edit':
                item_id = request.form['id']
                name = request.form['name'].strip()
                price_s = int(request.form.get('price_s', 0) or 0)
                price_m = int(request.form.get('price_m', 0) or 0)
                price_l = int(request.form.get('price_l', 0) or 0)
                if name:
                    db.execute(
                        "UPDATE dopings SET name = ?, price_s = ?, price_m = ?, price_l = ? WHERE id = ?",
                        (name, price_s, price_m, price_l, item_id),
                    )
                    db.commit()
                    flash('Добавка обновлена', 'success')
            elif action == 'delete':
                item_id = request.form['id']
                db.execute("DELETE FROM dopings WHERE id = ?", (item_id,))
                db.commit()
                flash('Добавка удалена', 'success')
        except Exception as e:
            flash(f'Ошибка: {e}', 'danger')
        db.close()
        return redirect(url_for('dopings'))

    items = db.execute("SELECT * FROM dopings ORDER BY sort_order").fetchall()
    db.close()
    return render_template('dopings.html', items=items)


# ══════════════════════════════════════════════════════════════════
#  СОРТА ЧАЯ
# ══════════════════════════════════════════════════════════════════

@app.route('/tea-types', methods=['GET', 'POST'])
@login_required
def tea_types():
    db = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'add':
                name = request.form['name'].strip()
                if name:
                    max_order = db.execute("SELECT COALESCE(MAX(sort_order),0) m FROM tea_types").fetchone()['m']
                    db.execute("INSERT INTO tea_types (name, sort_order) VALUES (?, ?)", (name, max_order + 1))
                    db.commit()
                    flash(f'Сорт чая «{name}» добавлен', 'success')
            elif action == 'edit':
                item_id = request.form['id']
                name = request.form['name'].strip()
                if name:
                    db.execute("UPDATE tea_types SET name = ? WHERE id = ?", (name, item_id))
                    db.commit()
                    flash('Сорт чая обновлён', 'success')
            elif action == 'delete':
                item_id = request.form['id']
                db.execute("DELETE FROM tea_types WHERE id = ?", (item_id,))
                db.commit()
                flash('Сорт чая удалён', 'success')
        except Exception as e:
            flash(f'Ошибка: {e}', 'danger')
        db.close()
        return redirect(url_for('tea_types'))

    items = db.execute("SELECT * FROM tea_types ORDER BY sort_order").fetchall()
    db.close()
    return render_template(
        'simple_list.html',
        items=items,
        title='Сорта чая',
        item_label='сорт чая',
        route_name='tea_types',
    )


# ══════════════════════════════════════════════════════════════════
#  АЛЬТЕРНАТИВНОЕ МОЛОКО
# ══════════════════════════════════════════════════════════════════

@app.route('/alt-milk', methods=['GET', 'POST'])
@login_required
def alt_milk():
    db = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'add':
                name = request.form['name'].strip()
                if name:
                    max_order = db.execute("SELECT COALESCE(MAX(sort_order),0) m FROM alt_milk_types").fetchone()['m']
                    db.execute("INSERT INTO alt_milk_types (name, sort_order) VALUES (?, ?)", (name, max_order + 1))
                    db.commit()
                    flash(f'Молоко «{name}» добавлено', 'success')
            elif action == 'edit':
                item_id = request.form['id']
                name = request.form['name'].strip()
                if name:
                    db.execute("UPDATE alt_milk_types SET name = ? WHERE id = ?", (name, item_id))
                    db.commit()
                    flash('Обновлено', 'success')
            elif action == 'delete':
                item_id = request.form['id']
                db.execute("DELETE FROM alt_milk_types WHERE id = ?", (item_id,))
                db.commit()
                flash('Удалено', 'success')
        except Exception as e:
            flash(f'Ошибка: {e}', 'danger')
        db.close()
        return redirect(url_for('alt_milk'))

    items = db.execute("SELECT * FROM alt_milk_types ORDER BY sort_order").fetchall()
    db.close()
    return render_template(
        'simple_list.html',
        items=items,
        title='Альтернативное молоко',
        item_label='вид молока',
        route_name='alt_milk',
    )


# ── Запуск ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    seed_db()
    port = int(os.environ.get('ADMIN_PORT', 5050))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    print("✅ База данных инициализирована")
    print(f"🔑 Пароль для входа: {ADMIN_PASSWORD}")
    print(f"🌐 Админ-панель: http://0.0.0.0:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
