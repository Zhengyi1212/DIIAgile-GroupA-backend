from flask import Flask, send_file,Blueprint
from .models import LogTable, get_db
import pandas as pd


log_bp = Blueprint("export_logs", __name__)


# 导出 Excel 文件的路由
@log_bp.route('/export_logs')
def export_logs():
    db = next(get_db())
    logs = db.query(LogTable)\
        .all()

    # 转换数据为 DataFrame
    data = {
        "ID": [log.id for log in logs],
        "Timestamp": [log.event_time for log in logs],
        "Description": [log.event_description for log in logs]
    }

    df = pd.DataFrame(data)

    # 生成 Excel 文件
    file_path = "logs_export.xlsx"
    df.to_excel(file_path, index=False)

    # 提供文件下载
    return send_file("D:\\Agile\\backend\\agilebackend\\logs_export.xlsx", as_attachment=True)


