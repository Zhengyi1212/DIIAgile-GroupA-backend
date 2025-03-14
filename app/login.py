from flask import Flask, request, jsonify, Blueprint

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
    #print(my_path)
    #print(database_file)
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
    
    
    email = data.get("email")
    password = data.get("password")
    

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    users = load_users(database_file)
    if email not in users:
        return jsonify({"success": False, "message": "Account does not exist. Please register first!"}), 401

    user = users[email]
    if user and user["password"] == password:
        token = jwt.encode(
            {
                "username": user["username"],
                "role": user["role"],
                "email": email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # 1小时过期
            },
            SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify({"success": True, "token": token})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401