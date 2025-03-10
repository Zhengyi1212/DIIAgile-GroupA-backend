from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
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

    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    if not username or not password or not role:
        return jsonify({"success": False, "message": "Username, password, and role are required"}), 400

    print(username)

    # Load existing database
    database = {}
    if os.path.exists(database_file):
        with open(database_file, "r") as file:
            database = json.load(file)

    # Check if the username already exists
    if username in database:
        return jsonify({"success": False, "message": "Username already exists"}), 401

    # Add new user to the database
    database[username] = {"password": password, "role": role}

    # Save the updated database
    with open(database_file, "w") as file:
        json.dump(database, file, indent=4)

    return jsonify({"success": True, "message": "Registration successful"})

