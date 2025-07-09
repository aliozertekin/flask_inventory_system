from flask import Blueprint, render_template
from db.connection import get_connection

terms_bp = Blueprint('terms', __name__, url_prefix='/terms')

@terms_bp.route('/')
def index():
    return render_template('terms.html')