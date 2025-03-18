from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()
engine = create_engine('mysql:///your_database.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Booking(Base):
    __tablename__ = 'bookings'

    booking_id = Column(Integer, primary_key=True)
    classroom_id = Column(Integer, ForeignKey('classrooms.classroom_id'), nullable=False)
    user_email = Column(String(100), ForeignKey('users.email'), nullable=False)

    user = relationship('User', back_populates='bookings')
    classroom = relationship("Classroom", back_populates="bookings")
    def __repr__(self):
        return f"<Booking(booking_id={self.booking_id}, email='{self.email}', classroom_id={self.classroom_id})>"


class User(Base):
    """User model."""
    __tablename__ = 'users'
    email = Column(String(100), primary_key=True, unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50))
    bookings = relationship("Booking", backref="users")

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
    device = Column(Integer, nullable=False)
    
   
    
    
    def __repr__(self):
        return f"<Classroom(classroom_id={self.classroom_id}, building='{self.building}', floor={self.floor}, classroom_name='{self.classroom_name}', start_time='{self.start_time}')>"
    
def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()