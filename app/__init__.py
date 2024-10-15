from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from app.config.config import get_config_by_name
from app.initialize_functions import initialize_route, initialize_db, initialize_swagger
from app.db.db import db
from app.models import User

# Flask-LoginとFlask-Migrateの初期化(無いと動かない)
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(get_config_by_name(config_name))
    app.config['UPLOAD_FOLDER'] = 'uploads'
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    migrate.init_app(app, db)

    from app.modules.main import main_bp
    app.register_blueprint(main_bp, name='main_bp')
    from app.modules.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin', name='admin_bp')
    from app.modules.shelter import shelter_bp
    app.register_blueprint(shelter_bp, url_prefix='/shelter', name='shelter_bp')

    from app.modules.stock import stock_bp
    app.register_blueprint(stock_bp, url_prefix='/stock', name='stock_bp')

    from app.modules.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/user', name='user_bp')

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    with app.app_context():
        initialize_route(app)
        initialize_db(app)
        initialize_swagger(app)

    '''
    # Routesの確認
    print("登録済みのRoutes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
    '''
    return app
