import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask app
app = Flask(__name__)

# Configure the database URI for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the User model (table)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    # You can add more fields here, such as phone, address, etc.

    def __repr__(self):
        return f'<User {self.username}>'

# Define the ParkingSpot model (table)
class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.String(50), unique=True, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<ParkingSpot {self.spot_number}>'

# Define the Booking model (table)
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    booking_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    release_time = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref='bookings', lazy=True)
    parking_spot = db.relationship('ParkingSpot', backref='bookings', lazy=True)

    def __repr__(self):
        return f'<Booking {self.id}>'

# Initialize the database (creates the database and tables)
@app.before_request
def before_request():
    if not os.path.exists("database.db"):
        db.create_all()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


