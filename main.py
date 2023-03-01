from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, make_response
from dotenv import load_dotenv
import os
from views import registerUser, loginUser, createAThread, getThreads, sendMessage, addParticipant, deleteThread, deleteParticipant
from datetime import datetime
from functools import wraps
import jwt
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})


# defined the database variables
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOADED_IMAGES_DEST'] = 'uploads/images'

#initialize db
db = SQLAlchemy(app)


#Schemas
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    public_id = db.Column(db.String(50), unique=True)
    profile = db.relationship('Profile', backref='user', lazy=True, uselist=False)
    messages = db.relationship('Message', backref='user', lazy=True)
    threads = db.relationship('Thread', backref='user', lazy=True)
    participants = db.relationship('Participant', backref='user', lazy=True)

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    messages = db.relationship('Message', backref='thread', lazy=True)
    participants = db.relationship('Participant', backref='thread', lazy=True)

    def to_dict(self):
        return {
            "thread_id" : self.id,
            "user_id": self.user_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            'messages': [message.to_dict() for message in self.messages],
            'participants': [participant.to_dict() for participant in self.participants]
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
        user = User.query.filter_by(id=self.user_id).first()
        return {
            "user_id": self.user_id,
            "username": user.username,
            "body": self.body,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at
        }

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "thread_id": self.thread_id,
            "user_id": self.user_id,
            "joined_at": self.joined_at
        }

# Creating the token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        # if request.cookies.get('token'):
        #     token = request.cookies.get('token')


        # returns 401 error if token isn't passed
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except Exception as e:
            print(e)
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# login users
@app.route('/api/login', methods=['POST'])
def login():
    return loginUser(request.form, User, app.config['SECRET_KEY'])


# register users
@app.route('/api/register', methods=['POST'])
def register():
    return registerUser(request.form, db, User)

# create thread
@app.route('/api/create-thread', methods=['POST'])
@token_required
def create_thread(current_user):
    return createAThread(request.form, db, Thread,  Participant, current_user)


# get all threads
@app.route('/api/get-threads', methods=['GET'])
@token_required
def get_threads(current_user):
    return getThreads( Thread, current_user)

# delete thread
@app.route('/api/delete-thread', methods=['POST'])
@token_required
def delete_thread(current_user):
    return deleteThread(request.form, db, Thread, current_user)


# send message
@app.route('/api/send-message', methods=['POST'])
@token_required
def send_message(current_user):
    return sendMessage(request.form, db, Message, current_user)

# add participant
@app.route('/api/add-participant', methods=['POST'])
@token_required
def add_participant(current_user):
    return addParticipant(request.form, db, Thread,User, Participant, current_user)

# delete participant
@app.route('/api/delete-participant', methods=['POST'])
@token_required
def delete_participant(current_user):
    return deleteParticipant(request.form, db, Thread,User, Participant, current_user)




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)