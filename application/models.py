from flask.ext.mongoengine import MongoEngine

db = MongoEngine()


class User(db.Document):
    user_id = db.StringField(required=True, unique=True)
    created = db.DateTimeField(required=True)
    last_login = db.DateTimeField(required=True)
    nino = db.StringField()
