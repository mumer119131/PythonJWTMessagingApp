from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, make_response
from dotenv import load_dotenv
import os
from decorators import token_required



load_dotenv()

app = Flask(__name__)

# defined the database variables
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOADED_IMAGES_DEST'] = 'uploads/images'

#initialize db
db = SQLAlchemy(app)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)