# from Schema import User, Profile, Thread, Message
from flask import jsonify
# from main import db
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

def registerUser(data, db, User):

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirmPassword = data.get('confirmPassword')

    print(username, email, password, confirmPassword)

    user = User.query.filter_by(username=username).first()
    user_email = User.query.filter_by(email=email).first()
    
    if user :
        return jsonify({'message': 'Username already exists!'}), 409    
    elif user_email :
        return jsonify({'message': 'Email already exists!'}), 409
    
    else:

        if password != confirmPassword:
            return jsonify({'message': 'Passwords do not match!'}), 409
        new_user = User(
            public_id=str(uuid.uuid4()),
            username=username,
            email=email,
            password=generate_password_hash(password, method='sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully!'}),201


def loginUser(data, User, secret_key):

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'User does not exist!'}), 404
    if not check_password_hash(user.password, password):
        return jsonify({'message': 'Incorrect password!'}), 401

    token = jwt.encode({'id': user.id,'email' : user.email, 'username' : user.username,'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10000)}, secret_key)

    return jsonify({'token' : token,'message': 'User logged in successfully!'}), 200


def createAThread(data, db, Thread, Participant, current_user):
    title = data.get('title')

    if not title:
        return jsonify({'message': 'Title is required!'}), 400
    new_thread = Thread(
        title=title,
        user_id=current_user.id
    )
    db.session.add(new_thread)
    db.session.commit()
    
    new_participant = Participant(
        user_id=current_user.id,
        thread_id=new_thread.id
    )
    db.session.add(new_participant)
    db.session.commit()
    return jsonify({'data': new_thread.to_dict(),'message': 'Thread created successfully!'}),201


# get Threads
def getThreads( Thread, current_user):
    threads = Thread.query.filter_by(user_id=current_user.id).all()
    participants = current_user.participants
    print(len(participants))
    output = []
    for participant in participants:
        output.append(participant.thread.to_dict())
    # for thread in threads:
    #     output.append(thread.to_dict())
    
    return jsonify({'data': output, 'message': 'Threads fetched successfully!'}), 200

# delete thread
def deleteThread(data, db, Thread, current_user):
    thread_id = data.get('thread_id')
    thread = Thread.query.filter_by(id=thread_id).first()

    if not thread:
        return jsonify({'message': 'Thread does not exist!'}), 404

    if thread.user_id != current_user.id:
        return jsonify({'message': 'You are not the owner of this thread!'}), 401

    db.session.delete(thread)
    db.session.commit()
    return jsonify({'message': 'Thread deleted successfully!'}), 200

# send message
def sendMessage(data, db, Message, current_user):
    body = data.get('body')
    thread_id = data.get('thread_id')
    print(body, thread_id)
    new_message = Message(
        body=body,
        user_id=current_user.id,
        thread_id=thread_id
    )
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'data': new_message.to_dict(),'message': 'Message sent successfully!'}),201

def addParticipant(data, db, Thread ,User, Participant, current_user):
    thread_id = data.get('thread_id')
    username = data.get('username')
    user = User.query.filter_by(username=username).first()
    thread = Thread.query.filter_by(id=thread_id).first()

    if thread.user_id != current_user.id:
        return jsonify({'message': 'You are not the owner of this thread!'}), 401
    
    if not user:
        return jsonify({'message': 'User does not exist!'}), 404
    
    if user.id == current_user.id:
        return jsonify({'message': 'You are already a participant in this thread!'}), 409
    
    thread_user_id = [participant.user_id for participant in thread.participants]
    if user.id in thread_user_id:
        return jsonify({'message': 'User already exists in this thread!'}), 409

    new_participant = Participant(
        user_id=user.id,
        thread_id=thread_id
    )
    db.session.add(new_participant)
    db.session.commit()
    return jsonify({'data': new_participant.to_dict(),'message': 'Participant added successfully!'}),201

# delete participant
def deleteParticipant(data, db, Participant, current_user):
    participant_id = data.get('participant_id')
    participant = Participant.query.filter_by(id=participant_id).first()
    thread_user_id = participant.thread.user_id

    if not participant:
        return jsonify({'message': 'Participant does not exist!'}), 404

    if thread_user_id != current_user.id:
        return jsonify({'message': 'You are not the owner of this thread!'}), 401

    if thread_user_id == participant.user_id:
        return jsonify({'message': 'You cannot delete yourself from this thread!'}), 401

    db.session.delete(participant)
    db.session.commit()
    return jsonify({'message': 'Participant deleted successfully!'}),200