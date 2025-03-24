from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine,func,Boolean

from sqlalchemy.orm import relationship, sessionmaker,declarative_base
import pymysql  # 确保安装了 pymysql

# MySQL 连接信息
DATABASE_URL = "mysql+pymysql://root:xd03@localhost:3306/booksystem"

# 创建 SQLAlchemy 连接
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True)  # echo=True 用于调试，生产环境可设为 False
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 预定表
class Booking(Base):
    __tablename__ = 'bookings'
    booking_id = Column(Integer, primary_key=True)
    classroom_id = Column(Integer, ForeignKey('classrooms.classroom_id'), nullable=False)
    user_email = Column(String(100), ForeignKey('users.email'), nullable=False)
    
    users = relationship('User', back_populates='bookings')
    classroom = relationship("Classroom", back_populates="bookings")

    def __repr__(self):
        return f"<Booking(booking_id={self.booking_id}, user_email='{self.user_email}', classroom_id={self.classroom_id})>"

# 用户表
class User(Base):
    __tablename__ = 'users'
    email = Column(String(100), primary_key=True, unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50))

    bookings = relationship("Booking", back_populates="users")

    def __repr__(self):
        return f"<User(email='{self.email}', username='{self.username}', role='{self.role}')>"


class Classroom(Base):
    __tablename__ = 'classrooms'

    classroom_id = Column(Integer, primary_key=True)
    building = Column(String(50), nullable=False)
    floor = Column(Integer, nullable=False)
    classroom_name = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False)
    capacity = Column(Integer, nullable=False)
    device = Column(String(255), nullable=False)
    isAvailable = Column(Boolean, nullable=False, default=True)
    forstudent =  Column(Boolean, nullable=False, default=True)
    
    bookings = relationship("Booking", back_populates="classroom")

    def __repr__(self):
        return f"<Classroom(classroom_id={self.classroom_id}, building='{self.building}', floor={self.floor}, classroom_name='{self.classroom_name}', start_time='{self.start_time}')>"

class LogTable(Base):
    __tablename__ = 'logtable'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_time = Column(DateTime, default=func.now())  # 默认当前时间
    event_description = Column(String(255), nullable=False)  # 事件描述

    def __repr__(self):
        return f"<LogTable(log_id={self.id}, event_time='{self.event_time}', event_description='{self.event_description}')>"

# 测试数据库连接
def test_db_connection():
    try:
        with engine.connect() as connection:
            print("✅ 成功连接到 MySQL 数据库！")
            db = next(get_db())
            ers = db.query(LogTable)\
             .all()
            print(ers)

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

