from flask import Blueprint, render_template
from db.connection import get_connection

privacy_bp = Blueprint('privacy', __name__, url_prefix='/privacy')

@privacy_bp.route('/')
def index():
    return render_template('privacy.html')