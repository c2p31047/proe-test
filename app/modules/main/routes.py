from flask import Blueprint
from flask_login import login_required
from app.common.controllers import index_controller, login_controller, register_controller, logout_controller, settings_controller

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return index_controller()

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    return login_controller()

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    return register_controller()

@main_bp.route('/logout')
@login_required
def logout():
    return logout_controller()

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return settings_controller()
