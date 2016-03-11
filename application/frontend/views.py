import json

from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    url_for
)

from application.models import User


frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/')
def index():
    users = User.objects.all()
    return render_template('index.html', users=users)


def get_or_404(model, **kwargs):
    try:
        return model.objects.get(**kwargs)

    except model.DoesNotExist:
        abort(404)


@frontend.route('/links/<id>', methods=['GET', 'POST'])
def links(id):
    user = get_or_404(User, id=id)

    if request.method == 'POST':
        other = get_or_404(User, id=request.form.get('user_id'))
        user.link(other)
        return redirect(url_for('.index'))

    return render_template('links.html', user=user)


@frontend.route('/links/<id>.json')
def links_json(id):
    user = get_or_404(User, id=id)

    return json.dumps({'ids': [
        u.user_id for u in user.linked_ids]})
