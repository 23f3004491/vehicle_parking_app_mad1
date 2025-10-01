from controllers import app, db, login_manager
from flask import render_template, redirect, flash, url_for, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime

# Import models after db is initialized
from models.models import User, ParkingLot, ParkingSpot, Reservation

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/test")
def test():
    """Test route to check if routing works"""
    return "Test route working! Routes are functional."

@app.cli.command("db-create")
def create_db():
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username="admin@parking.com").first()
        if not admin:
            admin = User(username="admin@parking.com", name="Admin", email="admin@parking.com", is_admin=True)
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
        print("Database created")

@app.route("/")
def index():
    """Home page - redirect to user dashboard if logged in, otherwise to login"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('email')  # Using email field from form
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash("Login successful", 'success')
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        flash("Invalid credentials", 'danger')
    
    return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        address = request.form.get('address', '').strip()
        pincode = request.form.get('pincode', '').strip()
        
        # Debug: Print form data
        print(f"Form data: name='{name}', email='{email}', address='{address}', pincode='{pincode}'")
        
        # Validation
        if not name:
            flash('Name is required', 'danger')
            return render_template("register.html")
        
        if not email:
            flash('Email is required', 'danger')
            return render_template("register.html")
        
        if not password:
            flash('Password is required', 'danger')
            return render_template("register.html")
        
        if User.query.filter_by(username=email).first():
            flash('Email already exists', 'danger')
            return render_template("register.html")
        
        # Create user with default name if empty
        if not name:
            name = email.split('@')[0]  # Use email prefix as name
        
        user = User(username=email, name=name, email=email, phone="", is_admin=False)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    """Logout endpoint"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route("/user-dashboard")
@login_required
def user_dashboard():
    """User dashboard page"""
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Get user's reservations with related data
    reservations = Reservation.query.filter_by(user_id=current_user.id)\
        .join(ParkingLot, Reservation.parking_lot_id == ParkingLot.id)\
        .join(ParkingSpot, Reservation.parking_spot_id == ParkingSpot.id)\
        .order_by(Reservation.created_at.desc()).limit(10).all()
    
    # Get active parking lots
    parking_lots = ParkingLot.query.filter_by(is_active=True).all()
    
    # Calculate statistics for each parking lot
    parking_lots_with_stats = []
    for lot in parking_lots:
        available_count = ParkingSpot.query.filter_by(
            parking_lot_id=lot.id, 
            is_available=True
        ).count()
        occupied_count = ParkingSpot.query.filter_by(
            parking_lot_id=lot.id, 
            is_available=False
        ).count()
        
        parking_lots_with_stats.append({
            'lot': lot,
            'available_spots_count': available_count,
            'occupied_spots_count': occupied_count
        })
    
    return render_template("user_dashboard.html", 
                         reservations=reservations,
                         parking_lots_with_stats=parking_lots_with_stats)

@app.route("/admin-dashboard")
@login_required
def admin_dashboard():
    """Admin dashboard page"""
    if not current_user.is_admin:
        flash("Access denied", 'danger')
        return redirect(url_for('user_dashboard'))
    
    # Get admin statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_parking_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    total_reservations = Reservation.query.count()
    
    # Get all parking lots
    parking_lots = ParkingLot.query.all()
    
    # Get all users
    users = User.query.filter_by(is_admin=False).all()
    
    # Get recent reservations
    recent_reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(10).all()
    
    # Get parking lots with stats
    parking_lots_with_stats = []
    for lot in parking_lots:
        available_count = ParkingSpot.query.filter_by(
            parking_lot_id=lot.id, 
            is_available=True
        ).count()
        occupied_count = ParkingSpot.query.filter_by(
            parking_lot_id=lot.id, 
            is_available=False
        ).count()
        
        parking_lots_with_stats.append({
            'lot': lot,
            'available_spots_count': available_count,
            'occupied_spots_count': occupied_count
        })
    
    return render_template("admin_dashboard.html",
                         parking_lots=parking_lots,
                         users=users,
                         recent_reservations=recent_reservations,
                         parking_lots_with_stats=parking_lots_with_stats,
                         total_users=total_users,
                         total_parking_lots=total_parking_lots,
                         total_spots=total_spots,
                         total_reservations=total_reservations)

