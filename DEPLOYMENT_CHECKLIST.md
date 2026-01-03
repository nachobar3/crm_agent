# ✅ AWS Lambda Deployment Checklist - Migraine Feature

## 📊 Summary

**Good News**: Your changes are **READY TO DEPLOY** to AWS Lambda! ✨

All the code changes have been made and all necessary dependencies are already in your `requirements.txt`.

## 🔍 What Changed

### New Files/Updates:
1. ✅ `agent.py` - Added `register_migraine` tool and updated system prompt
2. ✅ `lambda_function.py` - Updated to pass credentials file to agent
3. ✅ `sheets_manager.py` - Made `add_record()` flexible for different sheet structures
4. ✅ `main.py` - Updated for local testing
5. ✅ `MIGRAINE_FEATURE.md` - Documentation created

### Dependencies Check:

| Dependency | In requirements.txt? | In Python 3.11? | Status |
|------------|---------------------|-----------------|---------|
| `json` | N/A | ✅ Built-in | ✅ Ready |
| `os` | N/A | ✅ Built-in | ✅ Ready |
| `tempfile` | N/A | ✅ Built-in | ✅ Ready |
| `datetime` | N/A | ✅ Built-in | ✅ Ready |
| `zoneinfo` | N/A | ✅ Built-in (3.9+) | ✅ Ready |
| `unicodedata` | N/A | ✅ Built-in | ✅ Ready |
| `typing` | N/A | ✅ Built-in | ✅ Ready |
| `telegram` | ✅ Line 1 | via python-telegram-bot | ✅ Ready |
| `openai` | ✅ Line 4 | - | ✅ Ready |
| `gspread` | ✅ Line 2 | - | ✅ Ready |
| `google.oauth2` | ✅ Line 3 | via google-auth | ✅ Ready |
| `langchain` | ✅ Line 5 | - | ✅ Ready |
| `langchain_openai` | ✅ Line 6 | - | ✅ Ready |

**Result**: ✅ **NO NEW DEPENDENCIES NEEDED**

All the new imports (`datetime`, `zoneinfo`) are part of Python's standard library (available in Python 3.11).

## 🚀 Deployment Steps

### Option 1: Automatic Deployment (Recommended)

If you're using GitHub Actions (which you have set up):

```bash
# 1. Commit and push the changes
git add .
git commit -m "Added migraine tracking feature"
git push origin main
```

GitHub Actions will automatically:
- Build the deployment package
- Deploy to Lambda
- Your bot will be updated in ~2-3 minutes

### Option 2: Manual Deployment

If you prefer manual deployment:

```bash
# 1. Create deployment package
mkdir -p build
cp lambda_function.py agent.py sheets_manager.py build/
cd build
zip -r ../deployment.zip .
cd ..

# 2. Deploy to Lambda
aws lambda update-function-code \
  --function-name YOUR_FUNCTION_NAME \
  --zip-file fileb://deployment.zip \
  --region YOUR_REGION

# 3. Clean up
rm -rf build deployment.zip
```

## 🔐 Important: Verify Permissions

Make sure the migraine sheet has permissions for your service account:

1. Open: https://docs.google.com/spreadsheets/d/1Kp9c47qgiQQgDTdRq9vwkWIZsX7zfeVSTEtVJuy8qmA/edit
2. Click "Share"
3. Verify that your service account email is in the list with "Editor" access
4. Service account email is in your credentials JSON: `client_email` field

✅ You mentioned this is already done, so you're good!

## 🧪 Testing After Deployment

### Test 1: Basic Functionality
Send to your bot:
```
"¿Qué día es hoy?"
```
Expected response: Current date in Spanish

### Test 2: Migraine Registration
Send to your bot:
```
"Registra una migraña de hoy, intensidad media, causa: falta de sueño"
```
Expected response:
```
✅ Migraña registrada exitosamente:
- Fecha: 03/01/2026
- Intensidad: Media
- Posible causa: falta de sueño
```

