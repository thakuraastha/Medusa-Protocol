# Medusa Protocol - Secure Medical Image Steganography System

A professional, secure web application for embedding and extracting sensitive medical information within medical images using advanced steganography techniques.

## Features

- **🔐 Secure Authentication**: User registration and login with role-based access control (Patient/Doctor)
- **🖼️ Multiple Steganography Methods**: LSB, DCT, and DWT algorithms
- **📊 Real-time Metrics**: PSNR, SSIM, and Bit Accuracy measurements
- **🛡️ Enterprise Security**: CORS protection, CSRF tokens, rate limiting, input validation
- **📝 Audit Trail**: Comprehensive logging and database tracking of all operations
- **🎨 Beautiful UI**: Modern, responsive design with medical theme
- **📈 Interactive Charts**: Visualize comparison results with Chart.js
- **👥 Role-Based Dashboards**: Separate interfaces for patients and doctors

## Steganography Methods

1. **LSB (Least Significant Bit)**: Embeds data in the least significant bits of pixel values
2. **DCT (Discrete Cosine Transform)**: Embeds data in DCT coefficients for better robustness
3. **DWT (Discrete Wavelet Transform)**: Embeds data in wavelet coefficients for optimal quality

## Security Features

- ✅ User authentication and authorization
- ✅ Password hashing with Werkzeug security
- ✅ CSRF protection on all forms
- ✅ Rate limiting to prevent abuse
- ✅ Input validation and sanitization
- ✅ File type verification using magic numbers
- ✅ Restricted CORS origins
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ Audit logging for compliance
- ✅ Secure session management

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- libmagic (for file type detection)

### Setup Instructions

1. **Clone or navigate to the project directory**:
   ```bash
   cd "/Users/aasthathakur/Documents/classnotes/MedusaProtocol/medusa_steganography"
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install libmagic** (for file type detection):
   - **macOS**: `brew install libmagic`
   - **Ubuntu/Debian**: `sudo apt-get install libmagic1`
   - **Windows**: `pip install python-magic-bin`

5. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your configuration:
   ```
   FLASK_ENV=development
   SECRET_KEY=your-random-secret-key-here
   PORT=5000
   ```

6. **Initialize the database**:
   ```bash
   python app.py
   ```
   The database will be automatically created on first run.

## Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your web browser and navigate to**:
   ```
   http://localhost:5000
   ```

3. **Create an account**:
   - Click "Register" and create either a Patient or Doctor account
   - Use a strong password (min 8 chars with uppercase, lowercase, number, special char)

4. **Login and explore**:
   - Access the steganography tools
   - View role-specific dashboards
   - Track your operation history

## Usage

### Embedding Data

1. Navigate to the "Embed Data" tab
2. Upload a medical image (PNG, JPG, TIFF)
3. Select a steganography method (LSB, DCT, or DWT)
4. Enter secret medical data in JSON format
5. Click "Embed Data"
6. View metrics (PSNR, SSIM, Bit Accuracy)
7. Download the steganographic image

### Extracting Data

1. Navigate to the "Extract Data" tab
2. Upload a steganographic image
3. Select the method used for embedding
4. Enter the data length (shown during embedding)
5. Click "Extract Data"
6. View the extracted secret data

### Comparing Methods

1. Navigate to the "Compare Methods" tab
2. Upload a medical image
3. Enter secret medical data
4. Click "Compare Methods"
5. View interactive charts comparing all three methods

## Project Structure

```
medusa_steganography/
├── app.py                      # Main application entry point
├── config.py                   # Configuration management
├── models.py                   # Database models
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
│
├── routes/                    # Application routes
│   ├── __init__.py
│   ├── main.py                # Main page routes
│   ├── auth.py                # Authentication routes
│   └── api.py                 # API endpoints
│
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── steganography.py       # Steganography algorithms
│   ├── validation.py          # Input validation
│   └── logging_config.py      # Logging setup
│
├── templates/                 # HTML templates
│   ├── index.html             # Main steganography interface
│   ├── patient_dashboard.html # Patient dashboard
│   ├── doctor_dashboard.html  # Doctor dashboard
│   ├── error.html             # Error page
│   └── auth/
│       ├── login.html         # Login page
│       └── register.html      # Registration page
│
├── static/                    # Static files
│   ├── style.css              # Consolidated CSS
│   ├── script.js              # Main JavaScript
│   └── dashboard.js           # Dashboard interactions
│
├── logs/                      # Application logs
└── uploads/                   # Uploaded files (created automatically)
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `GET /auth/profile` - View user profile
- `POST /auth/profile/update` - Update user profile

