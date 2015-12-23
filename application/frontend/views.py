from flask import (
    Blueprint,
    render_template
)

from application.models import User

frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/')
def index():
    users = User.objects.all()
    return render_template('index.html', users=users)
