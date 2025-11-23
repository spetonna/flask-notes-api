from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

import sqlite3

app = Flask(__name__)

# --- Config ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # change in production

db = SQLAlchemy(app)
jwt = JWTManager(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    notes = db.relationship('Note', backref='owner', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- Create DB ---
with app.app_context():
    db.create_all()

# --- Routes ---

## Register
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

## Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': token}), 200

## Get all notes for current user
@app.route('/api/notes', methods=['GET'])
@jwt_required()
def get_notes():
    current_user_id = get_jwt_identity()
    notes = Note.query.filter_by(user_id=current_user_id).all()
    return jsonify([{'id': n.id, 'title': n.title, 'content': n.content} for n in notes]), 200

## Create note for current user
@app.route('/api/notes', methods=['POST'])
@jwt_required()
def create_note():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': 'Title and content required'}), 400

    current_user_id = get_jwt_identity()
    new_note = Note(title=title, content=content, user_id=current_user_id)
    db.session.add(new_note)
    db.session.commit()

    return jsonify({'message': 'Note created successfully'}), 201

## Update note
@app.route('/api/notes/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=current_user_id).first()

    if not note:
        return jsonify({'message': 'Note not found'}), 404

    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    db.session.commit()

    return jsonify({'message': 'Note updated successfully'}), 200

## Delete note
@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    current_user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=current_user_id).first()

    if not note:
        return jsonify({'message': 'Note not found'}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': 'Note deleted successfully'}), 200



# Call this before running the Flask app

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
