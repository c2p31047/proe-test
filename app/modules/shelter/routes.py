from flask import Blueprint
from .controllers import *

shelter_bp = Blueprint('shelter', __name__)

@shelter_bp.route('/admin/upload_shelter', methods=['GET', 'POST'])
def upload_shelter():
    return upload_shelter_controller()

@shelter_bp.route('/admin/add_shelter', methods=['GET', 'POST'])
@admin_required
def add_shelter():
    return add_shelter_controller()

@shelter_bp.route('/admin/manage_shelters')
@admin_required
def manage_shelters():
    return manage_shelters_controller()

@shelter_bp.route('/admin/shelter/edit/<int:shelter_id>', methods=['GET', 'POST'])
@admin_required
def edit_shelter(shelter_id):
    return edit_shelter_controller(shelter_id)

@shelter_bp.route('/shelter/<int:shelter_id>')
def shelter_detail(shelter_id):
    return shelter_detail_controller(shelter_id)

@shelter_bp.route('/admin/delete_shelter/<int:shelter_id>', methods=['GET'])
@admin_required
def delete_shelter(shelter_id):
    return delete_shelter_controller(shelter_id)
