from flask import Flask, send_file,Blueprint
import pandas as pd
import os
from .models import get_db,LogTable

log_bp = Blueprint("export_logs", __name__)



@log_bp.route('/export_logs')
def export_logs():
    db = next(get_db())
    logs = db.query(LogTable)\
        .all()

 
    data = {
        "ID": [log.id for log in logs],
        "Timestamp": [log.event_time for log in logs],
        "Description": [log.event_description for log in logs]
    }

    df = pd.DataFrame(data)

    # 
    file_path = "logs_export.xlsx"
    df.to_excel(file_path, index=False)

   

    return send_file("D:\CSU-DUNDEE\JUNIOR-2\AgileProgaming\DiiBookingSystem\DiiBookingSystem-backend\\logs_export.xlsx", as_attachment=True)


