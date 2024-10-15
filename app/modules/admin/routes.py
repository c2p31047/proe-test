from flask import Blueprint
from flask_login import login_required
from .controllers import *

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    return admin_dashboard_controller()

@admin_bp.route('/admin/add_admin', methods=['GET', 'POST'])
@admin_required
def add_admin():
    return add_admin_controller()

@admin_bp.route('/admin/promote', methods=['POST'])
@admin_required
def promote_user_by_email():
    return promote_user_by_email_controller()

@admin_bp.route('/admin/manage_admins')
@login_required
@admin_required
def manage_admins():
    return manage_admins_controller()

@admin_bp.route('/admin/edit_admin/<int:admin_id>', methods=['GET', 'POST'])
@admin_required
def edit_admin(admin_id):
    return edit_admin_controller(admin_id)

@admin_bp.route('/admin/delete_admin/<int:admin_id>', methods=['GET'])
@admin_required
def delete_admin(admin_id):
    return delete_admin_controller(admin_id)

@admin_bp.route('/admin/list_category', methods=['GET'])
def list_category():
    return list_category_controller()

@admin_bp.route('/admin/add_category', methods=['GET', 'POST'])
def add_category():
    return add_category_controller()

@admin_bp.route('/admin/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    return edit_category_controller(id)

@admin_bp.route('/admin/delete_category/<int:id>', methods=['GET', 'POST'])
@admin_required
def delete_category(id):
    return delete_category_controller(id)
