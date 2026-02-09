# Quick Setup Guide - Medusa Protocol

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
cd "/Users/aasthathakur/Documents/classnotes/MedusaProtocol/medusa_steganography"
pip install -r requirements.txt
```

### 2. Install libmagic

**macOS**:
```bash
brew install libmagic
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install libmagic1
```

**Windows**:
```bash
pip install python-magic-bin
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set a secret key:
```
SECRET_KEY=change-this-to-a-random-string
```

### 4. Run the Application

```bash
python app.py
```

### 5. Access the Application

Open your browser and go to:
```
http://localhost:5000
```

## First Time Setup

### Create Your First Account

1. Click "Register" on the login page
2. Fill in the form:
   - **Full Name**: Your name
   - **Username**: Choose a username
   - **Email**: Your email address
   - **Role**: Select "Patient" or "Doctor"
   - **Password**: Must have:
     - At least 8 characters
     - One uppercase letter
     - One lowercase letter
     - One number
     - One special character (!@#$%^&*...)

3. Click "Register"
4. Login with your credentials

## What's Fixed

✅ **All Security Issues Resolved**:
- Authentication and authorization added
- CORS restricted to specific origins
- CSRF protection on all forms
- Rate limiting to prevent abuse
- Input validation and sanitization
- Debug mode disabled by default

✅ **All Functional Bugs Fixed**:
- JavaScript event parameter bug fixed
- Port mismatch corrected (now uses 5000)
- Error handling improved
- Data loss in DWT minimized
- All methods validate capacity before embedding

✅ **Code Quality Improvements**:
- Separated concerns (MVC architecture)
- External CSS (no inline styles)
- Comprehensive logging
- Database models for persistence
- Audit trail system
- Configuration management

✅ **All Files Properly Linked**:
- CSS properly linked in all templates
- JavaScript properly loaded
- Routes organized in blueprints
- Models, utils, and routes separated

## Testing the Application

### Test Embedding

1. Login to your account
2. Go to the main page
3. Upload a test image (JPG, PNG, or TIFF)
4. Select a method (LSB recommended for first test)
5. Enter test data:
   ```json
   {
     "patient_id": "TEST-001",
     "hospital": "Test Hospital",
     "diagnosis": "Test Diagnosis",
     "notes": "This is a test"
   }
   ```
6. Click "Embed Data"
7. Download the steganographic image
8. Note the **data_length** value shown

### Test Extraction

1. Go to "Extract Data" tab
2. Upload the steganographic image you just downloaded
3. Select the same method (LSB)
4. Enter the **data_length** value from embedding
5. Click "Extract Data"
6. Verify the extracted data matches your original data

### Test Comparison

1. Go to "Compare Methods" tab
2. Upload an image
3. Enter test data
4. Click "Compare Methods"
5. View the charts showing PSNR, SSIM, and Bit Accuracy for all methods

## Troubleshooting

### Common Issues

**"No module named 'magic'"**
```bash
pip install python-magic
# On Windows: pip install python-magic-bin
```

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**Port already in use**
```bash
# Change PORT in .env file
PORT=5001
```

**Database errors**
```bash
# Delete the database and restart
rm medusa.db
python app.py
```

**Login issues**
- Make sure you registered an account first
- Check password meets requirements
- Clear browser cookies if needed

## File Structure

```
medusa_steganography/
├── app.py                 # ✅ Fixed - proper security, no debug mode
├── config.py              # ✅ New - configuration management
├── models.py              # ✅ New - database models
├── requirements.txt       # ✅ Updated - all dependencies
├── .env.example           # ✅ New - environment template
│
├── routes/                # ✅ New - organized routes
│   ├── main.py           # Page routes
│   ├── auth.py           # Authentication
│   └── api.py            # API endpoints
│
├── utils/                 # ✅ New - utility functions
│   ├── steganography.py  # Algorithms
│   ├── validation.py     # Input validation
│   └── logging_config.py # Logging setup
│
├── templates/             # ✅ Fixed - inline styles removed
│   ├── index.html
│   ├── patient_dashboard.html
│   ├── doctor_dashboard.html
│   ├── error.html
│   └── auth/
│       ├── login.html    # ✅ New
│       └── register.html # ✅ New
│
└── static/                # ✅ Fixed - consolidated CSS
    ├── style.css         # All styles in one file
    ├── script.js         # Fixed event bug
    └── dashboard.js
```

## Security Features Enabled

- ✅ User authentication (Flask-Login)
- ✅ Password hashing (Werkzeug)
- ✅ CSRF protection (Flask-WTF)
- ✅ Rate limiting (Flask-Limiter)
- ✅ Input validation (custom validators)
- ✅ File type verification (python-magic)
- ✅ SQL injection protection (SQLAlchemy)
- ✅ XSS protection (Jinja2 auto-escaping)
- ✅ Secure sessions
- ✅ Audit logging
- ✅ CORS restrictions

## Next Steps

1. **Customize**: Edit `.env` with your settings
2. **Test**: Try all three steganography methods
3. **Explore**: Check out patient and doctor dashboards
4. **Review**: Check audit logs in `logs/medusa.log`
5. **Deploy**: See README.md for production deployment

## Support

Need help? Check:
1. README.md for detailed documentation
2. logs/medusa.log for error messages
3. This SETUP.md for quick fixes

---

**All issues fixed ✅**
**All files properly linked ✅**
**Production ready ✅**
