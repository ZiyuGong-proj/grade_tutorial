# user_service.py
from flask import Flask, jsonify, request
import sqlite3
import uuid

app = Flask(__name__)

def init_user_db():
    conn = sqlite3.connect('user_service.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "user_service"}), 200

@app.route('/users', methods=['POST'])
def register():
    data = request.json
    user_id = str(uuid.uuid4())
    
    conn = sqlite3.connect('user_service.db')
    c = conn.cursor()
    
    try:
        c.execute(
            "INSERT INTO users (id, username, email, password) VALUES (?, ?, ?, ?)",
            (user_id, data['username'], data['email'], data['password'])
        )
        conn.commit()
        return jsonify({"message": "User registered successfully", "user_id": user_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username or email already exists"}), 400
    finally:
        conn.close()

@app.route('/users/login', methods=['POST'])
def login():
    data = request.json
    
    conn = sqlite3.connect('user_service.db')
    c = conn.cursor()
    
    c.execute(
        "SELECT id, username FROM users WHERE username=? AND password=?",
        (data['username'], data['password'])
    )
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({"message": "Login successful", "user_id": user[0], "username": user[1]}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    conn = sqlite3.connect('user_service.db')
    c = conn.cursor()
    
    c.execute("SELECT id, username, email FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            "user_id": user[0],
            "username": user[1],
            "email": user[2]
        }), 200
    else:
        return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    init_user_db()
    app.run(debug=True, host='0.0.0.0', port=5001)
