import mongoengine as db


class User(db.Document):
    user_id = db.StringField(required=True, unique=True)
    created = db.DateTimeField(required=True)
    last_login = db.DateTimeField()
    nino = db.StringField()
    linked_ids = db.ListField(db.ReferenceField('User'), default=[])

    def link(self, other):
        self.update(push__linked_ids=other)
        other.update(push__linked_ids=self)
