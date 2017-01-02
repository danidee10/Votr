from flask import Blueprint, render_template

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard',
                      template_folder='templates')


@dashboard.route('/')
def index():
    return render_template('dashboard.html')
