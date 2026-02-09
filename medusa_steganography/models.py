from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')  # patient, doctor, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    operations = db.relationship('SteganographyOperation', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class UserProfile(db.Model):
    """Extended user profile information"""
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(120))
    patient_id = db.Column(db.String(50), unique=True, index=True)
    doctor_id = db.Column(db.String(50), unique=True, index=True)
    hospital = db.Column(db.String(120))
    department = db.Column(db.String(120))
    specialty = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    blood_type = db.Column(db.String(5))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserProfile {self.full_name}>'


class SteganographyOperation(db.Model):
    """Track steganography operations for audit trail"""
    __tablename__ = 'operations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    operation_type = db.Column(db.String(20), nullable=False)  # embed, extract, compare
    method = db.Column(db.String(20), nullable=False)  # lsb, dct, dwt
    original_filename = db.Column(db.String(255))
    stego_filename = db.Column(db.String(255))
    data_length = db.Column(db.Integer)
    psnr = db.Column(db.Float)
    ssim = db.Column(db.Float)
    bit_accuracy = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45))
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)

    def __repr__(self):
        return f'<Operation {self.operation_type} by User {self.user_id}>'


class MedicalRecord(db.Model):
    """Medical records linked to steganography operations"""
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), nullable=False, index=True)
    doctor_id = db.Column(db.String(50), nullable=False, index=True)
    record_type = db.Column(db.String(50))  # MRI, CT, X-Ray, etc.
    diagnosis = db.Column(db.Text)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    stego_image_path = db.Column(db.String(255))
    metadata = db.Column(db.JSON)  # Store DICOM metadata or other info
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, encrypted, completed

    def __repr__(self):
        return f'<MedicalRecord {self.record_type} for Patient {self.patient_id}>'


class AuditLog(db.Model):
    """Comprehensive audit log for compliance"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    success = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<AuditLog {self.action} by User {self.user_id}>'
