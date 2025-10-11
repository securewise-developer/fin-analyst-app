# 🚀 Financial Analyst App

A professional-grade financial analysis and trading monitoring application with REST API, automated Slack notifications, and comprehensive stock analysis capabilities.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-production--ready-success)

## ✨ Features

### 📊 **Comprehensive Financial Analysis**
- **AI-Powered Analysis**: GPT-4 driven insights and recommendations
- **Grade System**: A-F rating system for investment quality
- **Technical Analysis**: 20+ indicators including RSI, MACD, Bollinger Bands
- **Fundamental Analysis**: P/E ratios, debt ratios, growth metrics
- **News Sentiment**: Real-time news analysis with sentiment scoring
- **Risk Assessment**: Comprehensive risk evaluation

### 🎯 **Trading Intelligence**
- **Smart Signals**: BUY/SELL/HOLD recommendations with confidence scores
- **Entry/Exit Points**: Precise price targets and stop-loss levels
- **Position Sizing**: Risk-adjusted position size recommendations
- **Market Timing**: Optimal timing analysis for trades
- **Portfolio Integration**: Multi-symbol analysis and comparison

### 🔌 **Professional API**
- **REST API**: Clean, well-documented endpoints
- **Background Processing**: Non-blocking analysis execution
- **Real-time Notifications**: Automatic Slack integration
- **Multiple Formats**: JSON output with structured data
- **Error Handling**: Comprehensive error responses

### 📱 **Integrations**
- **Slack Bot**: Automated notifications with rich formatting
- **Slack Slash Commands**: `/analyze AAPL MSFT` directly in Slack
- **Multiple Data Sources**: Yahoo Finance, FMP, News APIs
- **CLI Interface**: Command-line tools for automation
- **Docker Ready**: Containerization support

## 🏗️ Architecture

```
app/
├── api/                    # REST API Layer
│   ├── routes.py          # API endpoints
│   └── schemas.py         # Request/response models
├── core/                   # Business Logic
│   ├── analyzer.py        # Main analysis orchestrator
│   ├── trading_monitor.py # Real-time monitoring
│   ├── grading.py         # Scoring system
│   └── synthesize.py      # AI report generation
├── data/                   # Data Access Layer
│   ├── providers/         # External data sources
│   └── models.py          # Data models
├── services/               # External Services
│   ├── slack_service.py   # Slack integration
│   ├── llm_service.py     # AI/LLM service
│   └── news_service.py    # News processing
└── utils/                  # Utilities
    ├── indicators.py      # Technical indicators
    ├── fundamentals.py    # Fundamental analysis
    └── helpers.py         # Helper functions
```

## 🚀 Quick Start

### 1. **Installation**

```bash
# Clone the repository
git clone <your-repo-url>
cd fin-analyst-app

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. **Configuration**

Create a `.env` file with your API keys:

```bash
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional (for enhanced features)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL=#trading
FMP_API_KEY=your-fmp-api-key
```

### 3. **Start the Server**

```bash
# Development server
python3 scripts/run_server.py

# Production server
gunicorn --bind 0.0.0.0:8080 wsgi:application
```

The API will be available at `http://localhost:8080`

## 📡 API Reference

### **POST /api/v1/analyze**

Analyze financial symbols and get results via Slack.

**Request:**
```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "detailed": true,
  "mode": "once"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Analysis started for 3 symbols",
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "estimated_completion": "2-5 minutes"
}
```

**Example:**
```bash
curl -X POST http://localhost:8080/api/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"symbols": ["AAPL", "MSFT"], "detailed": true}'
```

### **POST /api/v1/slack/analyze**

Slack slash command endpoint for `/analyze` commands.

**Slack Command Usage:**
```
/analyze AAPL MSFT GOOGL
```

**Features:**
- Accepts up to 5 symbols per command
- Returns immediate confirmation to Slack
- Sends detailed results when analysis completes
- Rich formatting with grades, scores, and trading signals
- User attribution in notifications

### **GET /api/v1/status**

Get application configuration and status.

### **GET /health**

Health check endpoint.

## 🖥️ CLI Usage

### **Single Symbol Analysis**
```bash
python3 -m cli.commands analyze --symbol AAPL --type equity
```

### **Multi-Symbol Monitoring**
```bash
# One-time analysis
python3 -m cli.commands monitor --symbols AAPL MSFT GOOGL --detailed

# Continuous monitoring
python3 -m cli.commands monitor --symbols AAPL MSFT --mode continuous --interval 15
```

### **Configuration Check**
```bash
python3 -m cli.commands status
```

## 📊 Analysis Output

### **Grade System**

