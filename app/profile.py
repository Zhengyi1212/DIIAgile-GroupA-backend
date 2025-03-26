from flask import Flask, request, jsonify, Blueprint
import json
import os
import jwt
import datetime
from .models import get_db,User
from .login import  static_hash


SECRET_KEY = "your_secret_key"

profile_bp = Blueprint("profile", __name__)

@profile_bp.route('/profile', methods=["POST"])
def edit_profile():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request data"}), 400
    
    email = data.get("email")
    print(f'Email:{email}')
    new_username = data.get("username")
    print(f'USername:{new_username}')
    new_password = data.get("password")
    
    db = next(get_db())
    
    targetUser = db.query(User).filter(User.email == email).first()
    targetUser.username = new_username
    targetUser.password_hash = static_hash(new_password)
   
    
    
    token = jwt.encode(
        {
            "username": targetUser.username,
            "role": targetUser.role,
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  
        },
            SECRET_KEY,
            algorithm="HS256"
        )
    db.commit()
    db.refresh(targetUser)

   
    return jsonify({"success": True, "token": token})
   
        
        
        