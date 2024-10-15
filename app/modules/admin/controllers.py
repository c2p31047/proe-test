from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from app.db.db import db
from app.models import Admin, User, StockCategory
from functools import wraps

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_dashboard_controller():
    print("Admin dashboard controller called")  # デバッグ用
    return render_template('admin/dashboard.html')

def add_admin_controller():
    return render_template('admin/add_admin.html')

def promote_user_by_email_controller():
    email = request.form['email']
    user = User.query.filter_by(email=email).first()
    existing_admin = Admin.query.filter_by(email=email).first()
    if existing_admin:
        flash('このメールアドレスは既に登録されています。', 'error')
        return redirect(url_for('admin.add_admin'))
    if user:
        new_admin = Admin(email=user.email, name=user.name, password=user.password)
        db.session.add(new_admin)
        db.session.commit()
        flash('管理者が追加されました.')
    else:
        flash('ユーザーが見つかりません.')
    return redirect(url_for('admin.add_admin'))

def manage_admins_controller():
    admins = Admin.query.all()
    return render_template('admin/manage_admins.html', admins=admins)

def edit_admin_controller(admin_id):
    admin = Admin.query.get(admin_id)
    if request.method == 'POST':
        admin.name = request.form['name']
        admin.email = request.form['email']
        db.session.commit()
        return redirect(url_for('admin.manage_admins'))
    return render_template('admin/edit_admin.html', admin=admin)

def delete_admin_controller(admin_id):
    admin = Admin.query.get(admin_id)
    if admin:
        db.session.delete(admin)
        db.session.commit()
    return redirect(url_for('admin.manage_admins'))

def list_category_controller():
    categories = StockCategory.query.all()
    return render_template('category/list_category.html', categories=categories)

def add_category_controller():
    if request.method == 'POST':
        category_name = request.form['category']
        other_info = request.form['other']
        existing_category = StockCategory.query.filter_by(category=category_name).first()
        if existing_category:
            flash('このカテゴリはすでに存在します。', 'error')
            return redirect(url_for('admin.add_category'))
        new_category = StockCategory(category=category_name, other=other_info)
        db.session.add(new_category)
        db.session.commit()
        flash('新しいカテゴリが追加されました。', 'success')
        return redirect(url_for('admin.list_category'))
    return render_template('category/add_category.html')

def edit_category_controller(id):
    category = StockCategory.query.get_or_404(id)
    if request.method == 'POST':
        category.category = request.form['category']
        category.other = request.form['other']
        db.session.commit()
        flash('カテゴリが更新されました。', 'success')
        return redirect(url_for('admin.list_category'))
    return render_template('category/edit_category.html', category=category)

def delete_category_controller(id):
    category = StockCategory.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('カテゴリが削除されました。', 'success')
    return redirect(url_for('admin.list_category'))
