import logging
import os
from logging.handlers import RotatingFileHandler
from flask import request, has_request_context
from datetime import datetime


class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request information"""

    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
        else:
            record.url = None
            record.remote_addr = None
            record.method = None

        return super().format(record)


def setup_logging(app):
    """
    Setup application logging

    Args:
        app: Flask application instance
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(app.config.get('LOG_FILE', 'logs/medusa.log'))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set log level
    log_level_str = app.config.get('LOG_LEVEL', 'INFO')
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    app.logger.setLevel(log_level)

    # Remove default handlers
    app.logger.handlers.clear()

    # File handler with rotation
    file_handler = RotatingFileHandler(
        app.config.get('LOG_FILE', 'logs/medusa.log'),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10
    )
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Format for file logs
    file_formatter = RequestFormatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s '
        '[%(remote_addr)s - %(method)s %(url)s]'
    )
    file_handler.setFormatter(file_formatter)

    # Format for console logs
    console_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # Add handlers
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    # Also log werkzeug (Flask's server) to the same file
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(log_level)
    werkzeug_logger.addHandler(file_handler)

    app.logger.info('Medusa Protocol application started')


def log_audit(app, user_id, action, resource_type=None, resource_id=None,
               details=None, success=True):
    """
    Log audit trail to database

    Args:
        app: Flask application instance
        user_id: ID of user performing action
        action: Action being performed
        resource_type: Type of resource being accessed
        resource_id: ID of resource
        details: Additional details (dict)
        success: Whether action was successful
    """
    from models import AuditLog, db

    try:
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr if has_request_context() else None,
            user_agent=request.user_agent.string if has_request_context() else None,
            success=success
        )
        db.session.add(audit_entry)
        db.session.commit()

        app.logger.info(
            f'Audit: User {user_id} performed {action} on {resource_type} '
            f'{resource_id} - Success: {success}'
        )
    except Exception as e:
        app.logger.error(f'Failed to log audit entry: {str(e)}')
        db.session.rollback()
