from flask import Blueprint, jsonify, request
from .models import Classroom, get_db, Booking  # assuming model.py is in the same directory
from sqlalchemy import func

classroom_bp = Blueprint('classroom_information', __name__)

from flask import request, jsonify
from datetime import datetime
from collections import defaultdict



@classroom_bp.route('/classrooms', methods=['GET'])
def get_classrooms():
    """
    Retrieve all classroom records from the database, group them by classroom_name and date,
    and return only one record per unique classroom_name and date combination.
    """
    print("Access this method!")
    role = request.args.get('role')
    db = next(get_db())
    try:
        classrooms = db.query(Classroom).all()
        
        # Use a set to track unique classroom_name and date combinations
        unique_classrooms = set()
        
        # List to store the final response
        classroom_list = []
        
        for classroom in classrooms:
            if role == "Student" and not classroom.forstudent:
                continue
            
            # Extract date from start_time
            if classroom.start_time:
                date = classroom.start_time.date().isoformat()  # Format date as "YYYY-MM-DD"
            else:
                date = None
            
            # Create a unique key for the classroom_name and date combination
            unique_key = (classroom.classroom_name, date)
            
            # If this combination hasn't been processed yet, add it to the response
            if unique_key not in unique_classrooms:
                unique_classrooms.add(unique_key)
                classroom_list.append({
                    "building": classroom.building,
                    "floor": classroom.floor,
                    "classroom_name": classroom.classroom_name,
                    "date": date,
                    "capacity": classroom.capacity,
                    "device": classroom.device
                })
        
        print("Classroom information retrieved!")
        return jsonify({"success": True, "classrooms": classroom_list}), 200
    except Exception as e:
        print("Something went wrong!!!")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

def get_next_booking_id(db):
    max_id = db.query(func.max(Booking.booking_id)).scalar()
    return max_id + 1 if max_id else 1  # Handle empty table case]]


from flask import request, jsonify
from datetime import datetime

@classroom_bp.route('/classrooms', methods=['POST'])
def handle_classroom_request():
    
    data = request.get_json()  # Parse JSON data from the request body
    
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    request_type = data.get('request_type')
    
    if request_type == "get_classroom":
        # Handle the request for classroom time spans
        return get_classroom(data)
    elif request_type == "booking":
        # Handle the other type of request
        return create_booking(data)
    
    
    else:
        return jsonify({"success": False, "message": "Invalid request_type"}), 400


def get_classroom(data):
    """
    Retrieve a specific classroom's time spans and availability for a given date.
    """
    print("Handling get_classroom request!")
    
    # Extract data from the request body
    classroom_name = data.get('classroom_name')
    print(classroom_name)
    date_str = data.get('date')  # Expected format: "YYYY-MM-DD"
    
    if not classroom_name or not date_str:
        return jsonify({"success": False, "message": "Missing classroom_name or date"}), 400
    
    try:
        # Parse the date string into a date object
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Get the database session
        db = next(get_db())
        
        # Query all records for the given classroom_name and date
        classrooms = db.query(Classroom).filter(
            Classroom.classroom_name == classroom_name,
            func.date(Classroom.start_time) == date  # Use func.date directly
        ).all()
        
        # Extract time spans and availability
        time_spans = []
        for classroom in classrooms:
            if classroom.start_time:
                time = classroom.start_time.time().isoformat()  # Extract time (HH:MM:SS)
                time_spans.append({
                    "start_time": time,
                    "is_available": classroom.isAvailable
                })
        
        # Ensure there are exactly 5 time spans (fill with default values if necessary)
        while len(time_spans) < 5:
            time_spans.append({
                "start_time": "00:00:00",  # Default time
                "is_available": False      # Default availability
            })
        print(len(time_spans))
        # Return the result
        print("Classroom information retrieved!")
        return jsonify({
            "success": True,
            "message": "Information retrieved!",
            "time_spans": time_spans
        }), 200
    
    except Exception as e:
        print("Something went wrong!!!")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500



from datetime import datetime
from sqlalchemy.exc import IntegrityError

def create_booking(data):
    """
    Create a booking for a specific classroom occurrence.
    """
    if not data:
        return jsonify({"success": False, "message": "Invalid request data"}), 400
    
    user_email = data.get("email")
    classroom_name = data.get("classroom_name")
    start_time = data.get("time")  # Expected format: "YYYY-MM-DDTHH:MM:SS"
    
    if not user_email or not classroom_name or not start_time:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    db = next(get_db())
    
    try:
       
        # Fetch the classroom to update its availability
        classroom = db.query(Classroom).filter(
            Classroom.classroom_name == classroom_name,
            Classroom.start_time == start_time
        ).first()
        
        if not classroom:
            return jsonify({"success": False, "message": "Classroom not found"}), 404
        
        if not classroom.isAvailable:
            return jsonify({"success": False, "message": "Classroom is already booked"}), 400
        
        # Get the next booking ID
        booking_id = get_next_booking_id(db)
        
        # Create the new booking
        new_booking = Booking(
            booking_id=booking_id,
            user_email=user_email,
            classroom_id=classroom.classroom_id
        )
        
        # Update classroom availability
        classroom.isAvailable = False
        
        # Add and commit the new booking and classroom update
        db.add(new_booking)
        db.commit()
        
        return jsonify({
            "success": True,
            "message": "Booking created successfully",
            "booking_id": booking_id
        }), 200
    
    except IntegrityError:
        db.rollback()
        return jsonify({"success": False, "message": "Booking ID conflict. Please try again."}), 500
    except Exception as e:
        db.rollback()
        print("Something went wrong!!!")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500