@app.route("/user-search")
@login_required
def user_search():
    """User search page"""
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    search = request.args.get('search', '')
    parking_lots = ParkingLot.query.filter_by(is_active=True).all()
    
    if search:
        parking_lots = ParkingLot.query.filter(
            ParkingLot.prime_location_name.ilike(f'%{search}%') |
            ParkingLot.address.ilike(f'%{search}%')
        ).all()
    
    return render_template("user_dashboard.html", parking_lots=parking_lots)

@app.route("/user-history")
@login_required
def user_history():
    """User history page"""
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.created_at.desc()).all()
    return render_template("user_dashboard.html", reservations=reservations)

@app.route("/user-stats")
@login_required
def user_stats():
    """User statistics page"""
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    return render_template("user_stats.html")

@app.route("/admin-stats")
@login_required
def admin_stats():
    """Admin statistics page"""
    if not current_user.is_admin:
        flash("Access denied", 'danger')
        return redirect(url_for('user_dashboard'))
    
    # Get admin statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_parking_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    total_reservations = Reservation.query.count()
    
    # Get recent reservations
    recent_reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(10).all()
    
    # Get parking lots with stats
    parking_lots = ParkingLot.query.all()
    parking_lots_with_stats = []
    for lot in parking_lots:
        available_count = ParkingSpot.query.filter_by(
            parking_lot_id=lot.id, 
            is_available=True
        ).count()
        occupied_count = ParkingSpot.query.filter_by(
            parking_lot_id=lot.id, 
            is_available=False
        ).count()
        
        parking_lots_with_stats.append({
            'lot': lot,
            'available_spots_count': available_count,
            'occupied_spots_count': occupied_count
        })
    
    return render_template("admin_dashboard.html",
                         recent_reservations=recent_reservations,
                         parking_lots_with_stats=parking_lots_with_stats,
                         total_users=total_users,
                         total_parking_lots=total_parking_lots,
                         total_spots=total_spots,
                         total_reservations=total_reservations)

@app.route("/admin-users")
@login_required
def admin_users():
    """Admin users management page"""
    if not current_user.is_admin:
        flash("Access denied", 'danger')
        return redirect(url_for('user_dashboard'))
    
    # Get admin statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_parking_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    total_reservations = Reservation.query.count()
    
    users = User.query.filter_by(is_admin=False).all()
    
    return render_template("admin_dashboard.html", 
                         users=users,
                         total_users=total_users,
                         total_parking_lots=total_parking_lots,
                         total_spots=total_spots,
                         total_reservations=total_reservations)

@app.route("/admin-search")
@login_required
def admin_search():
    """Admin search page"""
    if not current_user.is_admin:
        flash("Access denied", 'danger')
        return redirect(url_for('user_dashboard'))
    
    search = request.args.get('search', '')
    parking_lots = ParkingLot.query.all()
    
    if search:
        parking_lots = ParkingLot.query.filter(
            ParkingLot.prime_location_name.ilike(f'%{search}%') |
            ParkingLot.address.ilike(f'%{search}%')
        ).all()
    
    # Get admin statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_parking_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    total_reservations = Reservation.query.count()
    
    return render_template("admin_dashboard.html", 
                         parking_lots=parking_lots,
                         search_query=search,
                         total_users=total_users,
                         total_parking_lots=total_parking_lots,
                         total_spots=total_spots,
                         total_reservations=total_reservations)

@app.route("/admin-parking-lots")
@login_required
def admin_parking_lots():
    """Admin parking lots management page"""
    if not current_user.is_admin:
        flash("Access denied", 'danger')
        return redirect(url_for('user_dashboard'))
    
    parking_lots = ParkingLot.query.all()
    return render_template("admin_dashboard.html", parking_lots=parking_lots)

@app.route("/admin-reservations")
@login_required
def admin_reservations():
    """Admin reservations management page"""
    if not current_user.is_admin:
        flash("Access denied", 'danger')
        return redirect(url_for('user_dashboard'))
    
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    return render_template("admin_dashboard.html", reservations=reservations)

