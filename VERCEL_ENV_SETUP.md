# Quick Start: Vercel Environment Variables

## Copy these exact variable names into Vercel Dashboard

Go to: **Project Settings → Environment Variables**

### Required Variables

```
Variable Name: FLASK_SECRET_KEY
Value: [Generate with: openssl rand -hex 32]
Environments: ✓ Production ✓ Preview ✓ Development
```

```
Variable Name: MONGODB_URI
Value: mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/phms?retryWrites=true&w=majority
Environments: ✓ Production ✓ Preview ✓ Development
```

```
Variable Name: DATABASE_NAME
Value: phms
Environments: ✓ Production ✓ Preview ✓ Development
```

```
Variable Name: GEMINI_API_KEY
Value: [Your Gemini API Key]
Environments: ✓ Production ✓ Preview ✓ Development
```

## How to Get Values

### FLASK_SECRET_KEY
Generate a secure random key:
```bash
# On Mac/Linux
openssl rand -hex 32

# Or use Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### MONGODB_URI
1. Go to MongoDB Atlas: https://cloud.mongodb.com
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string
5. Replace `<username>`, `<password>`, and `<dbname>`

Example:
```
mongodb+srv://admin:MyPassword123@cluster0.abc123.mongodb.net/phms?retryWrites=true&w=majority
```

### DATABASE_NAME
Use: `phms` (or any name you prefer)

### GEMINI_API_KEY
1. Go to: https://makersuite.google.com/app/apikey
2. Create API key
3. Copy the key

## After Adding Variables

1. Click **Save** for each variable
2. Go to **Deployments** tab
3. Click **Redeploy** on latest deployment
   OR
4. Push a new commit to trigger deployment

## Verify Variables Are Set

```bash
# Using Vercel CLI
vercel env ls
```

You should see all 4 variables listed for all environments.
