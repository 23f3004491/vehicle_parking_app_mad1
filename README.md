# Vehicle Parking App - MAD1 Project

A comprehensive web-based vehicle parking management system built with Flask.  This application enables users to find and book parking spots while providing administrators with tools to manage parking lots, spots, and view analytics.

## Features

### User Features
- 🔐 User registration and authentication
- 🚗 Browse available parking lots and spots
- 📍 View parking lot locations with address and pricing information
- 🎫 Book parking spots with vehicle details
- ⏱️ Real-time availability tracking
- 💰 Automatic cost calculation based on parking duration
- 📊 View personal parking history and statistics
- 🔓 Release parking spots and complete reservations

### Admin Features
- 👨‍💼 Separate admin authentication system
- 🏢 Create and manage parking lots
- 🅿️ Add and configure parking spots for each lot
- 📈 View comprehensive statistics and analytics
- 🔍 Monitor all reservations and user activities
- 💵 Track revenue and usage patterns
- ⚙️ Activate/deactivate parking lots and spots

## Technology Stack

- **Backend Framework**: Flask 2.3.3
- **Database**: SQLAlchemy (Flask-SQLAlchemy 3.0.5)
- **Authentication**: Flask-Login 0.6.3
- **Forms**: Flask-WTF 1.1.1, WTForms 3.0.1
- **Security**:  Werkzeug 2.3.7 (password hashing)
- **Template Engine**: Jinja2 3.1.2

## Project Structure

```
vehicle_parking_app_mad1/
├── app.py                      # Application entry point
├── create_db.py                # Database initialization script
├── requirements.txt            # Python dependencies
├── controllers/
│   ├── __init__.py            # Flask app and database initialization
│   ├── routes.py              # Application routes and views
│   └── forms.py               # WTForms form definitions
├── models/
│   └── models.py              # Database models (User, ParkingLot, ParkingSpot, Reservation)
└── templates/
    ├── base.html              # Base template
    ├── login.html             # User login page
    ├── register.html          # User registration page
    ├── admin_login.html       # Admin login page
    ├── user_dashboard.html    # User dashboard
    ├── admin_dashboard.html   # Admin dashboard
    ├── book_parking_spot.html # Parking spot booking form
    ├── release_parking_spot.html # Spot release form
    ├── view_parking_spot.html # Spot details view
    ├── occupied_spot_details.html # Occupied spot information
    ├── user_stats.html        # User statistics page
    └── admin_stats. html       # Admin analytics page
```

## Database Models

### User
- Username, email, password (hashed)
- Name, phone number
- Admin flag
- Relationships with reservations

### ParkingLot
- Location name and address
- PIN code, price per hour
- Maximum number of spots
- Active/inactive status
- Relationships with parking spots and reservations

### ParkingSpot
- Spot number (e.g., A1, B2)
- Availability status
- Active/inactive status
- Belongs to a parking lot

### Reservation
- User, parking lot, and parking spot references
- Parking and end timestamps
- Cost calculation
- Vehicle number
- Status (pending, active, completed, cancelled)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/23f3004491/vehicle_parking_app_mad1.git
   cd vehicle_parking_app_mad1
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python create_db.py
   ```
   This will create sample data including:
   - 1 admin user
   - 3 regular users
   - 4 parking lots with multiple spots each
   - Sample reservations

5. **Run the application**
   ```bash
   python app.py
   ```
   The application will be available at `http://localhost:5000`

## Default Credentials

### Admin Access
- **Email**: admin@parking.com
- **Password**: admin123

### Sample User Access
- **Email**: user1@test.com
- **Password**: password123

(Additional users:  user2@test.com, user3@test.com with the same password)

## Usage

### For Users
1. Register a new account or login with existing credentials
2. Browse available parking lots on the dashboard
3. Select a parking lot to view available spots
4. Book a spot by providing vehicle number
5. View your active reservations and parking history
6. Release parking spot when done to calculate final cost
7. Check your statistics and past reservations

### For Admins
1. Login with admin credentials at `/admin/login`
2. Create new parking lots with location and pricing details
3. Add parking spots to each lot
4. Monitor all reservations and user activities
5. View statistics including revenue, occupancy rates, and trends
6. Manage parking lot activation status

## Key Features Implementation

- **Real-time Availability**: Spots are marked unavailable when booked and released when parking ends
- **Automatic Cost Calculation**: Based on hourly rates and actual parking duration
- **Cascade Delete**: Proper database relationships ensure data integrity
- **Password Security**: Werkzeug password hashing for secure authentication
- **Role-based Access**:  Separate dashboards and permissions for users and admins
- **Responsive Forms**: WTForms validation for data integrity

## Future Enhancements

- Payment gateway integration
- Email notifications for booking confirmations
- Mobile app support
- Advanced search and filtering options
- Parking spot reservation in advance
- QR code-based entry/exit system
- Multi-language support

## Contributing

Feel free to fork this repository and submit pull requests for any improvements. 

## License

This project is created for educational purposes as part of MAD1 (Modern Application Development 1) coursework. 

## Contact

For any queries, please reach out through GitHub issues. 
