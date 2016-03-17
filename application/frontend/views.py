import datetime
from flask import (
    Blueprint,
    abort,
    jsonify,
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


@frontend.route('/', methods=['POST'])
def add_user():
    user_id = request.form.get('user_id')

    if user_id:
        User.objects.create(user_id=user_id, created=datetime.datetime.utcnow())

    return redirect(url_for('.index'))


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


@frontend.route('/links/<user_id>.json')
def links_json(user_id):
    try:
        user = User.objects.get(user_id=user_id)

    except User.DoesNotExist:
        return jsonify({'ids': []})

    return jsonify({'ids': [
        u.user_id for u in user.linked_ids]})


@frontend.route('/search.json')
def search_json():
    term = request.args.get('q')
    users = []

    if term:
        users = User.objects.filter(user_id__icontains=term)

    return jsonify({'users': [
        {
            'id': str(user.id),
            'uid': user.user_id
        }
        for user in users]})
