from flask import Blueprint
from flask_login import login_required
from app.common.controllers import login_controller, register_controller, logout_controller, settings_controller

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    return login_controller()

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    return register_controller()

@user_bp.route('/logout')
@login_required
def logout():
    return logout_controller()

@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return settings_controller()
