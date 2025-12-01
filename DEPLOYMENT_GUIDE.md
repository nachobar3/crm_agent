# 🚀 Deployment Guide

## How Dependencies Work

### What `git push` Does:
- ✅ Pushes your code to GitHub
- ✅ **NEW**: Automatically triggers GitHub Actions workflow
- ✅ **NEW**: Builds deployment package with ALL dependencies
- ✅ **NEW**: Deploys to AWS Lambda automatically

### What Changed:
Your GitHub Actions workflow (`.github/workflows/deploy.yml`) now:
1. Installs all dependencies from `requirements.txt`
2. Bundles them with your code
3. Deploys everything to Lambda automatically

## 📝 Deployment Process (Now Automated!)

### When you make changes:

```bash
# 1. Make your changes to the code
git add .
git commit -m "Added datetime tool"

# 2. Push to main branch
git push origin main

# 3. GitHub Actions automatically:
#    - Installs dependencies (including pytz)
#    - Packages everything
#    - Deploys to AWS Lambda
```

### Monitor the deployment:
Go to: `https://github.com/YOUR_USERNAME/nacho_leads/actions`

## 🔧 Manual Deployment (If Needed)

If you need to deploy manually:

```bash
# 1. Create deployment package
mkdir -p build
pip install -r requirements.txt -t build/
cp lambda_function.py agent.py sheets_manager.py asociate-f8e54014d9ea.json build/

# 2. Create zip
cd build
zip -r ../deployment.zip .
cd ..

# 3. Update Lambda
aws lambda update-function-code \
  --function-name YOUR_FUNCTION_NAME \
  --zip-file fileb://deployment.zip \
  --region YOUR_REGION
```

## 📦 What Gets Deployed

Your deployment package now includes:
- ✅ `lambda_function.py` - AWS Lambda handler
- ✅ `agent.py` - AI agent with tools
- ✅ `sheets_manager.py` - Google Sheets integration
- ✅ `asociate-f8e54014d9ea.json` - Google credentials
- ✅ **All dependencies** from `requirements.txt` including:
  - python-telegram-bot
  - gspread
  - openai
  - langchain
  - **pytz** (NEW!)
  - etc.

## ⚠️ Important Notes

1. **Environment Variables**: Make sure these are set in AWS Lambda:
   - `TELEGRAM_API`
   - `SPREADSHEET_ID`
   - `OPENAI_API_KEY`
   - `GOOGLE_CREDENTIALS_FILE` (defaults to "credentials.json")

2. **Package Size**: The deployment package might be larger now (~50-100MB) because dependencies are bundled. This is normal and acceptable for Lambda.

3. **Credentials**: The `asociate-f8e54014d9ea.json` file is now included in deployments automatically.

## 🧪 Testing After Deployment

After pushing to main:
1. Wait 2-3 minutes for deployment to complete
2. Send a test message to your Telegram bot
3. Check CloudWatch logs if there are issues

## 🔍 Troubleshooting

### Deployment fails:
- Check GitHub Actions logs: `https://github.com/YOUR_USERNAME/nacho_leads/actions`
- Verify AWS credentials are configured in GitHub Secrets

### Bot doesn't respond:
- Check AWS Lambda logs in CloudWatch
- Verify environment variables are set
- Test the function manually in AWS Console

### Import errors:
- Make sure all dependencies are in `requirements.txt`
- Re-run the deployment

---

**Last Updated**: December 2025

