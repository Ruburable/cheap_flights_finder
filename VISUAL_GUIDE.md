# 🎨 Visual Deployment Guide

## Understanding Your Options

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT OPTIONS                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   RAILWAY    │    │   YOUR NAS   │    │    DOCKER    │    │ PYTHONANYWHERE│
│   (Cloud)    │    │  (systemd)   │    │ (Container)  │    │    (Cloud)    │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬────────┘
       │                   │                   │                   │
       │                   │                   │                   │
   ┌───▼────────────────────▼───────────────────▼───────────────────▼────┐
   │                  WHAT THEY ALL DO:                                   │
   │  • Check prices every 6 hours                                        │
   │  • Send email when deals found                                       │
   │  • Store price history                                               │
   │  • Run 24/7 without you doing anything                               │
   └──────────────────────────────────────────────────────────────────────┘
```

---

## Option 1: Railway (Cloud) - Beginner Friendly

```
YOUR COMPUTER              GITHUB              RAILWAY CLOUD
┌─────────┐               ┌─────────┐         ┌──────────────┐
│         │   git push    │         │ deploy  │              │
│  Code   │──────────────>│  Repo   │────────>│  Bot Running │──> Sends emails
│         │               │         │         │    24/7      │    to you
└─────────┘               └─────────┘         └──────────────┘
```

**What you do**:
1. Push code to GitHub (one time)
2. Connect Railway to GitHub (one time)
3. Forget about it!

**Pros**: Dead simple, no server needed
**Cost**: Free (with $5/month credit)

---

## Option 2: systemd (Your NAS/Server)

### What is systemd?

Think of systemd as a "program babysitter" that:
- Starts your bot when computer boots up
- Restarts it if it crashes
- Keeps logs of what happens
- Lets you control it with simple commands

### How It Works:

```
┌─────────────────────────────────────────────────────┐
│                  YOUR NAS/SERVER                     │
│                                                      │
│  ┌──────────────┐                                   │
│  │   systemd    │  <-- The "babysitter"             │
│  │ (Always On)  │                                   │
│  └──────┬───────┘                                   │
│         │                                            │
│         │ Starts & monitors                          │
│         │                                            │
│  ┌──────▼────────┐                                  │
│  │  Flight Bot   │  <-- Your bot                    │
│  │  main.py      │                                  │
│  └───────────────┘                                  │
│                                                      │
└─────────────────────────────────────────────────────┘
           │
           │ Sends emails when deals found
           ▼
      Your Inbox
```

### Setup Steps (Detailed):

#### Step 1: Edit the Service File

```bash
cd flight-bot/deployment
nano flight-bot.service
```

Change these 3 things:

```ini
# 1. Change YOUR_USERNAME to your actual username
User=YOUR_USERNAME              ← Change this

# 2. Change /path/to/ to where you put the bot
WorkingDirectory=/path/to/flight-bot    ← Change this

# 3. Change /path/to/ to where you put the bot
ExecStart=/usr/bin/python3 /path/to/flight-bot/main.py  ← Change this
```

**How to find your username**:
```bash
whoami
# Example output: john
# Then use: User=john
```

**How to find the path**:
```bash
pwd
# Example output: /home/john/flight-bot
# Then use: WorkingDirectory=/home/john/flight-bot
```

**How to find Python**:
```bash
which python3
# Example output: /usr/bin/python3
# Use this in ExecStart
```

#### Step 2: Copy to System

```bash
sudo cp flight-bot.service /etc/systemd/system/
```

This puts the file where systemd can find it.

#### Step 3: Tell systemd About It

```bash
# Let systemd know there's a new service
sudo systemctl daemon-reload

# Tell it to start on boot
sudo systemctl enable flight-bot

# Start it now
sudo systemctl start flight-bot
```

#### Step 4: Check It's Working

```bash
sudo systemctl status flight-bot
```

You should see:
```
● flight-bot.service - Flight Deal Bot
   Loaded: loaded
   Active: active (running)  ← Good!
```

### Common systemd Commands:

```bash
# Start the bot
sudo systemctl start flight-bot

# Stop the bot
sudo systemctl stop flight-bot

# Restart the bot (after config changes)
sudo systemctl restart flight-bot

# Check if it's running
sudo systemctl status flight-bot

# See recent logs
sudo journalctl -u flight-bot -n 50

# Watch logs live
sudo journalctl -u flight-bot -f

