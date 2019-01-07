from db import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import time

###########################
### DB User Model
###########################
class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80))
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    accepted_user = db.Column(db.Boolean, nullable=False)
    user_role = db.Column(db.String(80))
    created = db.Column(db.DateTime, default=datetime.datetime.now())
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now())

    def __init__(self, email, password, first_name, last_name):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.accepted_user = False
        self.user_role = 'Customer' # ['Customer', 'Admin', 'Consultant']

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save_to_db(self):
        try:
            db.session.add(self)
            db.session.commit()
        except:
            return {'message': 'Error occured while adding user to DB'}, 500

    def delete_from_db(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            return {'message': 'Error occured while deleting user from DB'}, 500

    def json(self):
        return {
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name,
            }

    # Mapping by EMAIL
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    # Mapping by ID
    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
