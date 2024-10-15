from flask import render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import current_user
from app.db.db import db
from app.models import Shelter, Stock, StockActivity
from functools import wraps
import pandas as pd
import chardet
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import re

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def upload_shelter_controller():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルがありません。')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('ファイル名がありません。')
            return redirect(request.url)
        
        if file:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(filepath)
            try:
                # ファイルのエンコーディングを検出
                with open(filepath, 'rb') as f:
                    raw = f.read()
                    result = chardet.detect(raw)
                    encoding = result['encoding']
                
                # エンコーディングが検出できない場合やUTF-8での読み込みが失敗した場合はShift-JISを試す
                try:
                    df = pd.read_csv(filepath, encoding=encoding, low_memory=False)
                except UnicodeDecodeError:
                    df = pd.read_csv(filepath, encoding='shift-jis', low_memory=False)
                
                # 不要な改行や空データを削除
                df.columns = df.columns.str.replace('\n', '')
                df.dropna(how='all', inplace=True)  # 空行を削除
                df.dropna(axis=1, how='all', inplace=True)  # 空列を削除
                
                # 各行の処理
                for _, row in df.iterrows():
                    existing_shelter = Shelter.query.filter_by(name=row['名称']).first()
                    if existing_shelter is None:
                        # 収容人数の処理（空白や無効な値の場合にはNoneにする）
                        capacity = None
                        # "想定収容人数" と "収容可能人数（人）" のカラムから値を取得
                        capacity_str = str(row.get('想定収容人数', '')).strip() or str(row.get('収容可能人数（人）', '')).strip()
                        if capacity_str and capacity_str.lower() != 'nan':  # 空でない場合のみ処理
                            match = re.search(r'(\d{1,3}(?:,\d{3})*)', capacity_str)
                            if match:
                                digits = match.group(0).replace(',', '')
                                capacity = int(digits)
                        
                        # `other`が0の場合にNoneにする
                        other_value = row.get('施設種別呼称', False)
                        if other_value == 0:
                            other_value = None
                        
                        # データベースに保存する新しいシェルター情報を作成
                        shelter = Shelter(
                            name=row.get('名称', False),
                            address=row['住所'],
                            latitude=row['緯度'],
                            longitude=row['経度'],
                            capacity=capacity,  # capacity が空白なら None が入る
                            hightide=row.get('災害種別_高潮', False),
                            earthquake=row.get('災害種別_地震', False),
                            tsunami=row.get('災害種別_津波', False),
                            inland_flooding=row.get('災害種別_内水氾濫', False),
                            volcano=row.get('災害種別_火山現象', False),
                            landslide=row.get('災害種別_崖崩れ、土石流及び地滑り', False),
                            flood=row.get('災害種別_洪水', False),
                            other=other_value
                        )
                        db.session.add(shelter)

                # データベースにコミット
                db.session.commit()
                flash('ファイルが正常にアップロードされ、データが保存されました。')

            except Exception as e:
                # エラー時のロールバックとエラーメッセージの表示
                db.session.rollback()
                flash(f'エラーが発生しました: {str(e)}')
            finally:
                # 一時ファイルの削除
                if os.path.exists(filepath):
                    os.remove(filepath)
            return redirect(url_for('shelter.manage_shelters'))

    return render_template('shelter/upload_shelter.html')

def add_shelter_controller():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        existing_shelter = Shelter.query.filter_by(name=name).first()
        if existing_shelter:
            flash('この避難所は既に存在します。', 'danger')
            return redirect(url_for('shelter.add_shelter'))

        new_shelter = Shelter(name=name, address=address, latitude=latitude, longitude=longitude)
        db.session.add(new_shelter)
        db.session.commit()
        flash('新しい避難所が追加されました', 'success')
        return redirect(url_for('shelter.manage_shelters'))
    return render_template('shelter/add_shelter.html')

def manage_shelters_controller():
    shelters = Shelter.query.all()
    return render_template('shelter/manage_shelters.html', shelters=shelters)

def edit_shelter_controller(shelter_id):
    shelter = Shelter.query.get(shelter_id)
    if request.method == 'POST':
        shelter.name = request.form['name']
        shelter.address = request.form['address']
        shelter.latitude = request.form['latitude']
        shelter.longitude = request.form['longitude']
        db.session.commit()
        flash('避難所情報が更新されました')
        return redirect(url_for('shelter.manage_shelters'))
    return render_template('shelter/edit_shelter.html', shelter=shelter)

def shelter_detail_controller(shelter_id):
    shelter = Shelter.query.get_or_404(shelter_id)
    stocks = Stock.query.filter_by(shelter_id=shelter.id).all()
    return render_template('shelter/shelter_detail.html', shelter=shelter, stocks=stocks)

def delete_shelter_controller(shelter_id):
    shelter = Shelter.query.get(shelter_id)
    if shelter:
        db.session.delete(shelter)
        db.session.commit()
        flash('避難所が削除されました')
    return redirect(url_for('shelter.manage_shelters'))