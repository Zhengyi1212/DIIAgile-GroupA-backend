from flask import Flask, request, jsonify, Blueprint

import json
import os

# Define the Blueprint for sign-up
signup_bp = Blueprint("sign_up", __name__)



# Modification: 1.register via email
        #       2. verify subfix of the email to ensure it is a dundee eami
          #     3. username and password


database_file = 'database.txt'

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


    database = {}
    if os.path.exists(database_file):
        with open(database_file, "r") as file:
            database = json.load(file)

    # Check if the username already exists
    if email in database:
        return jsonify({"success": False, "message": "Account already exists with the given email"}), 401

    # Add new user to the database
    database[email] = {"username":username,"password": password, "role": role}
    print(email)
    # Save the updated database
    with open(database_file, "w") as file:
        json.dump(database, file, indent=4)

    return jsonify({"success": True, "message": "Registration successful"})

