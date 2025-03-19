from flask import Blueprint, request, jsonify
from .models import Booking, get_db

from sqlalchemy.orm import joinedload

mybooking_bp = Blueprint("my_bookings", __name__)


@mybooking_bp.route('/mybookings', methods=['POST'])
def get_bookings():
   data = request.get_json()
   if not data:
        return jsonify({"success": False, "message": "Invalid request data"}), 400

   email = data.get('email')

   bookings = get_bookings_from_database(email)

   return jsonify({'bookings':bookings,"success": False, "message": "Account already exists with the given email"})


def get_bookings_from_database(email):
   db = next(get_db()) 
    
   try :
       bookings = db.query(Booking)\
        .options(joinedload(Booking.classroom_id))\
        .filter(Booking.user_email == email)\
        .all()

       if not bookings:
            return jsonify({"message": "No bookings found"}), 404

       result = []
       for booking in bookings:
            result.append({
            "booking_id": booking.booking_id,
            "classroom_details": {
                "classroom_id": booking.classroom.classroom_id,
                "building": booking.classroom.building,
                "floor": booking.classroom.floor,
                "classroom_name": booking.classroom.classroom_name,
                "capacity": booking.classroom.capacity,
                "device": booking.classroom.device,
                "is_availble": booking.classroom.is_availble
            }
        })
       return jsonify(result)
   except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    
   finally:
        db.close()

