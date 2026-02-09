import os
import json
import re
from werkzeug.utils import secure_filename
from flask import current_app
import magic


def allowed_file(filename):
    """
    Check if file extension is allowed

    Args:
        filename: Name of the file

    Returns:
        bool: True if extension is allowed
    """
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def validate_file_type(file_stream):
    """
    Validate file type using magic numbers (MIME type detection)

    Args:
        file_stream: File stream to validate

    Returns:
        tuple: (bool, str) - (is_valid, mime_type)
    """
    try:
        # Read first 2048 bytes for MIME detection
        header = file_stream.read(2048)
        file_stream.seek(0)  # Reset stream position

        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(header)

        # Allow image MIME types
        allowed_mimes = [
            'image/png',
            'image/jpeg',
            'image/jpg',
            'image/tiff',
            'image/x-tiff'
        ]

        return mime_type in allowed_mimes, mime_type
    except Exception:
        return False, 'unknown'


def validate_json_data(data_string):
    """
    Validate JSON secret data

    Args:
        data_string: JSON string to validate

    Returns:
        tuple: (bool, dict/str) - (is_valid, parsed_data or error_message)
    """
    try:
        data = json.loads(data_string)

        # Check if it's a dict
        if not isinstance(data, dict):
            return False, "Secret data must be a JSON object"

        # Check for required fields in medical context
        # This is flexible - can be customized based on requirements
        if len(data) == 0:
            return False, "Secret data cannot be empty"

        # Check data length
        if len(data_string) > current_app.config.get('MAX_SECRET_DATA_LENGTH', 10000):
            return False, f"Secret data too large (max {current_app.config.get('MAX_SECRET_DATA_LENGTH')} characters)"

        return True, data
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_method(method):
    """
    Validate steganography method

    Args:
        method: Method name

    Returns:
        bool: True if method is valid
    """
    supported_methods = current_app.config.get('SUPPORTED_METHODS', ['lsb', 'dct', 'dwt'])
    return method in supported_methods


def validate_data_length(data_length):
    """
    Validate data length parameter

    Args:
        data_length: Data length value

    Returns:
        tuple: (bool, int/str) - (is_valid, value or error_message)
    """
    try:
        length = int(data_length)
        if length <= 0:
            return False, "Data length must be positive"
        if length > 1000000:  # 1 million bits max
            return False, "Data length too large"
        return True, length
    except (ValueError, TypeError):
        return False, "Invalid data length format"


def sanitize_filename(filename):
    """
    Sanitize and secure filename

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    # Use werkzeug's secure_filename
    filename = secure_filename(filename)

    # Remove any remaining special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)

    # Limit length
    max_length = 100
    name, ext = os.path.splitext(filename)
    if len(name) > max_length:
        name = name[:max_length]
    filename = name + ext

    return filename


def validate_image_dimensions(image):
    """
    Validate image dimensions

    Args:
        image: Numpy array of image

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if len(image.shape) not in [2, 3]:
        return False, "Invalid image dimensions"

    height, width = image.shape[:2]

    # Minimum dimensions
    if height < 100 or width < 100:
        return False, "Image too small (minimum 100x100 pixels)"

    # Maximum dimensions
    if height > 4096 or width > 4096:
        return False, "Image too large (maximum 4096x4096 pixels)"

    return True, ""


def validate_file_size(file_stream):
    """
    Validate file size

    Args:
        file_stream: File stream

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    max_size = current_app.config.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024)

    file_stream.seek(0, os.SEEK_END)
    size = file_stream.tell()
    file_stream.seek(0)

    if size > max_size:
        return False, f"File too large (max {max_size / (1024*1024):.1f} MB)"

    if size == 0:
        return False, "File is empty"

    return True, ""


def validate_email(email):
    """
    Validate email format

    Args:
        email: Email string

    Returns:
        bool: True if valid email
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    """
    Validate username format

    Args:
        username: Username string

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty"

    if len(username) < 3:
        return False, "Username must be at least 3 characters"

    if len(username) > 80:
        return False, "Username too long (max 80 characters)"

    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        return False, "Username can only contain letters, numbers, dots, hyphens, and underscores"

    return True, ""


def validate_password(password):
    """
    Validate password strength

    Args:
        password: Password string

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not password:
        return False, "Password cannot be empty"

    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if len(password) > 128:
        return False, "Password too long (max 128 characters)"

    # Check for at least one uppercase, lowercase, digit, and special char
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, ""
