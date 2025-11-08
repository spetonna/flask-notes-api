from flask import Flask , request , jsonify 
from flask_sqlalchemy import SQLAlchemy


import sqlite3

app = Flask(__name__)


## Database configuration (using SQLite)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Database connected successfully!"







def get_db_connection():
    conn = sqlite3.connect('notes.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/notes', methods=['GET'])
def get_notes():
    notes = Note.query.all()
    notes_list = []
    for note in notes:
        notes_list.append({
            "id": note.id,
            "title": note.title, 
            "content" : note.content
        })
    return jsonify(notes_list), 200
   
@app.route('/api/notes', methods=['POST'])
def create_note():
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Missing JSON data.'}),400

    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': 'Both title and content are required.'}), 400
    
    new_note = Note(title=data['title'], content=data['content'])
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"message": "Note added successfully!"}), 201
    

@app.route('/api/notes/<int:note_id>', methods = ['PUT'])
def update_note(note_id):
    data = request.get_json()
    note = Note.query.get(note_id)

    if not data:
        return jsonify({'message': 'Missing JSON data'}),400

    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': 'Both title and contents should be present.'}),400

    note.title = title
    note.content = content
    db.session.commit()

    return jsonify({
        "message": "Note updated successfully!",
        "note": {
            "id": note.id,
            "title" : note.title,
            "content": note.content
        }
    }),200

@app.route('/api/notes/<int:note_id>', methods = ['DELETE'])
def delete_note(note_id):
    note = Note.query.get(note_id)

    if not note:
        return jsonify({"message": "Note not found."}),404
    
    db.session.delete(note)
    db.session.commit()

    return jsonify({"message":" Note deleted successfully."}), 200
    
        
       
import sqlite3

def init_db():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Call this before running the Flask app
init_db()

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error', 'message': 'Something went wrong on our side.'}), 500
   
    




if __name__ == '__main__':

    app.run(debug=True)