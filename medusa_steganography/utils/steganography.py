import cv2
import numpy as np
import pywt
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr

# Constants
BITS_PER_BYTE = 8
LSB_MASK = 254  # 11111110 in binary
LSB_BIT = 1


def calculate_bit_accuracy(original_binary, extracted_binary):
    """
    Calculate the accuracy of bit extraction

    Args:
        original_binary: Original binary string
        extracted_binary: Extracted binary string

    Returns:
        float: Accuracy percentage
    """
    if len(original_binary) != len(extracted_binary):
        return 0.0
    correct_bits = sum(1 for i in range(len(original_binary))
                      if original_binary[i] == extracted_binary[i])
    return (correct_bits / len(original_binary)) * 100.0


def string_to_binary(text):
    """Convert string to binary representation"""
    return ''.join([format(ord(c), '08b') for c in text])


def binary_to_string(binary_data):
    """Convert binary string back to text"""
    text = ""
    for i in range(0, len(binary_data), BITS_PER_BYTE):
        byte = binary_data[i:i+BITS_PER_BYTE]
        if len(byte) == BITS_PER_BYTE:
            text += chr(int(byte, 2))
    return text


def check_capacity(image, data_length, method='lsb'):
    """
    Check if image has enough capacity for the data

    Args:
        image: Input image (numpy array)
        data_length: Length of binary data to embed
        method: Steganography method

    Returns:
        tuple: (bool, int) - (has_capacity, max_capacity)
    """
    if method == 'lsb':
        max_capacity = image.size
    elif method == 'dct':
        max_capacity = image.size
    elif method == 'dwt':
        # DWT capacity depends on coefficient dimensions
        coeffs = pywt.dwt2(image, 'haar')
        _, (_, _, cD) = coeffs
        max_capacity = cD.size
    else:
        max_capacity = 0

    return data_length <= max_capacity, max_capacity


def embed_lsb(image, binary_data):
    """
    Embed data using LSB (Least Significant Bit) method

    Args:
        image: Input image (numpy array, grayscale)
        binary_data: Binary string to embed

    Returns:
        numpy array: Stego image or None if capacity exceeded
    """
    pixels = image.flatten()
    data_length = len(binary_data)

    if data_length > len(pixels):
        return None

    stego_pixels = pixels.copy()
    for i in range(data_length):
        # Clear LSB and set new bit
        stego_pixels[i] = (stego_pixels[i] & LSB_MASK) | int(binary_data[i])

    return stego_pixels.reshape(image.shape)


def extract_lsb(image, data_length):
    """
    Extract data using LSB method

    Args:
        image: Stego image (numpy array)
        data_length: Number of bits to extract

    Returns:
        str: Extracted binary string
    """
    pixels = image.flatten()
    binary_data = "".join([str(pixels[i] & LSB_BIT) for i in range(data_length)])
    return binary_data


def embed_dct(image, binary_data):
    """
    Embed data using DCT (Discrete Cosine Transform) method

    Args:
        image: Input image (numpy array, grayscale)
        binary_data: Binary string to embed

    Returns:
        numpy array: DCT coefficients with embedded data
    """
    float_img = np.float32(image)
    dct_img = cv2.dct(float_img)
    pixels = dct_img.flatten()
    data_length = len(binary_data)

    if data_length > len(pixels):
        return None

    stego_pixels = pixels.copy()
    for i in range(data_length):
        val = stego_pixels[i]
        data_bit = int(binary_data[i])
        current_lsb = int(val) % 2

        if current_lsb != data_bit:
            stego_pixels[i] = val + (1 if data_bit == 1 else -1)

    return stego_pixels.reshape(dct_img.shape)


def extract_dct(stego_dct_coeffs, data_length):
    """
    Extract data from DCT coefficients

    Args:
        stego_dct_coeffs: DCT coefficients with embedded data
        data_length: Number of bits to extract

    Returns:
        str: Extracted binary string
    """
    binary_data = ""
    pixels = stego_dct_coeffs.flatten()
    for i in range(data_length):
        binary_data += str(int(pixels[i]) % 2)
    return binary_data


def embed_dwt(image, binary_data):
    """
    Embed data using DWT (Discrete Wavelet Transform) method

    Args:
        image: Input image (numpy array, grayscale)
        binary_data: Binary string to embed

    Returns:
        numpy array: Reconstructed image with embedded data
    """
    # Ensure image has even dimensions
    h, w = image.shape
    if h % 2 != 0:
        image = image[:h-1, :]
    if w % 2 != 0:
        image = image[:, :w-1]

    coeffs = pywt.dwt2(image.astype(np.float64), 'haar')
    cA, (cH, cV, cD) = coeffs

    binary_index = 0
    data_length = len(binary_data)
    stego_cD = cD.copy()
    rows, cols = stego_cD.shape

    for i in range(rows):
        for j in range(cols):
            if binary_index < data_length:
                val = stego_cD[i, j]
                data_bit = int(binary_data[binary_index])
                current_lsb = int(val) % 2

                if current_lsb != data_bit:
                    stego_cD[i, j] = val + (1 if data_bit == 1 else -1)
                binary_index += 1
            else:
                break
        if binary_index >= data_length:
            break

    # Reconstruct using float64 for precision
    reconstructed = pywt.idwt2((cA, (cH, cV, stego_cD)), 'haar')
    return reconstructed


def extract_dwt(stego_image, data_length):
    """
    Extract data from DWT coefficients

    Args:
        stego_image: Stego image (numpy array) or DWT coefficients
        data_length: Number of bits to extract

    Returns:
        str: Extracted binary string
    """
    # Convert to float64 for wavelet transform
    if stego_image.dtype != np.float64:
        stego_image = stego_image.astype(np.float64)

    coeffs = pywt.dwt2(stego_image, 'haar')
    _, (_, _, cD) = coeffs

    binary_data = ""
    binary_index = 0
    rows, cols = cD.shape

    for i in range(rows):
        for j in range(cols):
            if binary_index < data_length:
                lsb = int(cD[i, j]) % 2
                binary_data += str(lsb)
                binary_index += 1
            else:
                break
        if binary_index >= data_length:
            break

    return binary_data


def calculate_metrics(original_image, stego_image):
    """
    Calculate quality metrics for steganography

    Args:
        original_image: Original image
        stego_image: Stego image

    Returns:
        dict: Dictionary with PSNR and SSIM values
    """
    # Ensure both images are same type
    original_image = np.uint8(np.clip(original_image, 0, 255))
    stego_image = np.uint8(np.clip(stego_image, 0, 255))

    psnr_val = psnr(original_image, stego_image)
    ssim_val = ssim(original_image, stego_image)

    return {
        'psnr': float(psnr_val),
        'ssim': float(ssim_val)
    }