@app.route("/admin/add-parking-lot", methods=['POST'])
@login_required
def admin_add_parking_lot():
    """Add parking lot functionality"""
    if not current_user.is_admin:
        flash("Access denied", 'danger')
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        prime_location_name = request.form.get('prime_location_name')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        price_per_hour = request.form.get('price_per_hour', type=float)
        maximum_number_of_spots = request.form.get('maximum_number_of_spots', type=int)
        
        if not all([prime_location_name, address, pin_code, price_per_hour, maximum_number_of_spots]):
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        parking_lot = ParkingLot(
            prime_location_name=prime_location_name,
            address=address,
            pin_code=pin_code,
            price_per_hour=price_per_hour,
            maximum_number_of_spots=maximum_number_of_spots,
            is_active=True
        )
        
        db.session.add(parking_lot)
        db.session.commit()
        
        # Create parking spots for this lot
        for i in range(1, maximum_number_of_spots + 1):
            spot = ParkingSpot(
                parking_lot_id=parking_lot.id,
                spot_number=f"{chr(65 + (i-1)//10)}{i%10 if i%10 != 0 else 10}",
                is_available=True,
                is_active=True
            )
            db.session.add(spot)
        
        db.session.commit()
        flash('Parking lot added successfully!', 'success')
    
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/edit-parking-lot/<int:lot_id>", methods=['POST'])
@login_required
def admin_edit_parking_lot(lot_id):
    """Edit parking lot functionality"""
    if not current_user.is_admin:
        flash("Access denied", 'danger')
        return redirect(url_for('user_dashboard'))
    
    parking_lot = ParkingLot.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        parking_lot.prime_location_name = request.form.get('prime_location_name')
        parking_lot.address = request.form.get('address')
        parking_lot.pin_code = request.form.get('pin_code')
        parking_lot.price_per_hour = request.form.get('price_per_hour', type=float)
        parking_lot.maximum_number_of_spots = request.form.get('maximum_number_of_spots', type=int)
        
        db.session.commit()
        flash('Parking lot updated successfully!', 'success')
    
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/delete-parking-lot/<int:lot_id>", methods=['POST'])
@login_required
def admin_delete_parking_lot(lot_id):
    """Delete parking lot functionality"""
    if not current_user.is_admin:
        flash("Access denied", 'danger')
        return redirect(url_for('user_dashboard'))
    
    parking_lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check if there are any reservations for this lot
    all_reservations = Reservation.query.filter_by(parking_lot_id=lot_id).count()
    
    if all_reservations > 0:
        flash(f'Warning: This parking lot has {all_reservations} reservations that will also be deleted.', 'warning')
    
    # Delete the parking lot (reservations and spots will be deleted due to cascade)
    db.session.delete(parking_lot)
    db.session.commit()
    
    flash('Parking lot deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/delete-user/<int:user_id>", methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """Delete user functionality"""
    if not current_user.is_admin:
        flash("Access denied", 'danger')
        return redirect(url_for('user_dashboard'))
    
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot delete admin user', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    
    return redirect(url_for('admin_users'))

@app.route("/admin/manage-parking-spots/<int:lot_id>")
@login_required
def admin_manage_parking_spots(lot_id):
    """Manage parking spots for a specific lot"""
    if not current_user.is_admin:
        flash("Access denied", 'danger')
        return redirect(url_for('user_dashboard'))
    
    parking_lot = ParkingLot.query.get_or_404(lot_id)
    parking_spots = ParkingSpot.query.filter_by(parking_lot_id=lot_id).all()
    
    return render_template("admin_dashboard.html", 
                         parking_lot=parking_lot,
                         parking_spots=parking_spots)

@app.route("/admin/toggle-spot-status/<int:spot_id>", methods=['POST'])
@login_required
def admin_toggle_spot_status(spot_id):
    """Toggle parking spot availability"""
    if not current_user.is_admin:
        flash("Access denied", 'danger')
        return redirect(url_for('user_dashboard'))
    
    spot = ParkingSpot.query.get_or_404(spot_id)
    spot.is_available = not spot.is_available
    db.session.commit()
    
    flash(f'Spot {spot.spot_number} {"activated" if spot.is_available else "deactivated"} successfully!', 'success')
    return redirect(url_for('admin_manage_parking_spots', lot_id=spot.parking_lot_id))

@app.route("/book-parking-spot", methods=['GET', 'POST'])
@login_required
def book_parking_spot():
    """Book parking spot page"""
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        parking_lot_id = request.form.get('parking_lot_id', type=int)
        parking_spot_id = request.form.get('parking_spot_id', type=int)
        parking_timestamp = request.form.get('parking_timestamp')
        vehicle_number = request.form.get('vehicle_number')
        
        if not all([parking_lot_id, parking_spot_id, parking_timestamp, vehicle_number]):
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('user_dashboard'))
        
        # Check if spot is available
        spot = ParkingSpot.query.get_or_404(parking_spot_id)
        if not spot.is_available:
            flash('This parking spot is not available', 'danger')
            return redirect(url_for('user_dashboard'))
        
        # Check if user already has an active reservation
        active_reservation = Reservation.query.filter_by(
            user_id=current_user.id, 
            status='active'
        ).first()
        
        if active_reservation:
            flash('You already have an active parking reservation', 'danger')
            return redirect(url_for('user_dashboard'))
        
        try:
            # Parse datetime
            parking_time = datetime.fromisoformat(parking_timestamp.replace('Z', '+00:00'))
            
            # Mark spot as unavailable first
            spot.is_available = False
            
            reservation = Reservation(
                user_id=current_user.id,
                parking_lot_id=parking_lot_id,
                parking_spot_id=parking_spot_id,
                parking_timestamp=parking_time,
                status='active',
                vehicle_number=vehicle_number
            )
            
            db.session.add(reservation)
            db.session.commit()
            
            flash('Parking spot booked successfully!', 'success')
            return redirect(url_for('user_dashboard'))
            
        except Exception as e:
            # If there's an error, make the spot available again
            if spot:
                spot.is_available = True
                db.session.commit()
            flash(f'Error booking parking spot: {str(e)}', 'danger')
            return redirect(url_for('user_dashboard'))
    
    parking_lots = ParkingLot.query.filter_by(is_active=True).all()
    return render_template("book_parking_spot.html", parking_lots=parking_lots)

