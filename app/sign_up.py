from flask import Flask, request, jsonify, Blueprint
from .models import get_db, User
import json


# Define the Blueprint for sign-up
signup_bp = Blueprint("sign_up", __name__)


@signup_bp.route('/signup', methods=['POST'])
def sign_up():
    # Get data from the frontend
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request data"}), 400
   
    email = data.get("email")
    print(email)
    username = data.get("username")
    print(username)
    password = data.get("password")
    print(password)
    role = data.get("role")

    if not username or not password or not role:
        return jsonify({"success": False, "message": "Email, username, password, and role are required"}), 400
    
    ## start a seesion with db
    db = next(get_db())
    
    try :
        existing_user = db.query(User).filter(User.email == email).first()
        

    # Step 2: If the user exists, return False
        if existing_user:
            return jsonify({"success": False, "message": "Account already exists with the given email"}), 401
        
        # add to database"
        print(email)
        new_user = User(username=username, email=email, role=role,password_hash=static_hash(password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print("Signup sucessfully!")
        return jsonify({"success": True, "message": "Registration successful"})

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")

    
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