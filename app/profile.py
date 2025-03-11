from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import json
import os

my_path = os.path.abspath(os.path.dirname(__file__))
database_file= os.path.join(my_path, "..\database.txt")

profile_bp = Blueprint("profile", __name__)

def load_users(database_file):
    #print(my_path)
    #print(database_file)
    """Load user data from the JSON file, or return an empty dictionary if the file does not exist."""
    if os.path.exists(database_file):
        with open(database_file, "r") as file:
            return json.load(file)
    return {}


@profile_bp.route("/profile",methods=["POST"])
def edit_profile():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request data"}), 400
    
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")
    
    users = load_users(database_file)
    
    
    