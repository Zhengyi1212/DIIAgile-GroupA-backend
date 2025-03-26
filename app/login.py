from flask import Flask, request, jsonify, Blueprint
import jwt
import datetime
import os
from .models import User, get_db

import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# login.py 开头
from collections import defaultdict
import time
import random

# 临时内存结构：email -> (code, expires_at)
email_verification_store = {}

load_dotenv()
login_bp = Blueprint("login", __name__)

secret_key = "your_secret_key"

def send_email(to_email: str, subject: str, html_body: str):
    smtp_server = "smtp.qq.com"
    smtp_port = 587
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
            print(f"✅ Login email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send login email: {e}")


@login_bp.route('/login', methods=['POST'])
def login_with_verification():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request data"}), 400

    email = data.get("email")
    password = data.get("password")

    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()

    if not user or user.password_hash != static_hash(password):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    # ✅ 生成 6 位验证码并保存（5分钟有效）
    code = str(random.randint(100000, 999999))
    expires_at = time.time() + 300  # 5 分钟

    email_verification_store[email] = (code, expires_at)

    # ✅ 发验证码邮件
    send_email(
        to_email=email,
        subject="🔐 Your Login Verification Code",
        html_body=f"""
        <p>Hi <strong>{user.username}</strong>,</p>
        <p>Your login verification code is:</p>
        <h2>{code}</h2>
        <p>This code is valid for 5 minutes.</p>
        """
    )

    return jsonify({
        "success": True,
        "message": "Verification code sent to email."
    }), 200

@login_bp.route('/login/verify', methods=['POST'])
def login_verify():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")
    print(f"Received email: {email}, code: {code}")
    print("Stored:", email_verification_store.get(email))
    stored = email_verification_store.get(email)
    if not stored:
        return jsonify({"success": False, "message": "No verification code found"}), 400

    real_code, expires_at = stored
    if time.time() > expires_at:
        return jsonify({"success": False, "message": "Verification code expired"}), 400
    if code != real_code:
        return jsonify({"success": False, "message": "Invalid verification code"}), 400

    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    token = jwt.encode({
        "username": user.username,
        "role": user.role,
        "email": user.email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, os.getenv("JWT_SECRET"), algorithm="HS256")

    # 清除验证码
    del email_verification_store[email]

    return jsonify({
        "success": True,
        "token": token,
        "username": user.username,
        "role": user.role
    })
    
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