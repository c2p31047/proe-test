from flask import Blueprint
from .controllers import *

stock_bp = Blueprint('stock', __name__)

@stock_bp.route('/admin/edit_stock/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_stock(id):
    return edit_stock_controller(id)

@stock_bp.route('/admin/add_stock', methods=['GET', 'POST'])
@admin_required
def add_stock():
    return add_stock_controller()

@stock_bp.route('/admin/delete_stock/<int:id>', methods=['GET', 'POST'])
@admin_required
def delete_stock(id):
    return delete_stock_controller(id)

@stock_bp.route('/admin/activity_stock', methods=['GET', 'POST'])
def activity_stock():
    return activity_stock_controller()

@stock_bp.route('/admin/stock_list')
def stock_list():
    return stock_list_controller()

@stock_bp.route('/admin/print_stock')
@admin_required
def print_stock():
    return print_stock_controller()
