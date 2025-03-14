

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """User model."""
    __tablename__ = 'users'
    email = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"

class Classroom(db.Model):
    """Classroom model."""
    __tablename__ = 'classrooms'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campus = db.Column(db.String(100), nullable=False)
    block = db.Column(db.String(50), nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    number = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Classroom {self.campus} - Block {self.block} - Floor {self.floor}>"


class Schedule(db.Model):
    """Schedule model with free_times."""
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    free_times = db.Column(db.String, nullable=False)  # String to store all free times (e.g., "01-1,01-2,02-3")
    classroom = db.relationship('Classroom', backref=db.backref('schedules', lazy=True))
    def __repr__(self):
        return f"<Schedule Classroom ID {self.classroom_id} - Free Times {self.free_times}>"


def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    with app.app_context():
        db.create_all()


