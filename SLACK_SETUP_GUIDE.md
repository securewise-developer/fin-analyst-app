# 📱 Slack Slash Command Setup Guide

## ✨ New Feature: `/analyze` Slack Command

Your financial analyst app now supports **Slack slash commands**! Users can analyze stocks directly from Slack using:

```
/analyze AAPL MSFT GOOGL
```

## 🚀 How It Works

1. **User types:** `/analyze NVDA AAPL` in any Slack channel
2. **Immediate response:** Confirmation message shown to channel
3. **Background analysis:** AI-powered analysis runs (2-5 minutes)
4. **Rich results:** Detailed, formatted results posted to channel with:
   - 🟢 **Color-coded grades** (A-F with emojis)
   - 📊 **Trading signals** and confidence scores
   - 🎯 **Trading opportunities** highlighted
   - 👤 **User attribution** (who requested it)

## 🔧 Setup Instructions

### 1. Create Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Name: `Financial Analyst Bot`
4. Choose your workspace

### 2. Configure Slash Command

1. In your app settings, go to **"Slash Commands"**
2. Click **"Create New Command"**
3. Fill in:
   - **Command:** `/analyze`
   - **Request URL:** `https://your-domain.com/api/v1/slack/analyze`
   - **Short Description:** `Analyze financial symbols`
   - **Usage Hint:** `AAPL MSFT GOOGL`

### 3. Set Permissions

1. Go to **"OAuth & Permissions"**
2. Add these scopes under **"Bot Token Scopes"**:
   - `chat:write` (send messages)
   - `commands` (slash commands)
3. Click **"Install to Workspace"**

### 4. Get Bot Token

1. After installation, copy the **"Bot User OAuth Token"**
2. Add to your `.env` file:
   ```bash
   SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   SLACK_CHANNEL=#general
   ```

### 5. Test the Command

1. In any Slack channel, type:
   ```
   /analyze AAPL
   ```
2. You should see immediate confirmation
3. Wait 2-5 minutes for detailed results

## 📊 Example Usage

**Command:**
```
/analyze NVDA AAPL MSFT
```

**Immediate Response:**
```
📊 Financial Analysis Started
Symbols: NVDA, AAPL, MSFT
Requested by: @john.doe
Estimated completion: 2-5 minutes

⏳ Analysis running in background... Results will be posted when complete.
```

**Results Posted Later:**
```
📊 Financial Analysis Complete
Symbols Analyzed: NVDA, AAPL, MSFT
Requested by: @john.doe

🟢 NVDA
Grade: A | Score: 0.85

🔵 AAPL  
Grade: B | Score: 0.73

🟡 MSFT
Grade: C | Score: 0.62

🎯 Trading Opportunities Found: 2
🟢 NVDA - BUY (Confidence: 85%)
🔵 AAPL - BUY (Confidence: 73%)

💡 Tip: Use /analyze SYMBOL1 SYMBOL2 to analyze more stocks
```

## 🔒 Security Features

- **Input validation:** Only valid stock symbols accepted
- **Rate limiting:** Maximum 5 symbols per command
- **Error handling:** Graceful error messages
- **User tracking:** All requests logged with username

## 🛠️ Testing Locally

You can test the endpoint locally:

```bash
# Start your server
python3 scripts/run_server.py

# Test with curl (simulating Slack)
curl -X POST http://localhost:8080/api/v1/slack/analyze \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "token=test&command=/analyze&text=AAPL MSFT&user_name=testuser&channel_name=general"
```

## ⚠️ Important Notes

1. **SSL Required:** Slack requires HTTPS for production
2. **Response Time:** Must respond within 3 seconds (we use background processing)
3. **Rate Limits:** Consider implementing rate limiting for heavy usage
4. **Error Handling:** All errors are sent as ephemeral messages (only visible to user)

## 🎯 Success Indicators

- ✅ Slack app created and installed
- ✅ `/analyze` command configured  
- ✅ Bot token in `.env` file
- ✅ Server running and accessible
- ✅ Command works in Slack channel
- ✅ Analysis results posted back

Your financial analyst is now available directly in Slack! 🚀
