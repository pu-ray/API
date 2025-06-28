from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    school_name = db.Column(db.String(150))
    contact_info = db.Column(db.String(150))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    photo_filename = db.Column(db.String(150))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Initialize the database
with app.app_context():
    db.create_all()

# Signup endpoint
@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    file = request.files.get('photo')

    if not all([data.get('first_name'), data.get('last_name'), data.get('email'), data.get('password'), data.get('confirm_password')]):
        return jsonify({'message': 'Missing required fields'}), 400

    if data['password'] != data['confirm_password']:
        return jsonify({'message': 'Passwords do not match'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400

    filename = None
    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        school_name=data.get('school_name'),
        contact_info=data.get('contact_info'),
        telephone=data.get('telephone'),
        email=data['email'],
        photo_filename=filename
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if user and user.check_password(data.get('password')):
        return jsonify({'message': 'Login successful'})
    return jsonify({'message': 'Invalid email or password'}), 401

if __name__ == '__main__':
    app.run(debug=True)