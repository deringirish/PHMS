# Patient Health Data Management System (PHMS)

A secure, comprehensive web application for managing patient health records with AI-powered lab report extraction.

## Features

- **Admin-Only Authentication**: Secure login system with bcrypt password hashing
- **Patient Management**: Create, view, update patient profiles with medical history
- **Manual Health Records**: Comprehensive form for entering 40+ health metrics
- **AI Report Upload**: Extract data from lab reports (PDF/images) using Gemini AI
- **Data Visualization**: Interactive charts using Chart.js for health trends
- **Responsive Design**: Modern, premium UI that works on all devices

## Technology Stack

- **Backend**: Python 3.x, Flask
- **Database**: MongoDB (localhost)
- **AI**: Google Gemini API
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Chart.js
- **Security**: bcrypt password hashing, session-based authentication

## Prerequisites

1. **Python 3.8+** installed
2. **MongoDB** installed and running on `localhost:27017`
3. **Gemini API Key** (get from Google AI Studio)

## Installation & Setup

### 1. Clone or Navigate to Project

```bash
cd "c:\Users\giris\OneDrive\Desktop\IDT Project Platform"
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment:
- **Windows**: `venv\Scripts\activate`
- **Mac/Linux**: `source venv/bin/activate`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

### 5. Start MongoDB

Ensure MongoDB is running on `localhost:27017`. If not, start it:

```bash
mongod
```

### 6. Create Initial Admin Account

Run the setup script to create the first admin:

```bash
python init_admin.py
```

Follow the prompts to create your admin account. You'll need:
- User ID (username or email)
- Full Name
- Password (min 6 characters)
- Secret Password (for admin operations)

### 7. Run the Application

```bash
python app.py
```

The application will start on **http://localhost:5000**

## Usage

### First Time Login

1. Navigate to http://localhost:5000
2. Click "Login to PHMS"
3. Enter the credentials you created in step 6
4. You'll be redirected to the Patient Dashboard

### Adding Patients

1. From the dashboard, click "Add New Patient"
2. Fill in patient information
3. Select any known medical conditions
4. Click "Add Patient"

### Adding Health Records

**Manual Entry:**
1. Go to patient details page
2. Click "Add Health Record"
3. Fill in available health metrics
4. Click "Save Health Record"

**AI Upload:**
1. Go to patient details page
2. Click "Upload Lab Report"
3. Select a PDF or image file
4. Review extracted data
5. Edit if needed and confirm

### Creating More Admins

1. Navigate to "Admins" from the top menu
2. Fill in the "Add New Admin" form
3. Enter the secret password (the one you created during initial setup)
4. Click "Create Admin Account"

## Health Metrics Supported

The system tracks 40+ health metrics organized in categories:

- **Vitals**: BP, Heart Rate, Temperature, SpO2, Weight, Height, BMI
- **Diabetes/Glucose**: Fasting, Post-meal, Random, HbA1c
- **Lipid Profile**: Total Cholesterol, HDL, LDL, Triglycerides, VLDL
- **Kidney Function**: Creatinine, Urea, BUN, eGFR
- **Liver Function**: SGPT, SGOT, ALP, Bilirubin (Total, Direct, Indirect)
- **Electrolytes**: Sodium, Potassium, Chloride
- **Hematology (CBC)**: Hemoglobin, WBC, Platelets, RBC, PCV, MCV
- **Thyroid**: TSH, T3, T4
- **Vitamins**: Vitamin D, Vitamin B12

## Project Structure

```
IDT Project Platform/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── init_admin.py          # Admin setup script
├── requirements.txt       # Python dependencies
├── models/                # Database models
│   ├── admin.py
│   ├── patient.py
│   └── health_record.py
├── routes/                # Flask routes
│   ├── auth.py
│   ├── admin_routes.py
│   ├── patient_routes.py
│   └── record_routes.py
├── services/              # Business logic
│   ├── gemini_service.py
│   └── chart_data_service.py
├── utils/                 # Utilities
│   ├── decorators.py
│   └── validators.py
├── templates/             # HTML templates
└── static/                # CSS, JS, images
    └── css/
        └── styles.css
```

## Security Notes

- All passwords are hashed using bcrypt
- Admin-only access - no public registration
- Session-based authentication
- HTTPS recommended for production
- Store API keys in environment variables, never in code

## Troubleshooting

**MongoDB Connection Error:**
- Ensure MongoDB is running: `mongod`
- Check connection string in `.env`

**Gemini API Error:**
- Verify API key in `.env` is correct
- Check internet connection
- Ensure API key has proper permissions

**Import Errors:**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Future Enhancements

- Multi-clinic support
- Email notifications
- PDF report generation
- Advanced analytics
- Mobile app integration
- Role-based access (doctors, nurses, etc.)

## License

Internal use only - Healthcare data management system

## Support

For issues or questions, contact your system administrator.

---

**PHMS** - Patient Health Data Management System © 2025
