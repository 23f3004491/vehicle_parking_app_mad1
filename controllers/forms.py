from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateField, IntegerField, SelectField, SubmitField, RadioField, BooleanField, FloatField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from wtforms.widgets import HiddenInput
from datetime import datetime

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    accept_terms = BooleanField('I accept the terms and conditions', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ParkingLotForm(FlaskForm):
    prime_location_name = StringField('Location Name', validators=[DataRequired(), Length(max=200)])
    address = StringField('Address', validators=[DataRequired(), Length(max=500)])
    pin_code = StringField('PIN Code', validators=[DataRequired(), Length(max=10)])
    price_per_hour = FloatField('Price per Hour', validators=[DataRequired(), NumberRange(min=0)])
    maximum_number_of_spots = IntegerField('Maximum Spots', validators=[DataRequired(), NumberRange(min=1)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Parking Lot')

class ParkingSpotForm(FlaskForm):
    spot_number = StringField('Spot Number', validators=[DataRequired(), Length(max=20)])
    parking_lot_id = SelectField('Parking Lot', coerce=int, validators=[DataRequired()])
    is_available = BooleanField('Available', default=True)
    submit = SubmitField('Save Parking Spot')

class ReservationForm(FlaskForm):
    parking_lot_id = SelectField('Parking Lot', coerce=int, validators=[DataRequired()])
    parking_spot_id = SelectField('Parking Spot', coerce=int, validators=[DataRequired()])
    parking_timestamp = DateTimeField('Parking Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    estimated_duration = FloatField('Estimated Duration (hours)', validators=[DataRequired(), NumberRange(min=0.5, max=24)])
    submit = SubmitField('Make Reservation')

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=15)])
    submit = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class AdminUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=15)])
    is_admin = BooleanField('Admin User')
    submit = SubmitField('Save User')

class AdminSearchForm(FlaskForm):
    search_query = StringField('Search', validators=[DataRequired()])
    search_type = SelectField('Search Type', choices=[
        ('user', 'Users'),
        ('parking_lot', 'Parking Lots'),
        ('parking_spot', 'Parking Spots'),
        ('reservation', 'Reservations')
    ])
    submit = SubmitField('Search')

class UserSearchForm(FlaskForm):
    search_query = StringField('Search', validators=[DataRequired()])
    search_type = SelectField('Search Type', choices=[
        ('parking_lot', 'Parking Lots'),
        ('reservation', 'My Reservations')
    ])
    submit = SubmitField('Search')

class ReservationFilterForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('', 'All'),
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
    parking_lot_id = SelectField('Parking Lot', coerce=int)
    date_from = DateField('From Date', format='%Y-%m-%d', validators=[Optional()])
    date_to = DateField('To Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Filter')

class ParkingLotFilterForm(FlaskForm):
    search = StringField('Search Location', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('', 'All'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ])
    price_min = FloatField('Min Price', validators=[Optional(), NumberRange(min=0)])
    price_max = FloatField('Max Price', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Filter')

class AdminDashboardForm(FlaskForm):
    date_from = DateField('From Date', format='%Y-%m-%d', validators=[Optional()])
    date_to = DateField('To Date', format='%Y-%m-%d', validators=[Optional()])
    parking_lot_id = SelectField('Parking Lot', coerce=int)
    submit = SubmitField('Generate Report')

class ReservationDetailForm(FlaskForm):
    reservation_id = IntegerField(widget=HiddenInput())
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    cost = FloatField('Cost', validators=[Optional(), NumberRange(min=0)])
    end_timestamp = DateTimeField('End Time', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    submit = SubmitField('Update Reservation')
