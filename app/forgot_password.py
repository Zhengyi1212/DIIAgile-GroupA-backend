from flask import Blueprint, request, jsonify
from .models import User, get_db
import time, random, os, hashlib
from .login import send_email  # 使用已实现的邮件发送函数
from dotenv import load_dotenv

load_dotenv()

forgot_bp = Blueprint("forgot", __name__)
reset_code_store = {}  # email -> (code, expires_at)

# 工具函数：SHA-256 加密
def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# 发送验证码（支持重复发送）
@forgot_bp.route("/forgot/send-code", methods=["POST"])
def send_reset_code():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400

    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return jsonify({"success": False, "message": "No user found with this email"}), 404

    code = str(random.randint(100000, 999999))
    expires_at = time.time() + 300  # 5分钟有效

    reset_code_store[email] = (code, expires_at)

    send_email(
        to_email=email,
        subject="🔐 Reset Your Password",
        html_body=f"""
            <p>Hello <strong>{user.username}</strong>,</p>
            <p>Your password reset verification code is:</p>
            <h2>{code}</h2>
            <p>This code is valid for 5 minutes.</p>
        """
    )

    return jsonify({"success": True, "message": "Verification code sent"}), 200


# 验证验证码
@forgot_bp.route("/forgot/verify-code", methods=["POST"])
def verify_reset_code():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")

    stored = reset_code_store.get(email)
    if not stored:
        return jsonify({"success": False, "message": "No code found for this email"}), 400

    real_code, expires_at = stored
    if time.time() > expires_at:
        return jsonify({"success": False, "message": "Code expired"}), 400
    if code != real_code:
        return jsonify({"success": False, "message": "Incorrect code"}), 400

    return jsonify({"success": True, "message": "Code verified"}), 200


# 重设密码（使用验证码校验）
@forgot_bp.route("/forgot/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")
    new_password = data.get("new_password")

    stored = reset_code_store.get(email)
    if not stored:
        return jsonify({"success": False, "message": "No code found"}), 400

    real_code, expires_at = stored
    if time.time() > expires_at:
        return jsonify({"success": False, "message": "Code expired"}), 400
    if code != real_code:
        return jsonify({"success": False, "message": "Invalid code"}), 400

    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    user.password_hash = hash_password(new_password)
    db.commit()

    # 清除验证码（只可使用一次）
    del reset_code_store[email]

    return jsonify({"success": True, "message": "Password reset successfully"}), 200
