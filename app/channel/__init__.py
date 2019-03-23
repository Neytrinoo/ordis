from flask import Blueprint

channel = Blueprint('channel', __name__, template_folder='templates')

from app.channel import views