### Test 3: Verify in Sheet
1. Open the migraine sheet
2. Check that a new row was added with today's date
3. Verify the intensity and cause match

### Test 4: Contact Operations Still Work
Send to your bot:
```
"Busca a [nombre de un contacto existente]"
```
Expected: Contact information displayed correctly

## 📋 Current Deployment Architecture

```
┌─────────────────────────────────────────┐
│         GitHub Repository                │
│  - lambda_function.py                    │
│  - agent.py                              │
│  - sheets_manager.py                     │
└──────────────┬──────────────────────────┘
               │ git push
               ▼
┌─────────────────────────────────────────┐
│       GitHub Actions                     │
│  - Builds deployment.zip (code only)    │
│  - Deploys to Lambda                     │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│       AWS Lambda Function                │
│  ┌──────────────────────────────────┐   │
│  │ Code (auto-deployed)             │   │
│  │ - lambda_function.py             │   │
│  │ - agent.py                       │   │
│  │ - sheets_manager.py              │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │ Lambda Layer 1: Credentials      │   │
│  │ - credentials.json               │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │ Lambda Layer 2: Dependencies     │   │
│  │ - python-telegram-bot            │   │
│  │ - gspread                        │   │
│  │ - openai                         │   │
│  │ - langchain                      │   │
│  │ - langchain-openai               │   │
│  │ - google-auth                    │   │
│  │ - python-dotenv                  │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │ Environment Variables            │   │
│  │ - TELEGRAM_API                   │   │
│  │ - SPREADSHEET_ID                 │   │
│  │ - OPENAI_API_KEY                 │   │
│  │ - GOOGLE_CREDENTIALS_FILE        │   │
│  └──────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                ▼
    ┌─────────────────────┐
    │   API Gateway        │
    │   (Webhook)          │
    └──────────┬───────────┘
               ▼
    ┌─────────────────────┐
    │   Telegram Bot       │
    └─────────────────────┘
```

## ⚠️ Important Notes

1. **No Layer Update Required**: 
   - You don't need to update your Lambda Layer
   - `zoneinfo` is built into Python 3.11
   - All other dependencies are already in requirements.txt

2. **Credentials Location**:
   - The code expects `credentials.json` in Lambda
   - Make sure your Lambda has this in a layer or at the root

3. **Environment Variables**:
   - Verify all required env vars are set in Lambda:
     - `TELEGRAM_API`
     - `SPREADSHEET_ID`
     - `OPENAI_API_KEY`
     - `GOOGLE_CREDENTIALS_FILE` (should be `credentials.json`)

4. **Python Version**:
   - Lambda must use Python 3.11 or 3.12
   - (Python 3.9+ supports zoneinfo)

## 🎯 Quick Deployment Command

If you're ready to deploy right now:

```bash
git add agent.py lambda_function.py main.py sheets_manager.py MIGRAINE_FEATURE.md DEPLOYMENT_CHECKLIST.md
git commit -m "feat: Added migraine tracking feature with register_migraine tool"
git push origin main
```

Then monitor the GitHub Actions tab to see the deployment progress.

## ✅ Post-Deployment Verification

1. Check GitHub Actions succeeded
2. Test the bot with migraine registration
3. Verify data appears in the migraine sheet
4. Test that existing contact features still work

## 🐛 Troubleshooting

### If bot doesn't respond:
- Check Lambda CloudWatch logs
- Verify environment variables are set
- Check API Gateway webhook is connected

### If migraine registration fails:
- Verify sheet permissions for service account
- Check that sheet has correct column names: `Fecha`, `Intensidad`, `Posible causa`
- Look for error messages in CloudWatch

### If date is wrong:
- Verify Lambda timezone (should use Argentina/Buenos Aires)
- Check that `zoneinfo` is available (Python 3.11+ required)

---

**Status**: 🟢 **READY TO DEPLOY**

All changes are compatible with your current Lambda setup and require no infrastructure changes!
