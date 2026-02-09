from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Main steganography interface"""
    return render_template('index.html')


@main_bp.route('/patient')
@login_required
def patient_dashboard():
    """Patient dashboard - requires login"""
    if current_user.role != 'patient':
        return render_template('error.html', message='Access denied: Patient access only'), 403
    return render_template('patient_dashboard.html')


@main_bp.route('/doctor')
@login_required
def doctor_dashboard():
    """Doctor dashboard - requires login"""
    if current_user.role != 'doctor':
        return render_template('error.html', message='Access denied: Doctor access only'), 403
    return render_template('doctor_dashboard.html')
