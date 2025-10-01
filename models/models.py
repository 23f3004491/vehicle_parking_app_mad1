from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Import db from controllers
from controllers import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Admin {self.username}>'

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    parking_spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', backref='parking_lot', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ParkingLot {self.prime_location_name}>'
    
    @property
    def available_spots_count(self):
        return ParkingSpot.query.filter_by(parking_lot_id=self.id, is_available=True).count()
    
    @property
    def occupied_spots_count(self):
        return ParkingSpot.query.filter_by(parking_lot_id=self.id, is_available=False).count()

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.String(20), nullable=False)  # e.g., "A1", "B2"
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} - Available: {self.is_available}>'

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False)
    end_timestamp = db.Column(db.DateTime, nullable=True)
    estimated_duration = db.Column(db.Float, nullable=True)  # in hours
    cost = db.Column(db.Float, nullable=True)
    vehicle_number = db.Column(db.String(20), nullable=True)  # Vehicle registration number
    status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending', 'active', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Reservation {self.id} - User: {self.user_id}>'
    
    @property
    def duration_hours(self):
        if self.end_timestamp:
            duration = self.end_timestamp - self.parking_timestamp
            return duration.total_seconds() / 3600
        return self.estimated_duration
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    def calculate_cost(self):
        if self.cost is not None:
            return self.cost
        if self.end_timestamp and self.parking_spot.parking_lot.price_per_hour:
            hours = self.duration_hours
            return hours * self.parking_spot.parking_lot.price_per_hour
        return 0.0