from controllers import app, db
from models.models import User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def create_database():
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        print("Creating admin user...")
        # Create admin user
        admin = User(
            username="admin@parking.com",
            email="admin@parking.com",
            name="Admin User",
            phone="1234567890",
            is_admin=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        
        print("Creating sample users...")
        # Create sample users
        users = [
            User(username="user1@test.com", email="user1@test.com", name="John Doe", phone="1111111111", is_admin=False),
            User(username="user2@test.com", email="user2@test.com", name="Jane Smith", phone="2222222222", is_admin=False),
            User(username="user3@test.com", email="user3@test.com", name="Bob Johnson", phone="3333333333", is_admin=False)
        ]
        
        for user in users:
            user.set_password("password123")
            db.session.add(user)
        
        print("Creating parking lots...")
        # Create sample parking lots
        parking_lots = [
            ParkingLot(
                prime_location_name="Downtown Mall Parking",
                address="123 Main Street, Downtown",
                pin_code="123456",
                price_per_hour=5.00,
                maximum_number_of_spots=20,
                is_active=True
            ),
            ParkingLot(
                prime_location_name="Airport Parking Zone",
                address="456 Airport Road, Terminal 1",
                pin_code="654321",
                price_per_hour=8.00,
                maximum_number_of_spots=50,
                is_active=True
            ),
            ParkingLot(
                prime_location_name="Shopping Center Parking",
                address="789 Shopping Ave, Mall District",
                pin_code="789012",
                price_per_hour=3.50,
                maximum_number_of_spots=30,
                is_active=True
            ),
            ParkingLot(
                prime_location_name="Office Complex Parking",
                address="321 Business Blvd, Corporate Area",
                pin_code="456789",
                price_per_hour=6.00,
                maximum_number_of_spots=25,
                is_active=True
            )
        ]
        
        for lot in parking_lots:
            db.session.add(lot)
        
        db.session.commit()
        
        print("Creating parking spots...")
        # Create parking spots for each lot
        for lot in parking_lots:
            for i in range(1, lot.maximum_number_of_spots + 1):
                spot = ParkingSpot(
                    parking_lot_id=lot.id,
                    spot_number=f"{chr(65 + (i-1)//10)}{i%10 if i%10 != 0 else 10}",
                    is_available=True,
                    is_active=True
                )
                db.session.add(spot)
        
        db.session.commit()
        
        print("Creating sample reservations...")
        # Create sample reservations
        now = datetime.utcnow()
        
        # Get some users and spots for reservations
        user1 = User.query.filter_by(username="user1@test.com").first()
        user2 = User.query.filter_by(username="user2@test.com").first()
        
        lot1 = ParkingLot.query.filter_by(prime_location_name="Downtown Mall Parking").first()
        lot2 = ParkingLot.query.filter_by(prime_location_name="Airport Parking Zone").first()
        
        spot1 = ParkingSpot.query.filter_by(parking_lot_id=lot1.id, spot_number="A1").first()
        spot2 = ParkingSpot.query.filter_by(parking_lot_id=lot1.id, spot_number="A2").first()
        spot3 = ParkingSpot.query.filter_by(parking_lot_id=lot2.id, spot_number="A1").first()
        
        reservations = [
            Reservation(
                user_id=user1.id,
                parking_lot_id=lot1.id,
                parking_spot_id=spot1.id,
                parking_timestamp=now - timedelta(hours=2),
                end_timestamp=now - timedelta(hours=1),
                cost=5.00,
                vehicle_number="ABC123",
                status='completed'
            ),
            Reservation(
                user_id=user2.id,
                parking_lot_id=lot1.id,
                parking_spot_id=spot2.id,
                parking_timestamp=now - timedelta(hours=1),
                vehicle_number="XYZ789",
                status='active'
            ),
            Reservation(
                user_id=user1.id,
                parking_lot_id=lot2.id,
                parking_spot_id=spot3.id,
                parking_timestamp=now - timedelta(days=1),
                end_timestamp=now - timedelta(days=1, hours=-2),
                cost=16.00,
                vehicle_number="DEF456",
                status='completed'
            )
        ]
        
        for reservation in reservations:
            db.session.add(reservation)
        
        # Mark some spots as unavailable
        if spot2:
            spot2.is_available = False
        
        db.session.commit()
        
        print("Database created successfully!")
        print(f"Created {User.query.count()} users")
        print(f"Created {ParkingLot.query.count()} parking lots")
        print(f"Created {ParkingSpot.query.count()} parking spots")
        print(f"Created {Reservation.query.count()} reservations")
        
        print("\nAdmin credentials:")
        print("Email: admin@parking.com")
        print("Password: admin123")
        
        print("\nSample user credentials:")
        print("Email: user1@test.com")
        print("Password: password123")

if __name__ == "__main__":
    create_database() 