### Steganography Operations
- `POST /api/embed` - Embed data in image
- `POST /api/extract` - Extract data from image
- `POST /api/compare` - Compare all methods
- `GET /api/operations/history` - View operation history

### Pages
- `GET /` - Main steganography interface (public)
- `GET /patient` - Patient dashboard (requires login)
- `GET /doctor` - Doctor dashboard (requires login)

## Metrics Explained

- **PSNR (Peak Signal-to-Noise Ratio)**: Measures image quality. Higher values (typically 40-60 dB) indicate better quality and less visible changes.

- **SSIM (Structural Similarity Index)**: Measures structural similarity between original and stego image. Values closer to 1.0 indicate higher similarity.

- **Bit Accuracy**: Percentage of correctly recovered bits after embedding and extraction. 100% indicates perfect data recovery.

## Configuration

### Environment Variables

Create a `.env` file from `.env.example` and configure:

- `FLASK_ENV`: Environment (development/production)
- `FLASK_DEBUG`: Debug mode (True/False)
- `SECRET_KEY`: Secret key for sessions (generate a random string)
- `PORT`: Server port (default: 5000)
- `MAX_FILE_SIZE_MB`: Maximum file upload size
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)
- `DATABASE_URI`: Database connection string
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

### Security Settings

For production deployment:

1. Set `FLASK_ENV=production`
2. Set `FLASK_DEBUG=False`
3. Generate a strong `SECRET_KEY`
4. Configure `CORS_ORIGINS` to your domain only
5. Set up HTTPS/SSL certificates
6. Use a production database (PostgreSQL recommended)
7. Configure a reverse proxy (nginx/Apache)

## Technologies Used

### Backend
- **Flask 3.0**: Web framework
- **SQLAlchemy**: ORM for database
- **Flask-Login**: User session management
- **Flask-WTF**: CSRF protection
- **Flask-Limiter**: Rate limiting
- **OpenCV**: Image processing
- **scikit-image**: Image quality metrics
- **PyWavelets**: Wavelet transforms

### Frontend
- **HTML5 & CSS3**: Modern, responsive UI
- **JavaScript (ES6+)**: Interactive functionality
- **Chart.js**: Data visualization
- **Font Awesome**: Icons

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Any modern browser with ES6+ support

## Notes

- **Supported Image Formats**: JPG, PNG, TIFF
- **Image Requirements**: Minimum 100x100 pixels, Maximum 4096x4096 pixels
- **Data Format**: Secret data must be valid JSON
- **File Size Limit**: 10 MB by default (configurable)
- **Capacity**: Larger images can accommodate more data
- **DWT Compatibility**: Images are automatically adjusted to even dimensions

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'magic'"**
   - Solution: Install python-magic: `pip install python-magic`
   - On Windows: `pip install python-magic-bin`

2. **"File too large" error**
   - Solution: Increase `MAX_FILE_SIZE_MB` in `.env`

3. **"Invalid file type" error**
   - Solution: Ensure image is PNG, JPG, or TIFF format

4. **"Image capacity exceeded" error**
   - Solution: Use a larger image or reduce secret data size

5. **Database errors**
   - Solution: Delete `medusa.db` and restart to recreate

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

### Running Tests

```bash
python -m pytest tests/
```

## License

This project is developed for the Medusa Protocol research on secure medical data transmission and steganography techniques.

## Contributing

For bug reports or feature requests, please contact the development team.

## Security Notice

This application handles sensitive medical data. Always:
- Use HTTPS in production
- Implement proper access controls
- Follow HIPAA/GDPR compliance guidelines
- Regularly update dependencies
- Monitor audit logs
- Backup database regularly

## Support

For issues, questions, or support:
- Check the troubleshooting section
- Review the application logs in `logs/medusa.log`
- Contact the system administrator

---

**Version**: 2.0.0
**Last Updated**: February 2026
**Status**: Production Ready ✅
