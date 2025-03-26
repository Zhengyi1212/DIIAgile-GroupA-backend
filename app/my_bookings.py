from flask import Blueprint, request, jsonify
from .models import Booking, get_db,User

from sqlalchemy.orm import joinedload

import os
from dotenv import load_dotenv

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
load_dotenv()
mybooking_bp = Blueprint("my_bookings", __name__)

def send_cancellation_email(to_email, classroom_name, start_time):
    sender_email = os.getenv("MAIL_SENDER_EMAIL")
    sender_password = os.getenv("MAIL_SENDER_PASSWORD")
    smtp_server = os.getenv("MAIL_SMTP_HOST", "smtp.qq.com")
    smtp_port = int(os.getenv("MAIL_SMTP_PORT", 587))

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📢 Booking Cancellation Notice"
    msg["From"] = sender_email
    msg["To"] = to_email

    html = f"""
    <p>Dear user,</p>
    <p>Your booking for <strong>{classroom_name}</strong> at <strong>{start_time}</strong> has been <span style='color:red;'>cancelled</span>.</p>
    <p>If this wasn't you, please contact the admin immediately.</p>
    <p>Best regards,<br>Booking System</p>
    """
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            print(f"✅ Cancellation email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send cancellation email: {e}")
@mybooking_bp.route('/mybookings/cancel', methods=['POST'])
def cancel_booking():
    data = request.get_json()
    booking_id = data.get("booking_id")

    db = next(get_db())
    try:
        booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
        if not booking:
            return jsonify({"success": False, "message": "Booking not found"}), 404

        classroom_name = booking.classroom.classroom_name
        start_time = booking.classroom.start_time
        user_email = booking.user_email

        db.delete(booking)
        db.commit()

        send_cancellation_email(user_email, classroom_name, start_time)

        return jsonify({"success": True, "message": "Booking cancelled and email sent."}), 200

    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        db.close()

@mybooking_bp.route('/mybookings', methods=['POST'])
def get_bookings():
   data = request.get_json()
   if not data or 'email' not in data:
       return jsonify({"success": False, "message": "Invalid request data"}), 400

   email = data.get('email')
   print(f"Fetching bookings for email: {email}")

   # **解包 get_bookings_from_database 返回的字典和状态码**
   response_data, status_code = get_bookings_from_database(email)

   return jsonify(response_data), status_code


def get_bookings_from_database(email):
    db = next(get_db())

    try:
        user = db.query(User).filter(User.email == email).first()
        if user.role=="Admin":
               bookings = db.query(Booking).options(joinedload(Booking.classroom)).all()
        else:
               bookings = db.query(Booking)\
               .options(joinedload(Booking.classroom))\
               .filter(Booking.user_email == email)\
               .all()

        if not bookings:
            return {"success": False, "message": "No bookings found"}, 404

        result = []
        for booking in bookings:
            result.append({
                "booking_id": booking.booking_id,
                "user_email": booking.user_email,
                "classroom_details": {
                    "classroom_id": booking.classroom.classroom_id,
                    "building": booking.classroom.building,
                    "floor": booking.classroom.floor,
                    "classroom_name": booking.classroom.classroom_name,
                    "start_time": booking.classroom.start_time,
                    "capacity": booking.classroom.capacity,
                    "device": booking.classroom.device,
                    "isAvailable": booking.classroom.isAvailable
                }
            })

        return {"bookings": result, "success": True}, 200

    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}, 500

    finally:
        db.close()


