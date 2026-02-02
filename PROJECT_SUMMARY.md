# 🎉 Flight Deal Bot - Complete Code Package

## ✅ What You Have

A **fully automated, production-ready flight price monitoring system** for finding cheap flights from Warsaw to Brazil!

## 📦 Package Contents

```
flight-bot/
├── 📄 Core Application
│   ├── main.py                 # Main entry point with CLI
│   ├── setup.py               # Interactive configuration wizard
│   ├── requirements.txt       # Python dependencies
│   └── config.example.yaml    # Configuration template
│
├── 🐍 Source Code (src/)
│   ├── config.py              # Configuration loader
│   ├── flight_api.py          # Amadeus API client
│   ├── database.py            # SQLite database manager
│   ├── analyzer.py            # Price analysis engine
│   ├── email_sender.py        # Email notifications
│   └── scheduler.py           # Automated scheduling
│
├── 🚀 Deployment (deployment/)
│   ├── Procfile               # Railway/Heroku
│   ├── Dockerfile             # Docker container
│   ├── docker-compose.yml     # Docker Compose
│   └── flight-bot.service     # systemd service
│
├── 📚 Documentation
│   ├── README.md              # Complete documentation
│   ├── QUICKSTART.md          # 5-minute setup guide
│   └── LICENSE                # MIT License
│
└── 🔧 Configuration
    ├── .gitignore             # Git ignore rules
    ├── .env.example           # Environment variables
    └── config.example.yaml    # Full configuration example
```

## 🎯 Key Features Implemented

### ✅ All Your Requirements Met

1. **Fully Automated** ✓
   - Runs 24/7 with APScheduler
   - Checks prices every 6 hours (configurable)
   - No manual intervention needed

2. **Major Deals Only** ✓
   - Only alerts on >20% below average
   - Configurable thresholds (amazing/great/good)
   - Smart filtering to avoid spam

3. **Flexible Dates** ✓
   - Variable trip length (10-21 days, configurable)
   - Searches multiple departure dates
   - Target specific periods or search year-round

4. **Connection Preferences** ✓
   - Adjustable max stops (0, 1, 2, any)
   - Preferred hub airports
   - Layover time controls

5. **Airport Flexibility** ✓
   - Different return airports (GRU out, GIG return)
   - Ground transport cost estimation
   - Warnings when applicable

6. **Risk Tolerance** ✓
   - Separate tickets option
   - Conservative/Moderate/Aggressive modes
   - Clear risk warnings

7. **Price Thresholds** ✓
   - Amazing: <2000 PLN or >25% off
   - Great: <2500 PLN or >20% off
   - Good: <3000 PLN or >15% off

### ✅ Additional Features

- **Historical Database**: SQLite with auto-cleanup
- **Email Alerts**: Beautiful HTML + plain text
- **Price Analysis**: Compares to 30/90 day averages
- **Multi-Destination**: GRU, GIG, and more
- **CLI Tools**: Test mode, single run, verbose logging
- **Setup Wizard**: Interactive configuration
- **Error Handling**: Robust with notifications
- **Production Ready**: Logging, monitoring, restart on failure

## 🚀 How to Deploy

### Option 1: Cloud (Railway.app) - Recommended

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin your-repo-url
git push -u origin main

# 2. On railway.app
- New Project → Deploy from GitHub
- Select your repo
- Add environment variables (or use config.yaml)
- Deploy!
```

**Cost**: Free ($5/month credit)

### Option 2: Your NAS/Server

```bash
# 1. Copy to NAS
scp -r flight-bot/ user@nas:/path/to/

# 2. Install and configure
cd /path/to/flight-bot
pip3 install -r requirements.txt
python3 setup.py

