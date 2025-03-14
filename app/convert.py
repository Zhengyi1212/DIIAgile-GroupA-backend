import sqlite3
import pandas as pd

def create_database(db_name="class_schedule.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 创建课程安排表（只保留 free_slots）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            free_slots TEXT
        )
    ''')

    conn.commit()
    conn.close()

def insert_schedule_data(csv_file, db_name="class_schedule.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 获取课程表数据，计算空闲时段
    occupied_slots = set()

    # 读取单个 CSV 文件
    df = pd.read_csv(csv_file)

    # 打印列名以调试
    print("Columns in CSV:", df.columns)

    # 遍历每一行（表示不同的节次）
    for period, row in df.iterrows():
        for day in range(1, 8):  # 1-7 表示星期一到星期日
            day_column = df.columns[day]  # 获取星期几的列名（星期一，星期二，...）
            room_data = row[day_column]  # 获取对应列的课程信息（课程名称）

            if pd.notnull(room_data):  # 如果该时段有课
                week = 1  # 假设是第 1 周
                key = f"{week:02d}-{day}-{period+1}"  # 格式化为 week-day-period 形式
                occupied_slots.add(key)

    # 创建空闲时段信息并更新到数据库
    free_slots = set()
    for day in range(1, 8):  # 1-7 表示周一到周日
        for period in range(1, 6):  # 假设课程安排有 5 个时段（1-5）
            key = f"01-{day}-{period}"  # 只考虑 1 周
            if key not in occupied_slots:
                free_slots.add(key)

    # 将空闲时段存入数据库
    free_slots_str = ",".join(sorted(free_slots))
    cursor.execute(''' 
        REPLACE INTO schedule (free_slots)
        VALUES (?) 
    ''', (free_slots_str,))

    conn.commit()
    conn.close()


def get_all_free_slots(db_name="class_schedule.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('SELECT free_slots FROM schedule')
    free_slots = cursor.fetchall()

    conn.close()
    return [free_slot[0] for free_slot in free_slots]

if __name__ == "__main__":
    create_database()
    insert_schedule_data(r"C:\Users\30208\Desktop\data(3)\101教室\第1周.csv")  # 替换为实际的单个 CSV 文件路径
    free_slots_list = get_all_free_slots()
    for free_slots in free_slots_list:
        print(f"Free slots: {free_slots}")