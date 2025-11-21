# monolithic_app.py
from flask import Flask, jsonify, request
import sqlite3
import uuid

app = Flask(__name__)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    
    # 创建用户表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # 创建订单表
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# 用户注册
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user_id = str(uuid.uuid4())
    
    conn = sqlite3.connect('ecommerce.db')
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

# 用户登录
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    
    conn = sqlite3.connect('ecommerce.db')
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

# 创建订单
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    
    # 验证用户存在
    c.execute("SELECT id FROM users WHERE id=?", (data['user_id'],))
    if not c.fetchone():
        return jsonify({"error": "User not found"}), 404
    
    order_id = str(uuid.uuid4())
    
    try:
        c.execute(
            "INSERT INTO orders (id, user_id, product_name, quantity, price) VALUES (?, ?, ?, ?, ?)",
            (order_id, data['user_id'], data['product_name'], data['quantity'], data['price'])
        )
        conn.commit()
        return jsonify({"message": "Order created successfully", "order_id": order_id}), 201
    finally:
        conn.close()

# 获取用户订单
@app.route('/users/<user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    
    # 验证用户存在
    c.execute("SELECT username FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    c.execute(
        "SELECT id, product_name, quantity, price FROM orders WHERE user_id=?",
        (user_id,)
    )
    orders = c.fetchall()
    
    order_list = []
    for order in orders:
        order_list.append({
            "order_id": order[0],
            "product_name": order[1],
            "quantity": order[2],
            "price": order[3]
        })
    
    conn.close()
    return jsonify({"username": user[0], "orders": order_list}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
