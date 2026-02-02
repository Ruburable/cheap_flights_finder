# 📘 Complete Deployment Guide - Step by Step

## Problem 1: Fixing the `src` Installation Error

### What Happened?
When you ran `pip install -r requirements.txt`, pip saw a folder called `src` and tried to install it as a package. This is wrong - `src` is just a folder containing our code, not a package to install.

### ✅ Solution: How to Install Correctly

```bash
# Navigate to your project folder
cd flight-bot

# Install ONLY the requirements (NOT the src folder)
pip install -r requirements.txt

# That's it! Don't try to install the project itself
```

**Important**: You should NOT run:
- ❌ `pip install .`
- ❌ `pip install -e .`
- ❌ `pip install src`

Just run: ✅ `pip install -r requirements.txt`

### Why This Works
The `src` folder is a **source code directory**, not a package. Python will find it automatically because:
1. `main.py` adds `src` to the Python path
2. Python looks in the current directory for imports

---

## Problem 2: Understanding Deployment Options

You have **4 main ways** to run this bot. Let me explain each in detail:

---

## 🚀 Option 1: Cloud Deployment (Railway.app) - EASIEST

### What is it?
Railway.app is a free cloud service that runs your code 24/7. Think of it as "renting a computer in the cloud" that never sleeps.

### Step-by-Step Setup:

#### A. Push Your Code to GitHub

```bash
# 1. Go to your project folder
cd flight-bot

# 2. Initialize git (if not already done)
git init

# 3. Add all files
git add .

# 4. Commit
git commit -m "Initial flight bot"

# 5. Create a repository on GitHub
# Go to github.com → New Repository → Create

# 6. Connect and push
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

#### B. Deploy to Railway

1. **Go to**: https://railway.app/
2. **Sign up** with your GitHub account (free)
3. **Click**: "New Project"
4. **Select**: "Deploy from GitHub repo"
5. **Choose**: Your flight-bot repository
6. **Railway will**:
   - Automatically detect Python
   - Install requirements.txt
   - Start running main.py

#### C. Add Your Configuration

**Option A - Upload config.yaml:**
1. In Railway dashboard → Files tab
2. Upload your `config.yaml` file

**Option B - Use Environment Variables:**
1. In Railway → Variables tab
2. Add these variables:
   ```
   EMAIL_RECIPIENT=your@email.com
   GMAIL_SENDER=bot@gmail.com
   GMAIL_PASSWORD=your_app_password
   AMADEUS_API_KEY=your_key
   AMADEUS_API_SECRET=your_secret
   ```

#### D. That's It!
Your bot is now running 24/7 in the cloud!

**Cost**: Free ($5/month credit, usually enough for this bot)

---

## 💻 Option 2: Your Own Computer/NAS - ALWAYS RUNNING

### What is it?
Run the bot on your own computer or NAS (Network Attached Storage) that's always on.

### Step-by-Step Setup:

#### A. Copy Files to Your Computer/NAS

```bash
# If using NAS with SSH:
scp -r flight-bot/ username@nas-ip-address:/path/where/you/want/it

# Or just download and extract the folder to your NAS
```

#### B. Install Python and Dependencies

```bash
# On your NAS/Computer, navigate to the folder
cd /path/to/flight-bot

# Install Python 3.9+ if not already installed
# (How to do this depends on your NAS - check manufacturer docs)

# Install requirements
pip3 install -r requirements.txt
```

#### C. Configure the Bot

```bash
# Run the configuration wizard
python3 configure.py

# Or manually:
cp config.example.yaml config.yaml
nano config.yaml  # Edit with your settings
```

#### D. Test It

```bash
# Test that everything works
python3 main.py --test-email

# Run once to check
python3 main.py --once
```

#### E. Keep It Running - Choose One Method:

### **Method 2A: Simple Background Process**

This is the EASIEST way:

```bash
# Run in background (will stop if you close terminal or NAS reboots)
nohup python3 main.py > logs/output.log 2>&1 &

# To check if it's running:
ps aux | grep main.py

# To stop it:
pkill -f main.py
```

**Pros**: Super simple
**Cons**: Stops when you reboot

---

### **Method 2B: systemd Service (Linux/NAS)**

This is BETTER - it restarts automatically if it crashes or if your NAS reboots.

**What is systemd?**
systemd is Linux's system manager. It can start programs automatically when your computer boots and restart them if they crash.

**Step-by-Step:**

1. **Edit the service file**:

```bash
cd /path/to/flight-bot/deployment
nano flight-bot.service
```

2. **Change these lines** to match your setup:

```ini
[Unit]
Description=Flight Deal Bot - Automated price monitoring
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME              # ← Change this to your username
WorkingDirectory=/path/to/flight-bot    # ← Change to actual path
ExecStart=/usr/bin/python3 /path/to/flight-bot/main.py  # ← Change path
Restart=on-failure
RestartSec=10
StandardOutput=append:/path/to/flight-bot/logs/flight-bot.log
StandardError=append:/path/to/flight-bot/logs/flight-bot-error.log

[Install]
WantedBy=multi-user.target
```

**How to find your username**:
```bash
whoami
```

**How to find Python path**:
```bash
which python3
# Use this path in ExecStart
```

3. **Copy the service file**:

```bash
sudo cp flight-bot.service /etc/systemd/system/
```

4. **Enable and start**:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable (start on boot)
sudo systemctl enable flight-bot

# Start now
sudo systemctl start flight-bot

# Check status
sudo systemctl status flight-bot
```

5. **Useful commands**:

```bash
# Stop the bot
sudo systemctl stop flight-bot

# Restart the bot
sudo systemctl restart flight-bot

# View logs
sudo journalctl -u flight-bot -f

# Disable auto-start
sudo systemctl disable flight-bot
```

