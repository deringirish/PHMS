# Deployment Guide: Patient Health Data Management System (PHMS)

This guide provides step-by-step instructions for deploying the PHMS application to Vercel using GitHub.

## 📋 Prerequisites

Before you begin, ensure you have:

1. **GitHub Account** - [Sign up here](https://github.com/signup) if you don't have one
2. **Vercel Account** - [Sign up here](https://vercel.com/signup) (free tier available)
3. **MongoDB Atlas Account** - [Sign up here](https://www.mongodb.com/cloud/atlas/register) (free tier available)
4. **Git installed** on your local machine - [Download here](https://git-scm.com/downloads)

> [!IMPORTANT]
> **File Upload Limitation**: This deployment uses local file storage which is **ephemeral** on Vercel. Uploaded files (patient documents, reports) will not persist between deployments or serverless function invocations. For production use, consider migrating to cloud storage (Vercel Blob, AWS S3, etc.).

---

## 🗄️ Part 1: Set Up MongoDB Atlas

### 1. Create a MongoDB Cluster

1. Log in to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Click **"Build a Database"** or **"Create"**
3. Choose **"M0 Free"** tier
4. Select a cloud provider and region (closest to your users)
5. Name your cluster (e.g., `phms-cluster`)
6. Click **"Create Cluster"** (takes 3-5 minutes)

### 2. Configure Database Access

1. In the left sidebar, click **"Database Access"** under Security
2. Click **"Add New Database User"**
3. Authentication Method: **Password**
4. Username: `phms-admin` (or your choice)
5. Password: Click **"Autogenerate Secure Password"** and **save it securely**
6. Database User Privileges: **"Read and write to any database"**
7. Click **"Add User"**

### 3. Configure Network Access

1. In the left sidebar, click **"Network Access"** under Security
2. Click **"Add IP Address"**
3. Click **"Allow Access From Anywhere"** (0.0.0.0/0)
   - This is required for Vercel's serverless functions
4. Click **"Confirm"**

### 4. Get Connection String

1. Go back to **"Database"** in the left sidebar
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. Driver: **Python**, Version: **3.12 or later**
5. Copy the connection string (looks like):
   ```
   mongodb+srv://phms-admin:<password>@phms-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Replace `<password>` with your actual database password
7. **Save this connection string** - you'll need it for Vercel

---

## 🐙 Part 2: Push Code to GitHub

### 1. Initialize Git Repository (if not already done)

Open Command Prompt or Terminal and navigate to your project directory:

```bash
cd "c:\Users\giris\OneDrive\Desktop\Patient Health Data Management System"
```

If your project isn't already a Git repository, initialize it:

```bash
git init
```

### 2. Create a GitHub Repository

1. Go to [GitHub](https://github.com/) and log in
2. Click the **"+"** icon in the top-right, then **"New repository"**
3. Repository name: `patient-health-management-system`
4. Description: `Patient Health Data Management System - A Flask-based EMR application`
5. Visibility: **Private** or **Public** (your choice)
6. **Do NOT** initialize with README, .gitignore, or license (we already have these)
7. Click **"Create repository"**

### 3. Push Your Code to GitHub

GitHub will show you commands. Use these in your terminal:

```bash
# Add all files to Git
git add .

# Commit the files
git commit -m "Initial commit: Prepare for Vercel deployment"

# Add your GitHub repository as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/patient-health-management-system.git

# Push to GitHub
git branch -M main
git push -u origin main
```

> [!TIP]
> If prompted for credentials, use your GitHub username and a [Personal Access Token](https://github.com/settings/tokens) (not your password).

### 4. Verify Upload

1. Refresh your GitHub repository page
2. You should see all your project files
3. Verify `.env` is **NOT** visible (it should be in `.gitignore`)

---

## 🚀 Part 3: Deploy to Vercel

### 1. Import Project to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Under **"Import Git Repository"**, find your GitHub repository
4. Click **"Import"**

### 2. Configure Project Settings

On the project configuration page:

#### Framework Preset
- Select: **Other** (Vercel will auto-detect Python)

#### Root Directory
- Leave as: **`./`** (root of repository)

#### Build & Development Settings
- **Build Command**: Leave empty (not needed for Python)
- **Output Directory**: Leave empty
- **Install Command**: `pip install -r requirements.txt` (auto-detected)

### 3. Add Environment Variables

Click **"Environment Variables"** and add the following:

| Name | Value | Notes |
|------|-------|-------|
| `MONGODB_URI` | `mongodb+srv://phms-admin:PASSWORD@...` | Your MongoDB Atlas connection string |
| `FLASK_SECRET_KEY` | `[Generate random string]` | Use a password generator for 32+ characters |
| `DATABASE_NAME` | `phms` | Database name |
| `GEMINI_API_KEY` | `[Your API Key]` | (Optional) If using Google Gemini AI features |
| `UPLOAD_FOLDER` | `uploads` | Local folder for uploads (ephemeral) |

> [!WARNING]
> **Generate a strong `FLASK_SECRET_KEY`**: Use a password generator or run this Python command:
> ```python
> import secrets
> print(secrets.token_hex(32))
> ```

### 4. Deploy

1. Click **"Deploy"**
2. Wait for the build to complete (2-5 minutes)
3. If successful, you'll see confetti 🎉 and your deployment URL

---

## ✅ Part 4: Post-Deployment Setup

### 1. Access Your Application

1. Click **"Visit"** or go to your deployment URL (e.g., `https://patient-health-management-system.vercel.app`)
2. You should see the landing page

### 2. Create Admin User

Since this is a fresh deployment with a new database, you need to create an admin user:

#### Option A: Run Locally Against Production DB

1. Update your local `.env` file with the production `MONGODB_URI`
2. Run the admin initialization script:
   ```bash
   python init_admin.py
   ```
3. Follow the prompts to create an admin user
4. **Don't forget to change your `.env` back to local settings after!**

#### Option B: Add Admin Directly to MongoDB Atlas

1. Go to MongoDB Atlas Dashboard
2. Click **"Browse Collections"** on your cluster
3. Select database: `phms`
4. Select collection: `admins`
5. Click **"Insert Document"**
6. Use this template (replace values):
   ```json
   {
     "name": "Admin User",
     "email": "admin@example.com",
     "password": "$2b$12$[BCRYPT_HASH]",
     "created_at": "2025-11-23T16:15:00.000Z"
   }
   ```
   
   To generate bcrypt hash, run Python locally:
   ```python
   import bcrypt
   password = "YourSecurePassword123"
   hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
   print(hashed.decode('utf-8'))
   ```

### 3. Test the Application

1. **Login**: Go to `/login` and sign in with your admin credentials
2. **Add Patient**: Create a test patient
3. **Add Health Record**: Add sample health data
4. **View Dashboard**: Verify charts and data visualization work
5. **Test File Upload**: Try uploading a document (note: it won't persist on Vercel)

---

## 🔧 Part 5: Managing Your Deployment

### Updating Your Application

Whenever you make code changes:

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Add new feature or fix bug"

# Push to GitHub
git push origin main
```

Vercel will **automatically detect** the push and redeploy your application!

### Viewing Logs

1. Go to Vercel Dashboard
2. Select your project
3. Click on a deployment
4. Click **"Functions"** or **"Logs"** tab to see runtime logs

### Rollback to Previous Version

1. Go to Vercel Dashboard → Your Project
2. Click **"Deployments"** tab
3. Find a previous successful deployment
4. Click **"⋯"** → **"Promote to Production"**

### Custom Domain (Optional)

1. In Vercel project settings, go to **"Domains"**
2. Click **"Add"**
3. Enter your domain (e.g., `healthsystem.yourdomain.com`)
4. Follow instructions to update DNS records with your domain registrar

---

## 🐛 Troubleshooting

### Application Error 500

**Check Logs**:
1. Vercel Dashboard → Your Project → Deployments
2. Click the failed deployment → **"Functions"** tab
3. Look for Python errors

**Common causes**:
- Missing environment variables
- MongoDB connection string incorrect
- MongoDB network access not configured for 0.0.0.0/0

### MongoDB Connection Failed

- Verify `MONGODB_URI` is correct in Vercel environment variables
- Ensure MongoDB Atlas allows access from anywhere (0.0.0.0/0)
- Check database user has correct permissions

### Static Files Not Loading

- Ensure `static/` and `templates/` folders are in your Git repository
- Check `vercel.json` routes configuration
- Clear browser cache and hard refresh (Ctrl+Shift+R)

### File Uploads Not Working

This is **expected behavior** on Vercel's free tier:
- Vercel functions are stateless with ephemeral storage
- Files saved during a request are deleted when the function finishes
- Solution: Migrate to cloud storage (Vercel Blob, AWS S3, Cloudflare R2)

### Build Fails: Module Not Found

- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility
- Try adding `runtime.txt` with: `python-3.11`

---

## 🎯 Next Steps

### Recommended Enhancements

1. **Migrate File Storage**
   - Set up [Vercel Blob](https://vercel.com/docs/storage/vercel-blob) for persistent file storage
   - Update upload routes to use cloud storage SDK

2. **Set Up Monitoring**
   - Enable Vercel Analytics
   - Set up error tracking (Sentry, LogRocket, etc.)

3. **Improve Security**
   - Add rate limiting for login attempts
   - Enable HTTPS only (Vercel does this by default)
   - Implement CSRF protection

4. **Performance Optimization**
   - Enable MongoDB read preference for secondary reads
   - Add caching for frequently accessed data
   - Optimize database queries with indexes

---

## 📞 Support Resources

- **Vercel Documentation**: https://vercel.com/docs
- **MongoDB Atlas Docs**: https://docs.atlas.mongodb.com/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **GitHub Help**: https://docs.github.com/

---

## 📝 Summary Checklist

- [ ] MongoDB Atlas cluster created and configured
- [ ] Database user created with read/write permissions
- [ ] Network access configured (0.0.0.0/0)
- [ ] Code pushed to GitHub
- [ ] Vercel project created and connected to GitHub repo
- [ ] Environment variables configured in Vercel
- [ ] Application successfully deployed
- [ ] Admin user created in production database
- [ ] Application tested and working

**Congratulations!** 🎉 Your Patient Health Data Management System is now live on Vercel!
