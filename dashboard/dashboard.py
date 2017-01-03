from flask import Blueprint, render_template, redirect, url_for, session
from functools import wraps

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard',
                      template_folder='templates')


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('profile'):
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated


@dashboard.route('/')
@requires_auth
def index():
    return render_template('dashboard.html')
