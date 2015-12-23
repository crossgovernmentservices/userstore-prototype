import os
from application.factory import create_app
from application.models import db


app = create_app(os.environ['SETTINGS'])
db.init_app(app)
