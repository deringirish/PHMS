# Quick Start Guide for PHMS

## Step-by-Step Setup (Windows)

### 1. Open Command Prompt in Project Directory
```cmd
cd "c:\Users\giris\OneDrive\Desktop\IDT Project Platform"
```

### 2. Create and Activate Virtual Environment
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```cmd
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```cmd
copy .env.example .env
```

Then edit `.env` file and add your Gemini API key:
```
GEMINI_API_KEY=your-actual-api-key-here
```

### 5. Start MongoDB
Open another command prompt and run:
```cmd
mongod
```

Or if MongoDB is installed as a service, it should already be running.

### 6. Create First Admin
```cmd
python init_admin.py
```

Enter the following when prompted:
- User ID: `admin`
- Full Name: `System Administrator`
- Password: `admin123` (or your choice, min 6 chars)
- Secret Password: `secret123` (remember this for creating more admins)

### 7. Run the Application
```cmd
python app.py
```

### 8. Access PHMS
Open your browser and go to: **http://localhost:5000**

Login with the credentials you created in step 6.

## Testing Checklist

### ✅ Authentication
- [ ] Visit http://localhost:5000 - should show landing page
- [ ] Click "Login to PHMS"
- [ ] Login with admin credentials
- [ ] Should redirect to Patient Dashboard
- [ ] Click Logout - should return to landing page

### ✅ Admin Management
- [ ] Go to "Admins" menu
- [ ] Create a new admin (requires secret password)
- [ ] Verify new admin appears in list
- [ ] Logout and login with new admin

### ✅ Patient Management
- [ ] Click "Add New Patient"
- [ ] Fill in patient details
- [ ] Select medical conditions (e.g., Diabetes, Hypertension)
- [ ] Submit - should redirect to patient detail page
- [ ] Search for patient from dashboard
- [ ] Update patient information

### ✅ Manual Health Records
- [ ] Go to patient detail page
- [ ] Click "Add Health Record"
- [ ] Fill in various metrics (e.g., BP, Sugar, Lipids)
- [ ] Click "Save Health Record"
- [ ] Verify record appears in table
- [ ] Add multiple records with different dates

### ✅ AI Report Upload (if Gemini API configured)
- [ ] Get a sample lab report (PDF or image)
- [ ] Click "Upload Lab Report"
- [ ] Upload the file
- [ ] Review extracted data
- [ ] Edit if needed and confirm
- [ ] Verify record is saved with "REPORT_AI" badge

### ✅ Data Visualization
- [ ] After adding multiple records, verify charts appear
- [ ] Check different chart types (Sugar, BP, Lipids, etc.)
- [ ] Verify data points match records
- [ ] Check chart responsiveness

### ✅ Error Handling
- [ ] Try accessing protected routes without login
- [ ] Try invalid login credentials
- [ ] Submit forms with missing required fields
- [ ] Upload invalid file types

## Common Issues

**"Module not found" error:**
```cmd
pip install -r requirements.txt
```

**MongoDB connection error:**
- Ensure MongoDB is running
- Check if mongod service is active

**Port 5000 already in use:**
- Change port in app.py: `app.run(debug=True, port=5001)`

**Gemini API error:**
- Verify API key in .env is correct
- Test without AI upload first

## Next Steps

1. ✅ Complete all testing checklist items
2. 📝 Document any issues found
3. 🎨 Customize styling if needed
4. 🔐 Change default secret for production
5. 📊 Add sample patient data
6. 🚀 Deploy to production environment

---

**Need Help?** Check README.md for detailed documentation.
