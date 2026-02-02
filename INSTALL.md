# ⚡ QUICK START - 3 Simple Steps

## Step 1: Install Dependencies

```bash
cd flight-bot
pip install -r requirements.txt
```

**That's it!** Don't run anything else. Just install the requirements.

---

## Step 2: Configure

```bash
python configure.py
```

This wizard will ask you for:
- Your email address
- Gmail app password
- Amadeus API credentials
- Flight preferences

**Or configure manually**:
```bash
cp config.example.yaml config.yaml
nano config.yaml  # Edit your settings
```

---

## Step 3: Test & Run

```bash
# Test email works
python main.py --test-email

# Test price check (no email sent)
python main.py --test --once

# Real run (sends email if deals found)
python main.py --once

# Run continuously (production)
python main.py
```

---

## ✅ That's It!

Your bot is now working. To make it run 24/7, see **DEPLOYMENT_GUIDE.md** for:
- Cloud deployment (Railway.app)
- NAS/Server deployment (systemd)
- Docker deployment
- Cron jobs

---

## 🐛 Having Issues?

### "AttributeError: 'NoneType' object has no attribute 'has_pure_modules'"

**Solution**: Don't try to install the project itself. Only run:
```bash
pip install -r requirements.txt
```

Do NOT run:
- ❌ `pip install .`
- ❌ `pip install -e .`
- ❌ `pip install src`

### "No module named 'yaml'" or similar

**Solution**: Requirements not installed:
```bash
pip install -r requirements.txt
```

### "Configuration file not found"

**Solution**: Create config file:
```bash
python configure.py
# or
cp config.example.yaml config.yaml
```

### "Failed to send email"

**Solution**: Check Gmail app password:
1. Go to https://myaccount.google.com/apppasswords
2. Create new app password
3. Use the 16-character password in config.yaml

---

## 📖 More Help

- **Full documentation**: README.md
- **Deployment options**: DEPLOYMENT_GUIDE.md
- **Configuration reference**: config.example.yaml
