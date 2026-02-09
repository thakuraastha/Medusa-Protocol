from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, UserProfile
from utils.validation import validate_username, validate_password, validate_email
from utils.logging_config import log_audit
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        if not username or not password:
            flash('Please provide both username and password', 'error')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()

            logger.info(f'User {username} logged in successfully')
            log_audit(None, user.id, 'login', success=True)

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            # Redirect based on role
            if user.role == 'doctor':
                return redirect(url_for('main.doctor_dashboard'))
            else:
                return redirect(url_for('main.patient_dashboard'))
        else:
            flash('Invalid username or password', 'error')
            logger.warning(f'Failed login attempt for username: {username}')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'patient')
        full_name = request.form.get('full_name', '').strip()

        # Validate inputs
        is_valid_username, username_error = validate_username(username)
        if not is_valid_username:
            flash(username_error, 'error')
            return render_template('auth/register.html')

        if not validate_email(email):
            flash('Invalid email address', 'error')
            return render_template('auth/register.html')

        is_valid_password, password_error = validate_password(password)
        if not is_valid_password:
            flash(password_error, 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')

        if role not in ['patient', 'doctor']:
            flash('Invalid role selected', 'error')
            return render_template('auth/register.html')

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html')

        try:
            # Create new user
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # Get user ID

            # Create profile
            profile = UserProfile(user_id=user.id, full_name=full_name)
            db.session.add(profile)
            db.session.commit()

            logger.info(f'New user registered: {username} ({role})')
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            logger.error(f'Registration error: {str(e)}')
            flash('Registration failed. Please try again.', 'error')

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    username = current_user.username
    user_id = current_user.id
    logout_user()
    logger.info(f'User {username} logged out')
    log_audit(None, user_id, 'logout', success=True)
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        hospital = request.form.get('hospital', '').strip()

        if not current_user.profile:
            profile = UserProfile(user_id=current_user.id)
            db.session.add(profile)
        else:
            profile = current_user.profile

        profile.full_name = full_name
        profile.phone = phone
        profile.hospital = hospital

        db.session.commit()
        logger.info(f'Profile updated for user {current_user.username}')
        flash('Profile updated successfully', 'success')

    except Exception as e:
        db.session.rollback()
        logger.error(f'Profile update error: {str(e)}')
        flash('Failed to update profile', 'error')

    return redirect(url_for('auth.profile'))
