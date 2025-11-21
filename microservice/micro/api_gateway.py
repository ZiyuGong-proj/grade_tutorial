# api_gateway.py
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# 服务注册信息
SERVICES = {
    'user_service': 'http://localhost:5001',
    'order_service': 'http://localhost:5002'
}

@app.route('/health', methods=['GET'])
def health_check():
    # 检查所有服务的健康状态
    health_status = {}
    for service_name, service_url in SERVICES.items():
        try:
            response = requests.get(f'{service_url}/health', timeout=2)
            health_status[service_name] = response.json()
        except:
            health_status[service_name] = {"status": "unhealthy"}
    
    return jsonify(health_status), 200

@app.route('/users', methods=['POST'])
def register_user():
    """用户注册 - 路由到用户服务"""
    try:
        response = requests.post(
            f"{SERVICES['user_service']}/users",
            json=request.json,
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException:
        return jsonify({"error": "User service unavailable"}), 503

@app.route('/users/login', methods=['POST'])
def login_user():
    """用户登录 - 路由到用户服务"""
    try:
        response = requests.post(
            f"{SERVICES['user_service']}/users/login",
            json=request.json,
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException:
        return jsonify({"error": "User service unavailable"}), 503

@app.route('/orders', methods=['POST'])
def create_order():
    """创建订单 - 路由到订单服务"""
    try:
        response = requests.post(
            f"{SERVICES['order_service']}/orders",
            json=request.json,
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException:
        return jsonify({"error": "Order service unavailable"}), 503

@app.route('/users/<user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """获取用户订单 - 路由到订单服务"""
    try:
        response = requests.get(
            f"{SERVICES['order_service']}/orders/user/{user_id}",
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException:
        return jsonify({"error": "Order service unavailable"}), 503

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
