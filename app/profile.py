from flask import Flask, request, jsonify, Blueprint
import json
import os
import jwt
import datetime


SECRET_KEY = "your_secret_key"
my_path = os.path.abspath(os.path.dirname(__file__))
database_file= os.path.join(my_path, "..\database.txt")

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
    
    database = {}
    if os.path.exists(database_file):
        with open(database_file, "r") as file:
            database = json.load(file)
    
    
    
    user = database[email]
    user['username'] = new_username
    user['password'] = new_password  
    
    
    with open(database_file, "w") as file:
        json.dump(database, file, indent=4)
    
    token = jwt.encode(
        {
            "username": user["username"],
            "role": user["role"],
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  
        },
            SECRET_KEY,
            algorithm="HS256"
        )
    return jsonify({"success": True, "token": token})
   
        
        
        