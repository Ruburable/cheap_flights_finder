# 🚀 Quick Start Guide

## 5-Minute Setup

### 1. Clone & Install
```bash
git clone https://github.com/yourusername/flight-deal-bot.git
cd flight-deal-bot
pip install -r requirements.txt
```

### 2. Get API Credentials

**Amadeus API** (Free):
- Go to https://developers.amadeus.com/
- Create account → Create App
- Copy API Key and Secret

**Gmail App Password**:
- Go to https://myaccount.google.com/apppasswords
- Create new app password
- Copy 16-character password

### 3. Configure
```bash
python setup.py  # Interactive setup wizard
```

Or manually:
```bash
cp config.example.yaml config.yaml
nano config.yaml  # Edit with your details
```

### 4. Test
```bash
# Test email works
python main.py --test-email

# Test price check (no email sent)
python main.py --test --once

# Real run (sends email if deals found)
python main.py --once
```

### 5. Deploy

**Option A: Cloud (Railway.app)**
```bash
git push origin main
# On railway.app: New Project → Deploy from GitHub
```

**Option B: Your Server**
```bash
# Run continuously
python main.py

# Or as systemd service
sudo cp deployment/flight-bot.service /etc/systemd/system/
sudo systemctl enable flight-bot
sudo systemctl start flight-bot
```

**Option C: Docker**
```bash
cd deployment
docker-compose up -d
```

## Configuration Quick Reference

**Want more deals?**
- Increase `trip_length.maximum_days`
- Increase `max_stops` (0→1→2)
- Enable `different_return_airport`
- Lower `major_deal_threshold_percent` (20→15)

**Want fewer, better deals?**
- Narrow `trip_length` range
- Set `max_stops: 0` (direct only)
- Increase `major_deal_threshold_percent` (20→25)
- Lower price thresholds

**Change check frequency:**
- Edit `check_frequency_hours` (default: 6)

## Troubleshooting

**No emails?**
- Check Gmail app password
- Check spam folder
- Run: `python main.py --test-email`

**No API results?**
- Verify Amadeus credentials
- Check API quota (2000/month free)
- Try wider date ranges

**Bot not running?**
- Check logs: `tail -f logs/flight-bot.log`
- Verify process: `ps aux | grep main.py`

## Support

- Issues: GitHub Issues
- Docs: README.md
- Config help: `config.example.yaml`

Happy deal hunting! ✈️
