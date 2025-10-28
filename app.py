from flask import Flask , request , jsonify 
import sqlite3

app = Flask(__name__)










def get_db_connection():
    conn = sqlite3.connect('notes.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/notes', methods=['GET'])
def get_notes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notes')
    notes = cursor.fetchall()
    conn.close()
    
    #converting them into dic
    notes_list = [dict(note) for note in notes]
    return jsonify(notes_list)
   
@app.route('/api/notes', methods=['POST'])
def create_note():
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Missing JSON data.'}),400

    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': 'Both title and content are required.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO notes (title,content) VALUES (?,?)", (title,content))

    conn.commit()
    note_id = cursor.lastrowid
    
    msg = {
        "id": note_id,
        "title": title,
        "content": content
    }
    conn.close()
    return jsonify(msg), 200


@app.route('/api/notes/<int:note_id>', methods = ['PUT'])
def update_note(note_id):
    data = request.get_json()

    if not data:
        return jsonify({'message': 'Missing JSON data'})

    title = data.get('title')
    content = data.get('content'),400

    if not title or not content:
        return jsonify({'message': 'Both title and contents should be present.'}),400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'UPDATE notes SET title = ? , content = ? WHERE id = ?',
        (title,content, note_id)
    )
    conn.commit()

    #checking if any row was updated
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({
            'error': 'Note not found'
        }), 404
    
    conn.close()
    return jsonify({
        'id': note_id, 
        'title' : title, 
        'content': content
    }), 200

@app.route('/api/notes/<int:note_id>', methods = ['DELETE'])
def delete_note(note_id):
    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()

    if cursor.rowcount == 0:
        
        return jsonify({'error': 'Sorry no note with this id found'}), 404
    conn.close()
    return jsonify({'message': "Note deleted successfully"}), 200
    

        
       
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