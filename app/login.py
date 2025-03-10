from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import jwt
import datetime
import json
import os

SECRET_KEY = "your_secret_key"
login_bp = Blueprint("login", __name__)

my_path = os.path.abspath(os.path.dirname(__file__))

database_file= os.path.join(my_path, "..\database.txt")
print(database_file)

# login via : email + password

# 模拟数据库用户数据
#users = {
#    "lecturer": {"password": "123456", "role": "Lecturer"},
#    "student": {"password": "123456", "role": "Student"},
#}

def load_users(database_file):
    print(my_path)
    print(database_file)
    """Load user data from the JSON file, or return an empty dictionary if the file does not exist."""
    if os.path.exists(database_file):
        with open(database_file, "r") as file:
            return json.load(file)
    return {}

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request data"}), 400

    username = data.get("username")
    password = data.get("password")
    
    print(username)
    print(password)

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    users = load_users(database_file)
    if username not in users:
        return jsonify({"success": False, "message": "User does not exist. Please register first!"}), 401

    user = users[username]
    if user and user["password"] == password:
        token = jwt.encode(
            {
                "user_id": username,
                "role": user["role"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # 1小时过期
            },
            SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify({"success": True, "token": token})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401