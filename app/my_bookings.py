from flask import Blueprint, request, jsonify
from .models import Booking, get_db,User

from sqlalchemy.orm import joinedload

mybooking_bp = Blueprint("my_bookings", __name__)


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
                "user_role": booking.users.role,
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