**Pros**: Auto-restarts, starts on boot, professional
**Cons**: Requires root/sudo access

---

### **Method 2C: Cron Job (Scheduled Runs)**

Instead of running 24/7, run every 6 hours using cron.

**What is cron?**
Cron is a scheduler built into Linux. You tell it "run this command at these times" and it does it automatically.

**Step-by-Step:**

1. **Open crontab**:
```bash
crontab -e
```

2. **Add this line** at the bottom:
```bash
# Run every 6 hours
0 */6 * * * cd /path/to/flight-bot && /usr/bin/python3 main.py --once >> logs/cron.log 2>&1
```

**What this means**:
- `0 */6 * * *` = Every 6 hours at minute 0 (00:00, 06:00, 12:00, 18:00)
- `cd /path/to/flight-bot` = Go to project directory
- `/usr/bin/python3 main.py --once` = Run the bot once
- `>> logs/cron.log 2>&1` = Save output to log file

3. **Save and exit** (usually Ctrl+X, then Y, then Enter)

4. **Check it's scheduled**:
```bash
crontab -l
```

**Cron schedule examples**:
```bash
# Every 6 hours
0 */6 * * * command

# Every day at 8am
0 8 * * * command

# Every 12 hours (8am and 8pm)
0 8,20 * * * command

# Every 4 hours
0 */4 * * * command
```

**Pros**: Simple, doesn't use resources when not running
**Cons**: Not truly 24/7, runs at specific times

---

## 🐳 Option 3: Docker - CONTAINER DEPLOYMENT

### What is Docker?
Docker is like a "virtual box" that contains your app and everything it needs. You can move this box anywhere and it will work the same.

**When to use**: If you're familiar with Docker or want an isolated environment.

### Step-by-Step:

#### A. Install Docker

On most systems:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose  # or check docker docs for your system
```

#### B. Build and Run

```bash
# Go to your project
cd flight-bot

# Build the Docker image
docker build -f deployment/Dockerfile -t flight-bot .

# Run the container
docker run -d \
  --name flight-bot \
  --restart unless-stopped \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  flight-bot
```

**Or use Docker Compose (easier)**:

```bash
cd flight-bot/deployment

# Edit docker-compose.yml if needed
# Then start:
docker-compose up -d
```

#### C. Manage the Container

```bash
# Check if running
docker ps

# View logs
docker logs -f flight-bot

# Stop
docker stop flight-bot

# Start
docker start flight-bot

# Restart
docker restart flight-bot

# Remove
docker rm -f flight-bot
```

**Pros**: Isolated, portable, professional
**Cons**: Need to learn Docker, extra complexity

---

## 📝 Option 4: PythonAnywhere - FREE CLOUD

### What is it?
PythonAnywhere is a website where you can run Python code for free.

### Step-by-Step:

1. **Sign up**: https://www.pythonanywhere.com/ (free account)

2. **Upload your code**:
   - Go to "Files" tab
   - Upload all your project files
   - Or use git: `git clone your-repo-url`

3. **Install requirements**:
   - Go to "Consoles" tab → Start bash console
   ```bash
   cd flight-bot
   pip install --user -r requirements.txt
   ```

4. **Configure**:
   - Edit config.yaml via their web editor
   - Or upload your configured config.yaml

5. **Set up scheduled task**:
   - Go to "Tasks" tab
   - Add a new scheduled task:
   - Command: `/home/yourusername/.local/bin/python3 /home/yourusername/flight-bot/main.py --once`
   - Frequency: Every day at 00:00, 06:00, 12:00, 18:00

**Pros**: Free, no server needed, web interface
**Cons**: Free tier limited (1 scheduled task), must renew every 3 months

---

## 🎯 Which Option Should You Choose?

### Choose **Railway** if:
- ✅ You want easiest setup
- ✅ You don't have always-on hardware
- ✅ You're okay with $0-5/month cost
- ✅ You want it to "just work"

### Choose **NAS/Server** if:
- ✅ You have a NAS or always-on computer
- ✅ You want full control
- ✅ You want zero recurring costs
- ✅ You're comfortable with command line

### Choose **Docker** if:
- ✅ You already use Docker
- ✅ You want isolation from other apps
- ✅ You might move it to different servers

### Choose **PythonAnywhere** if:
- ✅ You want free cloud hosting
- ✅ You're okay with web interface
- ✅ You don't mind renewing every 3 months

---

## 🆘 Troubleshooting

### Bot not installing?
```bash
# Make sure you're in the right directory
cd flight-bot

# Install only requirements
pip3 install -r requirements.txt

# NOT: pip install .
# NOT: pip install src
```

### Bot not running?
```bash
# Check Python version (need 3.9+)
python3 --version

# Test configuration
python3 main.py --test-email

# Check logs
tail -f logs/flight-bot.log
```

### Systemd service not starting?
```bash
# Check status and errors
sudo systemctl status flight-bot

# View detailed logs
sudo journalctl -u flight-bot -n 50

# Common issues:
# - Wrong paths in service file
# - Wrong username
# - Python not found (use full path: /usr/bin/python3)
```

### Docker not working?
```bash
# Check if Docker is running
sudo systemctl status docker

# View container logs
docker logs flight-bot

# Rebuild if needed
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📞 Need More Help?

1. Check logs: `logs/flight-bot.log`
2. Run in test mode: `python3 main.py --test --once`
3. Check configuration: Review `config.yaml`
4. Test email: `python3 main.py --test-email`

---

**Remember**: Start simple! Try running it manually first (`python3 main.py --once`), then choose a deployment method once you know it works.
