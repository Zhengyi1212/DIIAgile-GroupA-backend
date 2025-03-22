from flask import Flask, request, jsonify, Blueprint
import jwt
import datetime
import os
from .models import User, get_db

login_bp = Blueprint("login", __name__)

secret_key = "your_secret_key"


@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request data"}), 400
    
    
    email = data.get("email")
    password = data.get("password")
    
    # start session
    db = next(get_db())
    user_ = db.query(User)\
        .filter(User.email == email)\
        .all()
    if not user_:
        return jsonify({"success": False, "message": "Account does not exist. Please register first!"}), 401

    user = user_[0]
    print(password)
    print(static_hash(password))
    print(user.password_hash)
    if user.password_hash == static_hash(password):
        token = jwt.encode(
            {
                "username": user.username,
                "role": user.role,
                "email": email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # 1小时过期
            },

            secret_key,
            algorithm="HS256"
        )
        print(f'Login sucessfully! Welcome {user.role}')
        return jsonify({"success": True, "token": token})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401
    
import hashlib

# Create a SHA-256 hash of a string
def static_hash(input_string):
    # Encode the string to bytes (required by hashlib)
    input_bytes = input_string.encode('utf-8')
    
    # Create a SHA-256 hash object
    hash_object = hashlib.sha256(input_bytes)
    
    # Get the hexadecimal digest of the hash
    return hash_object.hexdigest()

# Example usage
print(static_hash("hello")) 