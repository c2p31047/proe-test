from flask import Blueprint

shelter_bp = Blueprint('shelter', __name__)

from . import routes