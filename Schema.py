
from datetime import datetime
from main import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    public_id = db.Column(db.String(50), unique=True)
    profile = db.relationship('Profile', backref='user', lazy=True, uselist=False)
    messages = db.relationship('Message', backref='user', lazy=True)
    def __repr__(self):
        return '<User %r>' % self.username
    def to_dict(self):
        return {
            "public_id": self.public_id,
            "username": self.username,
            "email": self.email,
        }


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    img_url = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "img_url": self.img_url,
            "phone": self.phone,
            "created_at": self.created_at
        }
    


class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    messages = db.relationship('Message', backref='thread', lazy=True)

    def to_dict(self):
        return {
            "owner_id": self.owner_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    body = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "body": self.body,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at
        }