@app.route("/release-parking-spot", methods=['GET', 'POST'])
@login_required
def release_parking_spot():
    """Release parking spot page"""
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        reservation_id = request.form.get('reservation_id', type=int)
        if reservation_id:
            reservation = Reservation.query.get_or_404(reservation_id)
            if reservation.user_id == current_user.id and reservation.status == 'active':
                reservation.status = 'completed'
                reservation.end_timestamp = datetime.utcnow()
                
                # Calculate cost based on duration
                if reservation.parking_timestamp and reservation.end_timestamp:
                    duration = (reservation.end_timestamp - reservation.parking_timestamp).total_seconds() / 3600
                    reservation.cost = duration * reservation.parking_lot.price_per_hour
                
                # Make the parking spot available again
                spot = ParkingSpot.query.get(reservation.parking_spot_id)
                if spot:
                    spot.is_available = True
                
                db.session.commit()
                flash('Parking spot released successfully!', 'success')
            else:
                flash('Invalid reservation or already completed', 'danger')
        else:
            flash('Reservation ID is required', 'danger')
    
    return redirect(url_for('user_dashboard'))

@app.route("/view-parking-spot")
@login_required
def view_parking_spot():
    """View parking spot details"""
    spot_id = request.args.get('spot_id', type=int)
    if spot_id:
        spot = ParkingSpot.query.get_or_404(spot_id)
        return render_template("view_parking_spot.html", spot=spot)
    
    return redirect(url_for('user_dashboard'))

@app.route("/occupied-spot-details")
@login_required
def occupied_spot_details():
    """View occupied spot details"""
    reservation_id = request.args.get('reservation_id', type=int)
    if reservation_id:
        reservation = Reservation.query.get_or_404(reservation_id)
        return render_template("occupied_spot_details.html", reservation=reservation)
    
    return redirect(url_for('user_dashboard'))

@app.route("/admin-login", methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, is_admin=True).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash("Admin login successful", 'success')
            return redirect(url_for('admin_dashboard'))
        flash("Invalid admin credentials", 'danger')
    
    return render_template("admin_login.html")

