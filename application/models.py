import mongoengine as db


class User(db.Document):
    user_id = db.StringField(required=True, unique=True)
    created = db.DateTimeField(required=True)
    last_login = db.DateTimeField()
    nino = db.StringField()
