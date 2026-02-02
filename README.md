# ✈️ Flight Deal Bot - Warsaw to Brazil

Automated flight price monitoring system that finds and alerts you about cheap flights from Warsaw (WAW) to Brazil.

## 🎯 Features

- **Fully Automated**: Runs 24/7 checking prices every 6 hours
- **Smart Alerts**: Only notifies on major deals (>20% below average)
- **Multi-Flight Support**: Considers connections and multi-leg itineraries
- **Flexible Configuration**: All parameters adjustable via YAML
- **Email Notifications**: Detailed deal alerts sent to your inbox
- **Historical Tracking**: Builds price database to identify true deals

## 🚀 Quick Start

**New to this? Start here**:
1. **INSTALL.md** - Simple 3-step installation
2. **VISUAL_GUIDE.md** - Understand deployment options with diagrams
3. **DEPLOYMENT_GUIDE.md** - Detailed deployment instructions

### 1. Prerequisites

- Python 3.9 or higher
- Gmail account (for sending alerts)
- Amadeus API account (free tier available)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/flight-deal-bot.git
cd flight-deal-bot

# Install dependencies (IMPORTANT: Only run this!)
pip install -r requirements.txt
```

**⚠️ IMPORTANT**: Only run `pip install -r requirements.txt`
- Do NOT run: `pip install .`
- Do NOT run: `pip install -e .`
- Do NOT run: `pip install src`

### 3. Configuration

#### Get API Credentials

**Amadeus API** (Recommended - Free Tier):
1. Go to https://developers.amadeus.com/
2. Create account and get API Key + Secret
3. Free tier: 2000 API calls/month (enough for 4 checks/day)

**Gmail App Password**:
1. Go to https://myaccount.google.com/apppasswords
2. Create app password for "Mail"
3. Copy the 16-character password

#### Edit Configuration

Copy the example config and edit it:

```bash
cp config.example.yaml config.yaml
nano config.yaml  # or use your favorite editor
```

**Or use the interactive wizard**:
```bash
python configure.py
```

Edit these critical fields:
```yaml
email:
  recipient: "your.email@gmail.com"
  sender_gmail: "your.bot@gmail.com"
  smtp_password: "your_16_char_app_password"

api:
  amadeus_api_key: "YOUR_KEY"
  amadeus_api_secret: "YOUR_SECRET"
```

### 4. Run Configuration (Optional)

```bash
# Interactive configuration wizard
python configure.py

# Or manually copy and edit
cp config.example.yaml config.yaml
nano config.yaml
```

### 5. Test Run

```bash
# Test single check
python main.py --test

# Run once and exit
python main.py --once
```

### 5. Deploy

Choose your deployment method:

#### Option A: Cloud (Recommended)

**Railway.app** (Easiest):
```bash
# Push to GitHub
git add .
git commit -m "Initial commit"
git push origin main

# On railway.app:
1. New Project → Deploy from GitHub
2. Select your repo
3. Add environment variables (optional - can use config.yaml)
4. Deploy
```

**PythonAnywhere**:
```bash
# Upload via git or web interface
# Set scheduled task: python /path/to/main.py
```

#### Option B: Your NAS/Server

```bash
# Set up as systemd service
sudo cp deployment/flight-bot.service /etc/systemd/system/
sudo systemctl enable flight-bot
sudo systemctl start flight-bot
```

Or use cron:
```bash
crontab -e
# Add: 0 */6 * * * /usr/bin/python3 /path/to/flight-bot/main.py --once
```

## ⚙️ Configuration Guide

### Key Variables

All adjustable via `config.yaml`:

```yaml
# Trip Length (VARIABLE)
trip_length:
  minimum_days: 10
  maximum_days: 21
  flexible_duration: true

# Connections (VARIABLE)
connections:
  max_stops: 1  # 0=direct, 1, 2, or 99=any

# Airport Flexibility (VARIABLE)
airport_flexibility:
  different_return_airport: true

# Risk Tolerance (VARIABLE)
separate_tickets:
  enabled: true
  risk_tolerance: "moderate"  # conservative, moderate, aggressive

