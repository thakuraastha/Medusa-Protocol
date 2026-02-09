from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import base64
import io
import os
import logging

from models import db, SteganographyOperation
from utils.steganography import (
    embed_lsb, extract_lsb, embed_dct, extract_dct, embed_dwt, extract_dwt,
    string_to_binary, binary_to_string, calculate_bit_accuracy,
    calculate_metrics, check_capacity
)
from utils.validation import (
    allowed_file, validate_file_type, validate_json_data,
    validate_method, validate_data_length, sanitize_filename,
    validate_image_dimensions
)
from utils.logging_config import log_audit

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


def save_operation(user_id, operation_type, method, original_filename=None,
                   stego_filename=None, data_length=None, psnr=None,
                   ssim=None, bit_accuracy=None, success=True, error_message=None):
    """Save steganography operation to database"""
    try:
        operation = SteganographyOperation(
            user_id=user_id,
            operation_type=operation_type,
            method=method,
            original_filename=original_filename,
            stego_filename=stego_filename,
            data_length=data_length,
            psnr=psnr,
            ssim=ssim,
            bit_accuracy=bit_accuracy,
            ip_address=request.remote_addr,
            success=success,
            error_message=error_message
        )
        db.session.add(operation)
        db.session.commit()
        return operation.id
    except Exception as e:
        logger.error(f'Failed to save operation: {str(e)}')
        db.session.rollback()
        return None


