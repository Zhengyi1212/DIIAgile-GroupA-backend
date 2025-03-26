from flask import Flask, request, jsonify, Blueprint
from .models import get_db, User
import json


# Define the Blueprint for sign-up
signup_bp = Blueprint("sign_up", __name__)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import time
import random

load_dotenv() 
email_verification_store = {}  # email -> (code, expires_at)

def send_email(to_email: str, subject: str, html_body: str):
    smtp_server = os.getenv("MAIL_SMTP_HOST", "smtp.qq.com")
    smtp_port = int(os.getenv("MAIL_SMTP_PORT", 587))
    sender_email = os.getenv("MAIL_SENDER_EMAIL")
    sender_password = os.getenv("MAIL_SENDER_PASSWORD")

    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        
@signup_bp.route('/signup/send-code', methods=['POST'])
def send_signup_code():
    data = request.get_json()
    email = data.get("email")

    db = next(get_db())
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return jsonify({"success": False, "message": "Email already registered"}), 400

    code = str(random.randint(100000, 999999))
    expires_at = time.time() + 300  # 5分钟
    email_verification_store[email] = (code, expires_at)

    send_email(
        to_email=email,
        subject="📧 Registration Verification Code",
        html_body=f"<p>Your code is: <strong>{code}</strong>. Valid for 5 mins.</p>"
    )

    return jsonify({"success": True, "message": "Verification code sent"}), 200


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
        print(f"❌ Fail to connect to database: {e}")

    
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