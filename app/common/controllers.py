from flask import render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.db.db import db
from app.models import User, Shelter
from app.forms import LoginForm, RegisterForm
import googlemaps
from math import radians, sin, cos, sqrt, atan2

def get_shelters():
    shelters = Shelter.query.all()
    shelters_dict = [shelter.to_dict() for shelter in shelters]
    return shelters_dict

def index_controller():
    shelters_dict = get_shelters()
    user_address = current_user.address if current_user.is_authenticated else None
    return render_template('main/index.html', shelters=shelters_dict, user_address=user_address, current_user=current_user)

def login_controller():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        password = form.password.data.strip()
        user = User.query.filter_by(email=email).first()
        print(f"ログイン試行: email={email}, ユーザー存在={user is not None}")
        if user:
            '''
            print(f"保存されているパスワードハッシュ: {user.password}")
            print(f"入力されたパスワード: {password}")
            
            
            # 保存されているハッシュと入力パスワードの検証
            print(f"パスワード検証結果: {is_password_correct}")
            
            # テストハッシュと入力パスワードの検証
            test_check = check_password_hash(test_hash, password)
            print(f"テストハッシュ検証結果: {test_check}")
            '''
            is_password_correct = check_password_hash(user.password, password)
            if is_password_correct:
                login_user(user)
                print(f"ログイン成功: {user.email}")
                return redirect(url_for('main.index'))
        print(f"ログイン失敗: {email}")
        flash('ログインに失敗しました。', 'danger')
    return render_template('main/login.html', form=form, current_user=current_user)

def register_controller():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        address = form.address.data if form.address.data else None
        phonenumber = form.phonenumber.data if form.phonenumber.data else None
        password = form.password.data
        password_hash = generate_password_hash(password, method='scrypt')
        print(f"Original password: {password}")  # デバッグ用（本番環境では削除してください）
        print(f"Generated password hash: {password_hash}")  # デバッグ用
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('このメールアドレスはすでに登録されています。', 'danger')
            return redirect(url_for('user.register'))
        new_user = User(
            name=name,
            email=email,
            address=address,
            phonenumber=phonenumber,
            password=password_hash
        )
        try:
            with current_app.app_context():
                db.session.add(new_user)
                db.session.commit()
            flash('ユーザー登録が完了しました。', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('ユーザー登録中にエラーが発生しました。', 'danger')
    return render_template('main/register.html', form=form, current_user=current_user)

def logout_controller():
    logout_user()
    return redirect(url_for('main.index'))

def settings_controller():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_address = request.form.get('address')
        new_work_address = request.form.get('work_address')
        new_email = request.form.get('email')
        new_phonenumber = request.form.get('phonenumber')
        new_password = request.form.get('password')
        current_password = request.form.get('current_password')

        if new_username:
            current_user.name = new_username
        if new_phonenumber:
            current_user.phonenumber = new_phonenumber
        if new_email:
            current_user.email = new_email
        if new_address:
            current_user.address = new_address
            update_nearest_shelter(current_user, new_address, 'shelter_id')
        if new_work_address:
            current_user.work_address = new_work_address
            update_nearest_shelter(current_user, new_work_address, 'work_shelter_id')
        if new_password and check_password_hash(current_user.password, current_password):
            current_user.password = generate_password_hash(new_password)

        db.session.commit()
        flash('設定が更新されました', 'success')
        return redirect(url_for('main.index'))
    return render_template('main/settings.html')

def update_nearest_shelter(user, address, shelter_field):
    lat, lng = get_lat_lng_from_address(address)
    
    if lat and lng:
        nearest_shelter = find_nearest_shelter(lat, lng)
        if nearest_shelter:
            setattr(user, shelter_field, nearest_shelter.id)
            db.session.commit()
        else:
            flash(f'指定された住所 "{address}" の近くに緊急指定避難所が見つかりませんでした。', 'warning')

def get_lat_lng_from_address(address):
    gmaps = googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
    except Exception as e:
        current_app.logger.error(f"Geocoding error: {str(e)}")
    return None, None

def find_nearest_shelter(lat, lng):
    # 緊急指定避難所のみを取得
    shelters = Shelter.query.filter((Shelter.other == None) | (Shelter.other == '')).all()
    nearest_shelter = None
    min_distance = float('inf')

    for shelter in shelters:
        distance = calculate_distance(lat, lng, shelter.latitude, shelter.longitude)
        if distance < min_distance:
            min_distance = distance
            nearest_shelter = shelter

    return nearest_shelter

def get_lat_lng_from_address(address):
    gmaps = googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
    except Exception as e:
        current_app.logger.error(f"ジオコーディングエラー: {str(e)}")
    return None, None

def find_nearest_shelter(lat, lng):
    # 緊急指定避難所のみを取得
    shelters = Shelter.query.filter((Shelter.other == None) | (Shelter.other == '')).all()
    nearest_shelter = None
    min_distance = float('inf')

    for shelter in shelters:
        distance = calculate_distance(lat, lng, shelter.latitude, shelter.longitude)
        if distance < min_distance:
            min_distance = distance
            nearest_shelter = shelter

    return nearest_shelter

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # 地球の半径（キロメートル）

    # 緯度と経度をラジアンに変換
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # 緯度と経度の差を計算
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # ヒュベニの公式を使用して距離を計算
    # a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
    # ここで、φは緯度、λは経度を表す
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2

    # c = 2 ⋅ atan2( √a, √(1−a) )
    # atan2は逆正接（アークタンジェント）関数
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    # 距離 = 地球の半径 * c
    distance = R * c

    return distance
