from flask import Flask
from flask_login import LoginManager
from app.config.config import get_config_by_name
from app.initialize_functions import initialize_route, initialize_swagger
from app.models import User  # Userモデルをインポート
from app.db.db import db, migrate

login_manager = LoginManager()

def create_app(config=None) -> Flask:

    app = Flask(__name__)

    if not config:
        config = 'development'  # デフォルト設定を "development" にする

    app.config.from_object(get_config_by_name(config))

    # データベースの初期化
    db.init_app(app)
    migrate.init_app(app, db)

    # Flask-Loginの初期化
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'  # ログインページのエンドポイントを指定

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ルートとSwaggerの初期化
    initialize_route(app)
    initialize_swagger(app)

    return app
