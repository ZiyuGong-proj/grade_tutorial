# order_service.py
from flask import Flask, jsonify, request
import sqlite3
import uuid
import requests

app = Flask(__name__)

def init_order_db():
    conn = sqlite3.connect('order_service.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def validate_user(user_id):
    """验证用户是否存在（调用用户服务）"""
    try:
        response = requests.get(f'http://localhost:5001/users/{user_id}')
        return response.status_code == 200
    except:
        return False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "order_service"}), 200

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    
    # 验证用户是否存在
    if not validate_user(data['user_id']):
        return jsonify({"error": "User not found"}), 404
    
    order_id = str(uuid.uuid4())
    
    conn = sqlite3.connect('order_service.db')
    c = conn.cursor()
    
    try:
        c.execute(
            "INSERT INTO orders (id, user_id, product_name, quantity, price) VALUES (?, ?, ?, ?, ?)",
            (order_id, data['user_id'], data['product_name'], data['quantity'], data['price'])
        )
        conn.commit()
        return jsonify({"message": "Order created successfully", "order_id": order_id}), 201
    finally:
        conn.close()

@app.route('/orders/user/<user_id>', methods=['GET'])
def get_user_orders(user_id):
    # 验证用户是否存在
    if not validate_user(user_id):
        return jsonify({"error": "User not found"}), 404
    
    conn = sqlite3.connect('order_service.db')
    c = conn.cursor()
    
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
    return jsonify({"user_id": user_id, "orders": order_list}), 200

if __name__ == '__main__':
    init_order_db()
    app.run(debug=True, host='0.0.0.0', port=5002)
