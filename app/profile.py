from flask import Flask, request, jsonify, Blueprint
import json
import os
import jwt
import datetime
from .models import get_db,User
from .login import  static_hash


SECRET_KEY = "your_secret_key"

profile_bp = Blueprint("profile", __name__)

@profile_bp.route('/verify-password', methods=["POST","OPTIONS"])
def verify_password():
    if request.method == "OPTIONS":
        response = jsonify()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response
    
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({
            "success": False,
            "message": "Missing required fields"
        }), 400

    email = data["email"].strip()
    password = data["password"].strip()

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password cannot be empty"
        }), 400
    email = data.get("email")
    input_password = data.get("password")

    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()

    success = user and user.password_hash == static_hash(input_password)
    
    return jsonify({"success": success})


@profile_bp.route('/profile', methods=["POST","OPTIONS"])
def edit_profile():
    if request.method == "OPTIONS":
        response = jsonify()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response
    
    data = request.get_json()
    email = data.get("email")
    new_username = data.get("username")
    new_password = data.get("password")  # maybe null

    db = next(get_db())
    targetUser = db.query(User).filter(User.email == email).first()
    
    if not targetUser:
        return jsonify({"success": False, "message": "User not found"}), 404

    if new_password:  # only change when input new password
        targetUser.password_hash = static_hash(new_password)

    targetUser.username = new_username
    db.commit()
    db.refresh(targetUser)

    token = jwt.encode(
        {"username": targetUser.username, "role": targetUser.role, "email": email, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({"success": True, "token": token})
   
        
        
        