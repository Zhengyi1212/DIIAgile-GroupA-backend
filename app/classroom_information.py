from flask import Blueprint, jsonify, request
from .models import Classroom, get_db, Booking,LogTable  # assuming model.py is in the same directory
from sqlalchemy import func
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() 

classroom_bp = Blueprint('classroom_information', __name__)

from flask import request, jsonify
from datetime import datetime, timezone, timedelta
from collections import defaultdict


def create_ics_content(subject, start_dt, end_dt, location, description):
   
   
    beijing_tz = timezone(timedelta(hours=8))
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=beijing_tz)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=beijing_tz)

    start_utc = start_dt.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    end_utc = end_dt.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Classroom Reservation System//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
DTSTART:{start_utc}
DTEND:{end_utc}
DTSTAMP:{dtstamp}
UID:{dtstamp}@classroom-booking.local
SUMMARY:{subject}
LOCATION:{location}
DESCRIPTION:{description}
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT10M
DESCRIPTION:Reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR
"""
def send_booking_email_with_calendar(to_email, classroom_name, start_time_str, end_time_str):
   
    smtp_server = "smtp.qq.com"
    smtp_port = 587
    sender_email = os.getenv("MAIL_SENDER_EMAIL")
    sender_password = os.getenv("MAIL_SENDER_PASSWORD")

   
    subject = f"Booking Confirmation: {classroom_name}"
    location = classroom_name
    description = f"Your classroom {classroom_name} has been booked."
    start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
    end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%S")

    # email content
    msg = MIMEMultipart("mixed")
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    body = f"""
    <p>Dear user,</p>
    <p>Your classroom <strong>{classroom_name}</strong> has been successfully booked.</p>
    <p>📅 Time: {start_time_str} to {end_time_str}</p>
    <p>Please find the attached calendar invite to add this event to your calendar.</p>
    """

    msg.attach(MIMEText(body, "html"))

    # 
    ics_content = create_ics_content(subject, start_time, end_time, location, description)
    part = MIMEBase("text", "calendar", method="REQUEST", name="invite.ics")
    part.set_payload(ics_content)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment; filename=invite.ics")
    msg.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            print("✅ Email with calendar invite sent successfully")
    except Exception as e:
        print("❌ Failed to send email with calendar:", e)


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
        
        # Define the five default time spans in order
        default_times = ['08:00:00', '10:00:00', '14:00:00', '16:00:00', '19:00:00']
        
        # Create a dictionary to map time strings to their availability from the database
        available_times = {}
        for classroom in classrooms:
            if classroom.start_time:
                time_str = classroom.start_time.time().isoformat()
                available_times[time_str] = classroom.isAvailable
        
        # Build the time_spans list based on default_times and available_times
        time_spans = []
        for time_str in default_times:
            is_available = available_times.get(time_str, False)
            time_spans.append({
                "start_time": time_str,
                "is_available": is_available
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

from datetime import datetime, timedelta


def create_booking(data):
    """
    Create a booking for a specific classroom occurrence and log the event.
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

        # Calculate the end time (start_time + 2 hours)
        start_time_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        end_time_dt = start_time_dt + timedelta(hours=2)

        # Create a new log entry
        event_description = f"{user_email} booked {classroom_name} from {start_time} to {end_time_dt.strftime('%Y-%m-%dT%H:%M:%S')}"
        new_log = LogTable(event_description=event_description)

        db.add(new_log)
        db.commit()

        # Send confirmation email
        send_booking_email_with_calendar(
            to_email=user_email,
            classroom_name=classroom_name,
            start_time_str=start_time,
            end_time_str=end_time_dt.strftime('%Y-%m-%dT%H:%M:%S')
        )

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
    
    
@classroom_bp.route('/classroom_information/modify_room', methods=['POST'])
def modify_room():
    db = next(get_db())
    data = request.get_json()

    classroom_name = data.get("classroom_name")
    new_capacity = data.get("new_capacity")
    device = data.get("device")
    disabled_slots = data.get("disabled_slots", [])
    admin_email=data.get("admin_email")
    if not classroom_name:
        return jsonify({"success": False, "message": "Missing classroom name."}), 400

    try:
       
        if new_capacity:
            db.query(Classroom).filter(
                Classroom.classroom_name == classroom_name
            ).update({Classroom.capacity: int(new_capacity)})

        if device:
            db.query(Classroom).filter(
                Classroom.classroom_name == classroom_name
            ).update({Classroom.device: device})

        updated_count = 0
        canceled_count = 0
        print("🛑 Disabled time span:")
        for ts in disabled_slots:
            print(" -", ts)
            try:
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

            classroom = db.query(Classroom).filter(
                Classroom.classroom_name == classroom_name,
                Classroom.start_time == dt
            ).first()

            if classroom:
              
                bookings = db.query(Booking).filter(
                    Booking.classroom_id == classroom.classroom_id
                ).all()

                for booking in bookings:
                    db.delete(booking)
                    canceled_count += 1
                    send_disable_notice_email(booking.user_email, classroom_name, ts)

                classroom.isAvailable = False
                updated_count += 1
                if admin_email:
                    admin_booking=Booking(
                        user_email=admin_email,
                        classroom_id=classroom.classroom_id
                   )
                    db.add(admin_booking)
        log_message = f"Admin modified {classroom_name} | capacity={new_capacity}, device={device}, disabled={updated_count} slots, canceled={canceled_count} bookings"
        db.add(LogTable(event_description=log_message))
        db.commit()

        return jsonify({"success": True, "message": f"{updated_count} time slots disabled, {canceled_count} bookings canceled."}), 200

    except Exception as e:
        db.rollback()
        print("❌ Error modifying room:", e)
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


from datetime import datetime
from sqlalchemy.exc import IntegrityError

from datetime import datetime, timedelta
from flask import request, jsonify
from datetime import datetime
from .models import Classroom, LogTable, get_db
def send_disable_notice_email(to_email, classroom_name, canceled_time):
    subject = f"⛔ Your Booking for {classroom_name} Was Canceled"
    content = f"""
    Dear user,<br><br>
    Your booking for <b>{classroom_name}</b> at <b>{canceled_time}</b> has been <b>canceled</b> by the administrator due to room being disabled.<br><br>
    Please select another time slot if needed.<br><br>
    Sorry for the inconvenience.<br>
    """

    msg = MIMEText(content, "html")
    msg["Subject"] = subject
    msg["From"] = os.getenv("MAIL_SENDER_EMAIL")
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.qq.com", 587) as server:
            server.starttls()
            server.login(os.getenv("MAIL_SENDER_EMAIL"), os.getenv("MAIL_SENDER_PASSWORD"))
            server.sendmail(msg["From"], to_email, msg.as_string())
            print(f"📧 Disable notice sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}:", e)