# Disable auto-start
sudo systemctl disable flight-bot
```

---

## Option 3: Docker (Container)

### What is Docker?

Think of Docker as creating a "complete package" that includes:
- Your bot code
- Python
- All dependencies
- Everything it needs

This package (called a "container") runs isolated from everything else.

### How It Works:

```
┌────────────────────────────────────────────────────┐
│              YOUR COMPUTER/NAS                      │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │           Docker Container                    │  │
│  │  ┌────────────────────────────────────────┐  │  │
│  │  │  • Python 3.11                         │  │  │
│  │  │  • Your bot code                       │  │  │
│  │  │  • All requirements                    │  │  │
│  │  │  • Running main.py                     │  │  │
│  │  └────────────────────────────────────────┘  │  │
│  │                                               │  │
│  │  Volume Mounts (shared with host):           │  │
│  │  • config.yaml  ←──┐                         │  │
│  │  • data/        ←──┼── Your files            │  │
│  │  • logs/        ←──┘                         │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

### Setup Steps:

#### Option A: Using Docker Compose (Easier)

```bash
# 1. Go to deployment folder
cd flight-bot/deployment

# 2. Make sure config.yaml exists in parent folder
cd ..
cp config.example.yaml config.yaml
nano config.yaml  # Edit your settings
cd deployment

# 3. Start the container
docker-compose up -d
```

That's it! The bot is now running in Docker.

#### Option B: Using Docker Commands (More Control)

```bash
# 1. Build the image
docker build -f deployment/Dockerfile -t flight-bot .

# 2. Run the container
docker run -d \
  --name flight-bot \
  --restart unless-stopped \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  flight-bot
```

**What this means**:
- `-d`: Run in background
- `--name flight-bot`: Call it "flight-bot"
- `--restart unless-stopped`: Auto-restart if crashes
- `-v`: Mount (share) folders between your computer and container

### Common Docker Commands:

```bash
# Check if running
docker ps

# View logs
docker logs flight-bot

# View logs live
docker logs -f flight-bot

# Stop the bot
docker stop flight-bot

# Start the bot
docker start flight-bot

# Restart the bot
docker restart flight-bot

# Remove the container (to rebuild)
docker rm -f flight-bot

# Using docker-compose:
docker-compose up -d      # Start
docker-compose down       # Stop
docker-compose logs -f    # View logs
docker-compose restart    # Restart
```

---

## Comparison Chart

```
┌─────────────────┬──────────┬──────────┬──────────┬───────────────┐
│    Feature      │ Railway  │ systemd  │  Docker  │ PythonAnywhere│
├─────────────────┼──────────┼──────────┼──────────┼───────────────┤
│ Difficulty      │ ⭐        │ ⭐⭐⭐     │ ⭐⭐⭐⭐    │ ⭐⭐            │
│ Cost            │ $0-5/mo  │ Free     │ Free     │ Free          │
│ Auto-restart    │ ✅        │ ✅        │ ✅        │ ⚠️             │
│ Needs Server    │ ❌        │ ✅        │ ✅        │ ❌             │
│ Setup Time      │ 10 min   │ 15 min   │ 20 min   │ 15 min        │
│ Isolation       │ ✅        │ ❌        │ ✅        │ ✅             │
│ Control         │ ⭐⭐       │ ⭐⭐⭐⭐⭐    │ ⭐⭐⭐⭐     │ ⭐⭐⭐           │
└─────────────────┴──────────┴──────────┴──────────┴───────────────┘
```

---

## My Recommendation

### Start Here:
1. **Test locally first**: `python main.py --once`
2. **If it works**, choose deployment:

### Choose Railway if:
- You don't have a server/NAS
- You want the easiest option
- You're okay spending $0-5/month

### Choose systemd if:
- You have a NAS or Linux server that's always on
- You want free hosting
- You're comfortable with command line

### Choose Docker if:
- You already use Docker for other things
- You want complete isolation
- You might move it between servers

### Choose PythonAnywhere if:
- You want free cloud hosting
- You don't mind using a web interface
- You don't need 24/7 (scheduled tasks only)

---

## Still Confused?

**START SIMPLE**:

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure:
   ```bash
   python configure.py
   ```

3. Test:
   ```bash
   python main.py --once
   ```

4. **If it works**, come back and choose a deployment method!

**Don't worry about Docker/systemd yet if you're not sure. Just get it working first!**
