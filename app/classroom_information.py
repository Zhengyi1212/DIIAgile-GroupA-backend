from flask import Blueprint, jsonify, request
from .models import Classroom, get_db  # assuming model.py is in the same directory


classroom_bp = Blueprint('classroom_information', __name__)

@classroom_bp.route('/classrooms', methods=['GET'])
def get_classrooms():
    """
    Retrieve all classroom records from the database and return them as JSON.
    """
    print("Access this method!")
    
    db = next(get_db())
    try:
        classrooms = db.query(Classroom).all()
        classroom_list = []
        for classroom in classrooms:
            classroom_list.append({
                "classroom_id": classroom.classroom_id,
                "building": classroom.building,
                "floor": classroom.floor,
                "classroom_name": classroom.classroom_name,
                "start_time": classroom.start_time.isoformat() if classroom.start_time else None,
                "capacity": classroom.capacity,
                "device": classroom.device,
                "is_available": classroom.is_available
            })
        print("Classroom information retrived!")
        return jsonify({"success": True,"classrooms": classroom_list}), 200
    except Exception as e:
        return jsonify({"success": True, "message": f"An error occurred: {str(e)}"}), 500
