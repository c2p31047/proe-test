from flask import Flask
from flasgger import Swagger
from app.modules.main.routes import main_bp
from app.modules.admin.routes import admin_bp
from app.modules.shelter.routes import shelter_bp
from app.modules.stock.routes import stock_bp
from app.modules.user.routes import user_bp
from app.db.db import db

def initialize_route(app: Flask):
    with app.app_context():
        app.register_blueprint(main_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(shelter_bp)
        app.register_blueprint(stock_bp)
        app.register_blueprint(user_bp)

def initialize_db(app: Flask):
    with app.app_context():
        db.create_all()

def initialize_swagger(app: Flask):
    with app.app_context():
        swagger = Swagger(app)
        return swagger