# Price Thresholds (VARIABLE)
price_alerts:
  amazing_deal: 2000  # PLN
  great_deal: 2500
  major_deal_threshold_percent: 20
```

### Alert Levels

- 🔥 **AMAZING** (<2000 PLN or >25% off): Book immediately
- ⭐ **GREAT** (<2500 PLN or >20% off): Very good price
- ✓ **GOOD** (<3000 PLN or >15% off): Worth considering

Only **GREAT** and **AMAZING** deals trigger emails (major_deals_only mode).

## 📧 Email Alerts

You'll receive emails like this:

```
Subject: 🔥 AMAZING DEAL: Warsaw → São Paulo for 2,180 PLN (26% off!)

Route: WAW → GRU / GIG → WAW
Price: 2,180 PLN (round-trip)
Discount: 26% below average

✈️ OUTBOUND: Jun 15, WAW → GRU via LIS (1 stop)
✈️ RETURN: Jun 27, GIG → WAW via MAD (1 stop)

[Book Now] [View Details]
```

## 🗂️ Project Structure

```
flight-deal-bot/
├── main.py                 # Main entry point
├── config.yaml            # Your configuration (gitignored)
├── config.example.yaml    # Example configuration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables example
├── .gitignore            # Git ignore rules
├── README.md             # This file
│
├── src/
│   ├── __init__.py
│   ├── config.py         # Configuration loader
│   ├── flight_api.py     # Amadeus API client
│   ├── database.py       # SQLite database manager
│   ├── analyzer.py       # Price analysis engine
│   ├── email_sender.py   # Email notification system
│   └── scheduler.py      # APScheduler setup
│
├── deployment/
│   ├── Procfile          # For Railway/Heroku
│   ├── flight-bot.service  # systemd service
│   └── Dockerfile        # Docker container
│
├── data/
│   └── flights.db        # SQLite database (auto-created)
│
└── logs/
    └── flight-bot.log    # Application logs (auto-created)
```

## 🔧 Advanced Usage

### Command Line Options

```bash
# Run continuously (production)
python main.py

# Test mode (dry run, no emails)
python main.py --test

# Run once and exit
python main.py --once

# Force check now (ignores schedule)
python main.py --force

# Verbose logging
python main.py --verbose

# Specific config file
python main.py --config my-config.yaml
```

### Environment Variables

Instead of config.yaml, you can use environment variables:

```bash
export EMAIL_RECIPIENT="your@email.com"
export GMAIL_SENDER="bot@gmail.com"
export GMAIL_PASSWORD="xxxx"
export AMADEUS_API_KEY="xxxx"
export AMADEUS_API_SECRET="xxxx"

python main.py
```

## 📊 Database

The bot maintains a SQLite database (`data/flights.db`) with:

- **price_checks**: Every price check (30 days detailed)
- **daily_stats**: Daily aggregates (365 days)
- **monthly_stats**: Monthly aggregates (unlimited)
- **deals**: Record of all deals found

View your data:
```bash
sqlite3 data/flights.db "SELECT * FROM deals ORDER BY found_at DESC LIMIT 10;"
```

## 🛠️ Troubleshooting

### No emails received?

1. Check Gmail app password is correct
2. Check spam folder
3. Review logs: `tail -f logs/flight-bot.log`
4. Test email: `python main.py --test-email`

### No API results?

1. Verify Amadeus credentials
2. Check API quota (2000/month on free tier)
3. Try different date ranges
4. Check logs for API errors

### Bot not running?

1. Check process: `ps aux | grep main.py`
2. Check logs: `tail -f logs/flight-bot.log`
3. Verify schedule: `cat /var/log/syslog | grep flight-bot`

## 🤝 Contributing

Feel free to open issues or submit PRs!

## 📝 License

MIT License - feel free to use and modify

## 🙏 Credits

- Flight data: Amadeus API
- Inspiration: Wanting to visit Brazil without breaking the bank

## 📞 Support

- Issues: GitHub Issues
- Questions: GitHub Discussions
- Email: your@email.com

---

**Happy Deal Hunting! 🎉✈️🇧🇷**