| Grade | Score Range | Description           | Recommendation |
| ----- | ----------- | --------------------- | -------------- |
| **A** | 0.8 - 1.0   | Excellent opportunity | Strong BUY     |
| **B** | 0.65 - 0.79 | Good opportunity      | BUY            |
| **C** | 0.5 - 0.64  | Neutral               | HOLD           |
| **D** | 0.35 - 0.49 | Poor quality          | Avoid          |
| **F** | 0.0 - 0.34  | High risk             | Strong SELL    |

### **Sample Output**

```json
{
  "symbol": "AAPL",
  "grade": "B",
  "overall_score": 0.73,
  "trading_signal": {
    "action": "BUY",
    "confidence": 0.82,
    "entry_price": 150.50,
    "stop_loss": 145.00,
    "take_profit": 165.00,
    "position_size": "2-3% of portfolio",
    "time_horizon": "2-4 weeks"
  },
  "analysis": {
    "fundamental_score": 0.78,
    "technical_score": 0.71,
    "news_sentiment": 0.65,
    "key_drivers": [
      "Strong quarterly earnings beat",
      "Positive analyst upgrades",
      "Technical breakout above resistance"
    ],
    "risk_factors": [
      "Market volatility concerns",
      "Sector rotation potential"
    ]
  }
}
```

## 📱 Slack Integration

### **Slash Commands**
Use `/analyze` directly in Slack:
```
/analyze AAPL MSFT GOOGL NVDA TSLA
```

### **Rich Notifications**
The app automatically sends beautifully formatted notifications:

- **🟢 Grade A-F** with color-coded emojis
- **Trading Signals** with confidence levels
- **Entry/Exit Points** with precise prices
- **Risk Analysis** with key factors
- **User Attribution** showing who requested analysis
- **Trading Opportunities** highlighted prominently

### **Setup for Slash Commands**
1. Create a Slack App at https://api.slack.com/apps
2. Add `/analyze` slash command pointing to: `https://your-domain.com/api/v1/slack/analyze`
3. Add required scopes: `chat:write`, `commands`
4. Install app to your workspace

## 🔧 Configuration

### **Environment Variables**

| Variable          | Required | Description                         |
| ----------------- | -------- | ----------------------------------- |
| `OPENAI_API_KEY`  | ✅        | OpenAI API key for AI analysis      |
| `SLACK_BOT_TOKEN` | ❌        | Slack bot token for notifications   |
| `SLACK_CHANNEL`   | ❌        | Slack channel for notifications     |
| `FMP_API_KEY`     | ❌        | Financial Modeling Prep API key     |
| `NEWSAPI_KEY`     | ❌        | News API key for sentiment analysis |

### **API Keys Setup**

1. **OpenAI** (Required): https://platform.openai.com/api-keys
2. **Slack Bot** (Optional): https://api.slack.com/apps
3. **FMP** (Optional): https://financialmodelingprep.com/developer
4. **News API** (Optional): https://newsapi.org/

## 🐳 Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:application"]
```

```bash
# Build and run
docker build -t fin-analyst .
docker run -p 8080:8080 --env-file .env fin-analyst
```

## 🧪 Testing

```bash
# Run basic tests
python3 -m pytest tests/

# Test configuration
python3 -m cli.commands status

# Test API endpoints
curl http://localhost:8080/health
```

## 📈 Performance

- **Analysis Speed**: 30-60 seconds per symbol
- **Concurrent Requests**: Up to 10 simultaneous analyses
- **Data Sources**: Real-time and historical data
- **Uptime**: 99.9% availability target
- **Response Time**: < 500ms for API responses

## 🔒 Security

- ✅ Environment-based configuration
- ✅ Input validation and sanitization
- ✅ Rate limiting and error handling
- ✅ Secure API key management
- ✅ HTTPS-ready deployment

## 🛠️ Development

### **Project Structure**
- **Clean Architecture**: Separated concerns and dependencies
- **Type Hints**: Full type annotations
- **Error Handling**: Comprehensive error management
- **Logging**: Structured logging throughout
- **Documentation**: Inline and external docs

### **Contributing**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📚 Documentation

- **API Documentation**: Available at `/api/v1/docs` (when running)
- **Architecture Guide**: See `NEW_STRUCTURE_GUIDE.md`
- **Migration Guide**: See `REFACTORING_SUMMARY.md`
- **Quick Start**: See `QUICK_START.md`

## ⚠️ Disclaimer

This application is for educational and analysis purposes only. It is not financial advice. Always:

- ✅ Do your own research
- ✅ Consult financial advisors
- ✅ Practice proper risk management
- ✅ Test with small amounts first
- ✅ Understand the risks involved

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Documentation**: Check the docs/ directory
- **Email**: Contact the maintainers

---

**Built with ❤️ for the trading community**

*Transform your trading decisions with AI-powered financial analysis*