@api_bp.route('/embed', methods=['POST'])
@login_required
def embed():
    """Embed secret data into an image"""
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        if not image_file or image_file.filename == '':
            return jsonify({'error': 'No image selected'}), 400

        if not allowed_file(image_file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        # Validate file type
        is_valid_type, mime_type = validate_file_type(image_file.stream)
        if not is_valid_type:
            return jsonify({'error': f'Invalid file type: {mime_type}'}), 400

        secret_data = request.form.get('secret_data', '').strip()
        method = request.form.get('method', '').strip().lower()

        # Validate secret data
        is_valid_json, json_result = validate_json_data(secret_data)
        if not is_valid_json:
            return jsonify({'error': json_result}), 400

        # Validate method
        if not validate_method(method):
            return jsonify({'error': f'Invalid method: {method}'}), 400

        # Read and decode image
        img_bytes = image_file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        original_image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if original_image is None:
            return jsonify({'error': 'Failed to decode image'}), 400

        # Validate image dimensions
        is_valid_dims, dim_error = validate_image_dimensions(original_image)
        if not is_valid_dims:
            return jsonify({'error': dim_error}), 400

        # Ensure even dimensions for DWT
        h, w = original_image.shape
        if method == 'dwt' and (h % 2 != 0 or w % 2 != 0):
            original_image = original_image[:h//2 * 2, :w//2 * 2]
            logger.info(f'Cropped image to even dimensions for DWT: {original_image.shape}')

        # Convert secret data to binary
        binary_data = string_to_binary(secret_data)
        data_length = len(binary_data)

        # Check capacity
        has_capacity, max_capacity = check_capacity(original_image, data_length, method)
        if not has_capacity:
            return jsonify({
                'error': f'Image too small for data. Max capacity: {max_capacity} bits, Required: {data_length} bits'
            }), 400

        # Perform embedding
        stego_result = None
        extracted_binary = None

        if method == 'lsb':
            stego_result = embed_lsb(original_image.copy(), binary_data)
            if stego_result is None:
                return jsonify({'error': 'Embedding failed: Image capacity exceeded'}), 400
            stego_image_8bit = np.uint8(stego_result)
            extracted_binary = extract_lsb(stego_image_8bit, data_length)

        elif method == 'dct':
            stego_dct_coeffs = embed_dct(original_image.copy(), binary_data)
            if stego_dct_coeffs is None:
                return jsonify({'error': 'Embedding failed: Image capacity exceeded'}), 400
            stego_image_8bit = np.uint8(np.clip(cv2.idct(stego_dct_coeffs), 0, 255))
            extracted_binary = extract_dct(stego_dct_coeffs, data_length)

        elif method == 'dwt':
            stego_dwt_float = embed_dwt(original_image.copy(), binary_data)
            if stego_dwt_float is None:
                return jsonify({'error': 'Embedding failed'}), 400
            stego_image_8bit = np.uint8(np.clip(stego_dwt_float, 0, 255))
            extracted_binary = extract_dwt(stego_dwt_float, data_length)

        # Calculate metrics
        metrics = calculate_metrics(original_image, stego_image_8bit)
        bit_accuracy = calculate_bit_accuracy(binary_data, extracted_binary)

        # Encode stego image to base64
        _, buffer = cv2.imencode('.png', stego_image_8bit)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        # Save operation to database
        operation_id = save_operation(
            user_id=current_user.id,
            operation_type='embed',
            method=method,
            original_filename=sanitize_filename(image_file.filename),
            data_length=data_length,
            psnr=metrics['psnr'],
            ssim=metrics['ssim'],
            bit_accuracy=bit_accuracy,
            success=True
        )

        logger.info(f'User {current_user.username} embedded data using {method}')
        log_audit(current_app._get_current_object(), current_user.id, 'embed_data',
                  'steganography', operation_id, {'method': method}, True)

        return jsonify({
            'success': True,
            'stego_image': img_base64,
            'psnr': metrics['psnr'],
            'ssim': metrics['ssim'],
            'bit_accuracy': bit_accuracy,
            'data_length': data_length,
            'operation_id': operation_id
        })

    except Exception as e:
        logger.error(f'Embed error: {str(e)}', exc_info=True)
        save_operation(
            user_id=current_user.id,
            operation_type='embed',
            method=request.form.get('method', 'unknown'),
            success=False,
            error_message=str(e)
        )
        return jsonify({'error': 'An error occurred during embedding'}), 500


@api_bp.route('/extract', methods=['POST'])
@login_required
def extract():
    """Extract hidden data from a steganographic image"""
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        if not image_file or image_file.filename == '':
            return jsonify({'error': 'No image selected'}), 400

        if not allowed_file(image_file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        method = request.form.get('method', '').strip().lower()
        data_length_str = request.form.get('data_length', '').strip()

        # Validate method
        if not validate_method(method):
            return jsonify({'error': f'Invalid method: {method}'}), 400

        # Validate data length
        is_valid_length, length_result = validate_data_length(data_length_str)
        if not is_valid_length:
            return jsonify({'error': length_result}), 400
        data_length = length_result

        # Read and decode image
        img_bytes = image_file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        stego_image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if stego_image is None:
            return jsonify({'error': 'Failed to decode image'}), 400

        # Extract based on method
        extracted_binary = None

        if method == 'lsb':
            extracted_binary = extract_lsb(stego_image, data_length)
        elif method == 'dct':
            float_img = np.float32(stego_image)
            dct_coeffs = cv2.dct(float_img)
            extracted_binary = extract_dct(dct_coeffs, data_length)
        elif method == 'dwt':
            extracted_binary = extract_dwt(stego_image.astype(np.float64), data_length)

        # Convert binary to text
        extracted_text = binary_to_string(extracted_binary)

        # Save operation
        operation_id = save_operation(
            user_id=current_user.id,
            operation_type='extract',
            method=method,
            original_filename=sanitize_filename(image_file.filename),
            data_length=data_length,
            success=True
        )

        logger.info(f'User {current_user.username} extracted data using {method}')
        log_audit(current_app._get_current_object(), current_user.id, 'extract_data',
                  'steganography', operation_id, {'method': method}, True)

        return jsonify({
            'success': True,
            'extracted_data': extracted_text,
            'operation_id': operation_id
        })

    except Exception as e:
        logger.error(f'Extract error: {str(e)}', exc_info=True)
        save_operation(
            user_id=current_user.id,
            operation_type='extract',
            method=request.form.get('method', 'unknown'),
            success=False,
            error_message=str(e)
        )
        return jsonify({'error': 'An error occurred during extraction'}), 500


@api_bp.route('/compare', methods=['POST'])
@login_required
def compare():
    """Compare all steganography methods"""
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        if not image_file or image_file.filename == '':
            return jsonify({'error': 'No image selected'}), 400

        if not allowed_file(image_file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        secret_data = request.form.get('secret_data', '').strip()

        # Validate secret data
        is_valid_json, json_result = validate_json_data(secret_data)
        if not is_valid_json:
            return jsonify({'error': json_result}), 400

        # Read and decode image
        img_bytes = image_file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        original_image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if original_image is None:
            return jsonify({'error': 'Failed to decode image'}), 400

        # Validate dimensions
        is_valid_dims, dim_error = validate_image_dimensions(original_image)
        if not is_valid_dims:
            return jsonify({'error': dim_error}), 400

        # Ensure even dimensions
        h, w = original_image.shape
        if h % 2 != 0 or w % 2 != 0:
            original_image = original_image[:h//2 * 2, :w//2 * 2]

        binary_data = string_to_binary(secret_data)
        data_length = len(binary_data)

        results = []

        # LSB
        try:
            stego_lsb = embed_lsb(original_image.copy(), binary_data)
            if stego_lsb is not None:
                stego_lsb_8bit = np.uint8(stego_lsb)
                extracted_lsb = extract_lsb(stego_lsb_8bit, data_length)
                metrics_lsb = calculate_metrics(original_image, stego_lsb_8bit)
                results.append({
                    'method': 'LSB',
                    'psnr': metrics_lsb['psnr'],
                    'ssim': metrics_lsb['ssim'],
                    'bit_accuracy': calculate_bit_accuracy(binary_data, extracted_lsb)
                })
        except Exception as e:
            logger.warning(f'LSB comparison failed: {str(e)}')

        # DCT
        try:
            stego_dct_coeffs = embed_dct(original_image.copy(), binary_data)
            if stego_dct_coeffs is not None:
                stego_dct_8bit = np.uint8(np.clip(cv2.idct(stego_dct_coeffs), 0, 255))
                extracted_dct = extract_dct(stego_dct_coeffs, data_length)
                metrics_dct = calculate_metrics(original_image, stego_dct_8bit)
                results.append({
                    'method': 'DCT',
                    'psnr': metrics_dct['psnr'],
                    'ssim': metrics_dct['ssim'],
                    'bit_accuracy': calculate_bit_accuracy(binary_data, extracted_dct)
                })
        except Exception as e:
            logger.warning(f'DCT comparison failed: {str(e)}')

        # DWT
        try:
            stego_dwt_float = embed_dwt(original_image.copy(), binary_data)
            if stego_dwt_float is not None:
                stego_dwt_8bit = np.uint8(np.clip(stego_dwt_float, 0, 255))
                extracted_dwt = extract_dwt(stego_dwt_float, data_length)
                metrics_dwt = calculate_metrics(original_image, stego_dwt_8bit)
                results.append({
                    'method': 'DWT',
                    'psnr': metrics_dwt['psnr'],
                    'ssim': metrics_dwt['ssim'],
                    'bit_accuracy': calculate_bit_accuracy(binary_data, extracted_dwt)
                })
        except Exception as e:
            logger.warning(f'DWT comparison failed: {str(e)}')

        if not results:
            return jsonify({'error': 'All methods failed'}), 500

        # Save operation
        operation_id = save_operation(
            user_id=current_user.id,
            operation_type='compare',
            method='all',
            original_filename=sanitize_filename(image_file.filename),
            data_length=data_length,
            success=True
        )

        logger.info(f'User {current_user.username} compared methods')
        log_audit(current_app._get_current_object(), current_user.id, 'compare_methods',
                  'steganography', operation_id, None, True)

        return jsonify({
            'success': True,
            'results': results,
            'operation_id': operation_id
        })

    except Exception as e:
        logger.error(f'Compare error: {str(e)}', exc_info=True)
        return jsonify({'error': 'An error occurred during comparison'}), 500


@api_bp.route('/operations/history', methods=['GET'])
@login_required
def operation_history():
    """Get user's operation history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        operations = SteganographyOperation.query.filter_by(
            user_id=current_user.id
        ).order_by(
            SteganographyOperation.created_at.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'success': True,
            'operations': [{
                'id': op.id,
                'type': op.operation_type,
                'method': op.method,
                'filename': op.original_filename,
                'created_at': op.created_at.isoformat(),
                'psnr': op.psnr,
                'ssim': op.ssim,
                'bit_accuracy': op.bit_accuracy,
                'success': op.success
            } for op in operations.items],
            'total': operations.total,
            'pages': operations.pages,
            'current_page': operations.page
        })

    except Exception as e:
        logger.error(f'History error: {str(e)}')
        return jsonify({'error': 'Failed to retrieve history'}), 500
