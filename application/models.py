from flask.ext.mongoengine import MongoEngine

db = MongoEngine()


class User(db.Document):
    email = db.EmailField(required=True, unique=True)
    created = db.DateTimeField(required=True)
    last_login = db.DateTimeField(required=True)
    nino = db.StringField()
