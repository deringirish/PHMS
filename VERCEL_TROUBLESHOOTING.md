# PHMS - Patient Health Data Management System

## Quick Deployment Check

If you're seeing errors after deploying to Vercel, follow these steps:

### 1. Check Vercel Logs
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your project
3. Click on the latest deployment
4. Click **"Functions"** tab
5. Look for any Python errors

### 2. Verify Environment Variables
In Vercel Project Settings → Environment Variables, ensure you have:

- `MONGODB_URI` - Your MongoDB Atlas connection string (starts with `mongodb+srv://`)
- `FLASK_SECRET_KEY` - A random secret key
- `DATABASE_NAME` - Usually `phms`
- `GEMINI_API_KEY` - (Optional) For AI features
- `UPLOAD_FOLDER` - Set to `uploads`

### 3. Common Errors & Solutions

#### Error: "Application Error" or blank page
- **Cause**: MongoDB connection failed
- **Fix**: Check your `MONGODB_URI` is correct and MongoDB Atlas allows access from `0.0.0.0/0`

#### Error: "Module not found"
- **Cause**: Missing dependencies
- **Fix**: Ensure all packages are in `requirements.txt`

#### Error: "Function Timeout"
- **Cause**: MongoDB connection too slow or not responding
- **Fix**: Check MongoDB Atlas is running and accessible

### 4. Re-deploy with Latest Changes

```bash
git add .
git commit -m "Fix Vercel deployment configuration"
git push origin main
```

Vercel will automatically redeploy.

### 5. Test After Deployment

Visit your Vercel URL. You should see the landing page.

---

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)