# 3. Run as systemd service
sudo cp deployment/flight-bot.service /etc/systemd/system/
sudo systemctl enable flight-bot
sudo systemctl start flight-bot
```

### Option 3: Docker

```bash
cd flight-bot/deployment
docker-compose up -d
```

### Option 4: PythonAnywhere

```bash
# 1. Upload via web interface or git
# 2. Set up scheduled task in web UI:
#    Command: /home/username/.local/bin/python3 /home/username/flight-bot/main.py
#    Schedule: Every 6 hours
```

## ⚙️ Configuration

### Quick Setup

```bash
python setup.py  # Interactive wizard
```

### Manual Setup

```bash
cp config.example.yaml config.yaml
nano config.yaml  # Edit your settings
```

### Key Variables to Adjust

```yaml
# Trip Length (VARIABLE)
trip_length:
  minimum_days: 10
  maximum_days: 21
  flexible_duration: true

# Connections (VARIABLE)
max_stops: 1  # 0, 1, 2, or 99

# Airport Flexibility (VARIABLE)
different_return_airport: true

# Risk Tolerance (VARIABLE)
risk_tolerance: "moderate"  # conservative, moderate, aggressive

# Price Thresholds (VARIABLE)
amazing_deal: 2000  # PLN
major_deal_threshold_percent: 20
```

## 🧪 Testing

```bash
# Test email configuration
python main.py --test-email

# Dry run (no emails sent)
python main.py --test --once

# Single check with email
python main.py --once

# Continuous mode (production)
python main.py
```

## 📧 What You'll Receive

### Email Subject
```
🔥 AMAZING DEAL: Warsaw → São Paulo for 2,180 PLN (26% off!)
```

### Email Content
- Beautiful HTML email with flight details
- Outbound and return flight info
- Connection details
- Price history analysis
- Direct booking links
- Alternative trip lengths

## 🗂️ Database

Automatically maintains SQLite database:
- Last 30 days: Detailed price checks
- Last 365 days: Daily aggregates
- Forever: Monthly aggregates + all deals found

Storage: < 1 MB even after years

## 📊 Monitoring

```bash
# View logs
tail -f logs/flight-bot.log

# Check database
sqlite3 data/flights.db "SELECT * FROM deals ORDER BY found_at DESC LIMIT 10;"

# Check if running
ps aux | grep main.py

# Restart service (if using systemd)
sudo systemctl restart flight-bot
```

## 🔧 Customization

All parameters are in `config.yaml`:
- Email settings
- API credentials
- Routes and destinations
- Date ranges
- Connection preferences
- Price thresholds
- Check frequency
- Alert levels

## 🆘 Troubleshooting

**No emails?**
- Check `logs/flight-bot.log`
- Verify Gmail app password
- Run `python main.py --test-email`

**No API results?**
- Check Amadeus credentials
- Verify API quota (2000/month free)
- Try wider date ranges

**Bot stopped?**
- Check logs for errors
- Restart: `systemctl restart flight-bot`
- Check API limits

## 📝 Next Steps

1. **Configure**: Run `python setup.py` or edit `config.yaml`
2. **Test**: `python main.py --test-email`
3. **Deploy**: Choose deployment method above
4. **Monitor**: Check `logs/flight-bot.log` occasionally
5. **Adjust**: Fine-tune config based on results

## 🎓 Learning Points

This project demonstrates:
- ✅ API integration (Amadeus)
- ✅ Database management (SQLite)
- ✅ Task scheduling (APScheduler)
- ✅ Email automation (SMTP)
- ✅ Price analysis algorithms
- ✅ Configuration management (YAML)
- ✅ Logging and monitoring
- ✅ Deployment automation
- ✅ Production-ready code structure

## 🤝 Support

- **Documentation**: README.md
- **Quick Start**: QUICKSTART.md
- **Issues**: Create GitHub issue
- **Configuration**: config.example.yaml

## 📜 License

MIT License - Use freely!

---

## 🎉 You're All Set!

Your flight deal bot is ready to deploy. It will:

1. ✅ Check prices every 6 hours automatically
2. ✅ Compare to historical averages
3. ✅ Alert only on major deals (>20% off)
4. ✅ Consider multi-leg flights
5. ✅ Send beautiful HTML emails
6. ✅ Store data efficiently
7. ✅ Run 24/7 without intervention

### Push to GitHub and Deploy!

```bash
git init
git add .
git commit -m "Initial commit - Flight Deal Bot"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

**Happy deal hunting! ✈️🇧🇷**

---

*Questions? Check README.md or create an issue on GitHub!*
