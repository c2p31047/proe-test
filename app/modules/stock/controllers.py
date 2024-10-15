from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from app.db.db import db
from app.models import Stock, StockActivity, StockCategory, Shelter, Admin
from functools import wraps
from datetime import datetime
from sqlalchemy.orm import joinedload

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def edit_stock_controller(id):
    shelters = Shelter.query.all()
    stock = Stock.query.get_or_404(id)
    admin = Admin.query.filter_by(email=current_user.email).first()
    if admin is None:
        flash('管理者が見つかりません。', 'error')
        return redirect(url_for('stock.stock_list'))
    if request.method == 'POST':
        stock.stockname = request.form['stockname']
        stock.quantity = request.form['quantity']
        stock.unit = request.form['unit']
        stock.location = request.form['location']
        stock.note = request.form['note']
        stock.expiration = datetime.strptime(request.form['expiration'], '%Y-%m-%d')
        stock.condition = request.form['condition']
        db.session.commit()
        stock_activity = StockActivity(
            admin_id=admin.id,
            shelter_id=stock.shelter_id,
            stock_id=stock.id,
            date=datetime.now(),
            type="編集",
            content=f"{stock.stockname} の情報を更新しました"
        )
        db.session.add(stock_activity)
        db.session.commit()
        return redirect(url_for('stock.stock_list'))
    return render_template('stock/edit_stock.html', stock=stock, shelters=shelters)

def add_stock_controller():
    shelters = Shelter.query.filter((Shelter.other == None) | (Shelter.other == '')).all()
    categories = StockCategory.query.all()
    admin = Admin.query.filter_by(email=current_user.email).first()
    if admin is None:
        flash('管理者が見つかりません。', 'error')
        return redirect(url_for('stock.stock_list'))
    if request.method == 'POST':
        new_stock = Stock(
            shelter_id=request.form['shelter_id'],
            category_id=request.form['category_id'],
            stockname=request.form['stockname'],
            quantity=request.form['quantity'],
            unit=request.form['unit'],
            location=request.form['location'],
            note=request.form['note'],
            expiration=datetime.strptime(request.form['expiration'], '%Y-%m-%d').date(),
            condition=request.form['condition']
        )
        db.session.add(new_stock)
        db.session.commit()
        stock_activity = StockActivity(
            admin_id=admin.id,
            shelter_id=request.form['shelter_id'],
            stock_id=new_stock.id,
            date=datetime.now(),
            type="追加",
            content=f"{request.form['stockname']} を追加しました"
        )
        db.session.add(stock_activity)
        db.session.commit()
        return redirect(url_for('stock.stock_list'))
    return render_template('stock/add_stock.html', shelters=shelters, categories=categories)

def delete_stock_controller(id):
    stock = Stock.query.get_or_404(id)
    
    # 関連するStockActivityレコードを削除
    StockActivity.query.filter_by(stock_id=id).delete()
    
    db.session.delete(stock)
    try:
        db.session.commit()
        flash('備蓄品が正常に削除されました。', 'success')
    except Exception as e:
        db.session.rollback()
        flash('備蓄品の削除中にエラーが発生しました。', 'error')
        print(f"Error: {str(e)}")
    
    return redirect(url_for('stock.stock_list'))

def stock_list_controller():
    shelters = Shelter.query.all()
    stocks = Stock.query.all()
    return render_template('stock/list_stock.html', stocks=stocks, shelters=shelters)

def activity_stock_controller():
    shelters = Shelter.query.all()
    activities = []
    selected_shelter_name = None
    selected_shelter_id = None

    if request.method == 'POST':
        selected_shelter_id = request.form.get('shelter_id')
        selected_shelter = Shelter.query.get(selected_shelter_id)
        if selected_shelter:
            selected_shelter_name = selected_shelter.name
        activities = StockActivity.query.filter_by(shelter_id=selected_shelter_id).all()

    return render_template( 
        'stock/stock_activity.html',
        activities=activities,
        shelters=shelters,
        selected_shelter_name=selected_shelter_name,
        selected_shelter_id=selected_shelter_id
    )