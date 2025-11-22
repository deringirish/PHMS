# Deploying PHMS to Vercel

This guide explains how to deploy the Patient Health Data Management System to Vercel with environment variables.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **MongoDB Atlas**: Cloud MongoDB database (free tier available at [mongodb.com/atlas](https://www.mongodb.com/atlas))
3. **Git Repository**: Push your code to GitHub, GitLab, or Bitbucket
4. **Vercel CLI** (optional): `npm install -g vercel`

## Step 1: Prepare MongoDB Atlas

Since Vercel runs on serverless infrastructure, you need a cloud MongoDB:

1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a **Free Cluster**
3. Create a **Database User** (username & password)
4. **Whitelist IP**: Add `0.0.0.0/0` to allow connections from anywhere (Vercel uses dynamic IPs)
5. Get your **Connection String**:
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string:
     ```
     mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/<dbname>?retryWrites=true&w=majority
     ```
   - Replace `<username>`, `<password>`, and `<dbname>` with your values

## Step 2: Set Up Environment Variables in Vercel

### Option A: Via Vercel Dashboard (Recommended)

1. Go to your project in Vercel Dashboard
2. Navigate to **Settings** > **Environment Variables**
3. Add the following variables:

| Variable Name | Value | Environment |
|--------------|-------|-------------|
| `FLASK_SECRET_KEY` | Generate a random string (e.g., `openssl rand -hex 32`) | Production, Preview, Development |
| `MONGODB_URI` | Your MongoDB Atlas connection string | Production, Preview, Development |
| `DATABASE_NAME` | `phms` (or your database name) | Production, Preview, Development |
| `GEMINI_API_KEY` | Your Google Gemini API key | Production, Preview, Development |

4. Click **Save** for each variable

### Option B: Via Vercel CLI

```bash
vercel env add FLASK_SECRET_KEY production
vercel env add MONGODB_URI production
vercel env add DATABASE_NAME production
vercel env add GEMINI_API_KEY production
```

Follow the prompts to enter values.

## Step 3: Deploy to Vercel

### Method 1: Git Integration (Recommended)

1. **Push code to Git**:
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Import in Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your Git repository
   - Vercel auto-detects Python and uses `vercel.json` configuration
   - Click **Deploy**

3. **Automatic Deployments**:
   - Every push to `main` branch triggers production deployment
   - Pull requests trigger preview deployments

### Method 2: Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   # Preview deployment
   vercel

   # Production deployment
   vercel --prod
   ```

## Step 4: Initialize Admin Account

After deployment, initialize an admin account:

1. **Option A**: Run init script locally connected to Atlas
   ```bash
   # Update .env with Atlas connection
   python init_admin.py
   ```

2. **Option B**: Use MongoDB Compass or Atlas Dashboard
   - Connect to your Atlas cluster
   - Manually insert admin document in `admins` collection

## Step 5: Verify Deployment

1. Visit your Vercel URL (e.g., `https://your-project.vercel.app`)
2. Test the landing page loads
3. Try logging in with admin credentials
4. Check all features work correctly

## Important Notes

### 🚨 File Uploads Limitation

Vercel serverless functions have **read-only filesystem**. The current file upload feature won't work on Vercel.

**Solutions**:
- **Recommended**: Use cloud storage (AWS S3, Cloudinary, or MongoDB GridFS)
- **Alternative**: Use Vercel Blob Storage
- **Temporary**: Disable file upload features for now

### 📝 Viewing Logs

**Via Dashboard**:
- Go to your project > **Deployments**
- Click on a deployment > **Functions** tab
- View runtime logs

**Via CLI**:
```bash
vercel logs [deployment-url]
```

### 🔄 Updating Environment Variables

After updating environment variables in Vercel Dashboard:
1. Go to **Deployments**
2. Click **⋯** on latest deployment
3. Select **Redeploy**

Or re-deploy via CLI/Git push.

## Troubleshooting

### Problem: "Module not found" errors

**Solution**: Ensure all dependencies are in `requirements.txt`
```bash
pip freeze > requirements.txt
```

### Problem: MongoDB connection timeout

**Solution**: 
- Check MongoDB Atlas whitelist includes `0.0.0.0/0`
- Verify connection string is correct
- Ensure database user has read/write permissions

### Problem: Environment variables not loading

**Solution**:
- Verify variables are set in **all environments** (Production, Preview, Development)
- Redeploy after adding variables
- Check variable names match exactly (case-sensitive)

### Problem: 500 Internal Server Error

**Solution**:
- Check Vercel function logs for error details
- Verify all routes are properly imported
- Ensure `api/index.py` correctly imports `app`

### Problem: Static files (CSS/JS) not loading

**Solution**:
- Ensure `static/` directory is included in deployment
- Check paths in templates use `url_for('static', filename='...')`
- May need to add static file serving in `vercel.json`

## Environment-Specific Configuration

### Local Development
```bash
# Use .env file
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=phms
```

### Vercel Production
- Set via Vercel Dashboard
- Use MongoDB Atlas connection string
- Use strong secret keys

## Security Best Practices

1. ✅ **Never commit `.env` file** - Already in `.gitignore`
2. ✅ **Use strong `FLASK_SECRET_KEY`** - Generate with `openssl rand -hex 32`
3. ✅ **Restrict MongoDB access** - Use specific IP ranges if possible
4. ✅ **Enable MongoDB access control** - Create specific database users
5. ✅ **Use HTTPS** - Vercel provides SSL automatically
6. ✅ **Rotate secrets regularly** - Update API keys and passwords periodically

## Useful Commands

```bash
# View deployment info
vercel ls

# View environment variables
vercel env ls

# Remove environment variable
vercel env rm VARIABLE_NAME

# View logs
vercel logs

# Rollback to previous deployment
vercel rollback [deployment-url]
```

## Support & Resources

- **Vercel Docs**: https://vercel.com/docs
- **Python on Vercel**: https://vercel.com/docs/functions/serverless-functions/runtimes/python
- **MongoDB Atlas**: https://docs.atlas.mongodb.com/
- **Vercel Community**: https://github.com/vercel/community

## Next Steps

After successful deployment:
1. Set up custom domain (optional)
2. Configure cloud storage for file uploads
3. Set up monitoring and alerts
4. Implement backup strategy for MongoDB
5. Add CI/CD for automated testing
