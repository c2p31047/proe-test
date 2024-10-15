from flask import render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.db.db import db
from app.models import User, Shelter
from app.forms import LoginForm, RegisterForm

def get_shelters():
    shelters = Shelter.query.all()
    shelters_dict = [shelter.to_dict() for shelter in shelters]
    return shelters_dict

def index_controller():
    shelters_dict = get_shelters()
    return render_template('main/index.html', shelters=shelters_dict, current_user=current_user)

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
        if new_work_address:
            current_user.work_address = new_work_address
        if new_password and check_password_hash(current_user.password, current_password):
            current_user.password = generate_password_hash(new_password)

        db.session.commit()
        flash('設定が更新されました', 'success')
        return redirect(url_for('main.index'))
    return render_template('main/settings.html')