@app.route("/parking-lots")
def parking_lots_list():
    """Parking lots listing page"""
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    query = ParkingLot.query
    if search:
        query = query.filter(ParkingLot.prime_location_name.ilike(f'%{search}%'))
    if status:
        query = query.filter_by(is_active=(status == 'active'))
    
    parking_lots = query.all()
    return render_template("user_dashboard.html", parking_lots=parking_lots)

@app.route("/parking-lots/<int:lot_id>")
def parking_lot_detail(lot_id):
    """Parking lot detail page"""
    parking_lot = ParkingLot.query.get_or_404(lot_id)
    parking_spots = ParkingSpot.query.filter_by(parking_lot_id=lot_id).all()
    recent_reservations = Reservation.query.filter_by(parking_lot_id=lot_id).limit(5).all()
    
    return render_template("user_dashboard.html",
                         parking_lot=parking_lot,
                         parking_spots=parking_spots,
                         recent_reservations=recent_reservations)

@app.route("/reservations")
@login_required
def reservations_list():
    """Reservations listing page"""
    query = Reservation.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)
    
    reservations = query.order_by(Reservation.created_at.desc()).all()
    parking_lots = ParkingLot.query.all()
    
    return render_template("user_dashboard.html",
                         reservations=reservations,
                         parking_lots=parking_lots)

@app.route("/reservations/<int:reservation_id>")
@login_required
def reservation_detail(reservation_id):
    """Reservation detail page"""
    reservation = Reservation.query.get_or_404(reservation_id)
    if not current_user.is_admin and reservation.user_id != current_user.id:
        flash("Access denied", 'danger')
        return redirect(url_for('reservations_list'))
    
    return render_template("occupied_spot_details.html", reservation=reservation)

@app.route("/make-reservation", methods=['GET', 'POST'])
@login_required
def make_reservation():
    """Make reservation page"""
    if request.method == 'POST':
        parking_lot_id = request.form.get('parking_lot_id', type=int)
        parking_spot_id = request.form.get('parking_spot_id', type=int)
        parking_timestamp = request.form.get('parking_timestamp')
        estimated_duration = request.form.get('estimated_duration', type=float)
        
        if not all([parking_lot_id, parking_spot_id, parking_timestamp, estimated_duration]):
            flash('Please fill in all required fields', 'danger')
            return render_template("book_parking_spot.html")
        
        reservation = Reservation(
            user_id=current_user.id,
            parking_lot_id=parking_lot_id,
            parking_spot_id=parking_spot_id,
            parking_timestamp=datetime.fromisoformat(parking_timestamp.replace('Z', '+00:00')),
            estimated_duration=estimated_duration,
            status='pending'
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        flash('Reservation created successfully!', 'success')
        return redirect(url_for('reservation_detail', reservation_id=reservation.id))
    
    parking_lots = ParkingLot.query.filter_by(is_active=True).all()
    return render_template("book_parking_spot.html", parking_lots=parking_lots)

@app.route("/my-reservations")
@login_required
def my_reservations():
    """User's reservations page"""
    return redirect(url_for('reservations_list'))

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        
        current_user.email = email
        current_user.name = name
        current_user.phone = phone
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template("user_dashboard.html")

@app.route("/change-password", methods=['POST'])
@login_required
def change_password():
    """Change password endpoint"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'danger')
        return redirect(url_for('profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    flash('Password changed successfully!', 'success')
    return redirect(url_for('profile'))

@app.route("/api/parking-lots/<int:lot_id>/spots")
def api_parking_spots(lot_id):
    """API endpoint for parking spots"""
    spots = ParkingSpot.query.filter_by(parking_lot_id=lot_id).all()
    return jsonify([{
        'id': spot.id,
        'spot_number': spot.spot_number,
        'is_available': spot.is_available
    } for spot in spots])

@app.route("/api/parking-lots")
def api_parking_lots():
    """API endpoint for parking lots"""
    lots = ParkingLot.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': lot.id,
        'name': lot.prime_location_name,
        'address': lot.address,
        'price_per_hour': lot.price_per_hour
    } for lot in lots])

@app.context_processor
def inject_now():
    """Inject current year into templates"""
    return {'current_year': datetime.now().year}
