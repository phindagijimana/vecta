# Vecta AI - CLI Guide

## Command Line Interface

Vecta AI now includes a comprehensive CLI for managing the service.

---

## Quick Start

```bash
# Start the service
./vecta start

# Check status
./vecta status

# Stop the service
./vecta stop
```

---

## Installation

The CLI script is located at the root of the project:
```bash
/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/med42_service/vecta
```

**Make it executable (if not already):**
```bash
chmod +x vecta
```

**Optional - Add to PATH:**
```bash
# Add to ~/.bashrc or ~/.bash_profile
export PATH="$PATH:/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/med42_service"

# Then you can use 'vecta' from anywhere
vecta start
```

---

## Available Commands

### `vecta start`
Start the Vecta AI service.

**Usage:**
```bash
vecta start              # Start in background (default)
vecta start -f           # Start in foreground
vecta start -p 8090      # Start on specific port
```

**Features:**
- Starts in background by default
- Auto-detects free port (8085-8150 range)
- Creates PID file for tracking
- Logs to `logs/vecta_ai.log`
- Shows access URLs on success

**Default Port:** 8085  
**Port Range:** 8085-8150 (auto-finds free port)

**Example Output:**
```
═══════════════════════════════════════════════════════════════════
  Vecta AI - Medical Analysis Platform
  Command Line Interface
═══════════════════════════════════════════════════════════════════

Starting Vecta AI service...

[OK] Vecta AI started successfully in background
   PID: 12345
   Port: 8085

   Main App:   http://localhost:8085
   Validator:  http://localhost:8085/validate

   Logs: logs/vecta_ai.log

   Stop with: vecta stop
```

---

### `vecta stop`
Stop the running Vecta AI service.

**Usage:**
```bash
vecta stop
```

**Features:**
- Graceful shutdown (SIGTERM)
- Force kill after 10 seconds if needed
- Cleans up PID file
- Shows status messages

**Example Output:**
```
═══════════════════════════════════════════════════════════════════
  Vecta AI - Medical Analysis Platform
  Command Line Interface
═══════════════════════════════════════════════════════════════════

Stopping Vecta AI (PID: 12345, Port: 8085)...
[OK] Vecta AI stopped successfully
```

---

### `vecta restart`
Restart the Vecta AI service.

**Usage:**
```bash
vecta restart
```

**What it does:**
1. Stops the service (if running)
2. Waits 1 second
3. Starts the service in background

**Example Output:**
```
═══════════════════════════════════════════════════════════════════
  Vecta AI - Medical Analysis Platform
  Command Line Interface
═══════════════════════════════════════════════════════════════════

Restarting Vecta AI...

Stopping Vecta AI (PID: 12345, Port: 8085)...
[OK] Vecta AI stopped successfully

Starting Vecta AI service...
[OK] Vecta AI started successfully in background
   PID: 12346
   Port: 8085
```

---

### `vecta status`
Check the current status of Vecta AI service.

**Usage:**
```bash
vecta status
```

**Example Output (Running):**
```
═══════════════════════════════════════════════════════════════════
  Vecta AI - Medical Analysis Platform
  Command Line Interface
═══════════════════════════════════════════════════════════════════

Vecta AI Status
──────────────────────────────────────────────────────────────────
Status:  RUNNING
PID:     12345
Port:    8085

Access URLs:
  Main App:   http://localhost:8085
  Validator:  http://localhost:8085/validate

Stop with:    vecta stop
Restart with: vecta restart
```

**Example Output (Not Running):**
```
Vecta AI Status
──────────────────────────────────────────────────────────────────
Status:  NOT RUNNING

Start with: vecta start
```

---

### `vecta logs`
View recent application logs.

**Usage:**
```bash
vecta logs           # Show last 50 lines
vecta logs 100       # Show last 100 lines
```

**Example Output:**
```
═══════════════════════════════════════════════════════════════════
  Vecta AI - Medical Analysis Platform
  Command Line Interface
═══════════════════════════════════════════════════════════════════

Recent logs (last 50 lines):
──────────────────────────────────────────────────────────────────
2026-02-13 17:30:15 | INFO | vectaai | Starting Vecta AI service...
2026-02-13 17:30:15 | INFO | vectaai | Port 8085 is available
2026-02-13 17:30:16 | INFO | vectaai | [OK] Few-shot examples and guidelines loaded
2026-02-13 17:30:16 | INFO | vectaai | [OK] Validation routes registered
...

Full logs: logs/vecta_ai.log
```

---

### `vecta help`
Show help message with all available commands.

**Usage:**
```bash
vecta help
vecta -h
vecta --help
```

---

## Port Configuration

### Default Port: 8085

If port 8085 is available, it will be used automatically.

### Auto Port Detection

If port 8085 is in use, Vecta AI will **automatically find a free port** in the range 8085-8150.

**Example:**
```
Port 8085 is in use, searching for free port...
Found free port: 8089
Starting Vecta AI server on 0.0.0.0:8089
```

### Manual Port Override

**Option 1 - CLI Flag:**
```bash
vecta start -p 8090
```

**Option 2 - Environment Variable:**
```bash
export SERVICE_PORT=8090
vecta start
```

**Option 3 - Permanent Change:**
Edit `app.py` and change:
```python
default_port = int(os.environ.get("SERVICE_PORT", 8085))  # Change 8085
```

---

## PID File

The CLI uses a PID file to track the running process:

**Location:** `vecta_ai.pid`

**Format:** `PID:PORT` (e.g., `12345:8085`)

**Usage:**
- Created on start
- Used by stop/status/restart
- Cleaned up on stop

---

## Logs

**Location:** `logs/vecta_ai.log`

**Contents:**
- Startup messages
- Model loading status
- Request processing
- Errors and warnings
- Shutdown messages

**View logs:**
```bash
vecta logs           # Last 50 lines
vecta logs 100       # Last 100 lines
tail -f logs/vecta_ai.log  # Follow live
```

---

## Common Workflows

### Development Workflow
```bash
# Start in foreground (see output immediately)
vecta start -f

# Make changes to code
# Press Ctrl+C to stop

# Restart
vecta start -f
```

### Production Workflow
```bash
# Start in background
vecta start

# Check status
vecta status

# Monitor logs
vecta logs

# Restart after updates
vecta restart

# Stop when needed
vecta stop
```

### Debugging Workflow
```bash
# Check status
vecta status

# View logs
vecta logs 100

# Stop service
vecta stop

# Start in foreground to see errors
vecta start -f
```

---

## Troubleshooting

### Issue: "vecta: command not found"

**Solution:**
```bash
# Use with ./ prefix
./vecta start

# Or add to PATH
export PATH="$PATH:$(pwd)"
```

### Issue: "Permission denied"

**Solution:**
```bash
chmod +x vecta
./vecta start
```

### Issue: "Port already in use"

**Solution:**
Vecta AI will automatically find a free port (8085-8150).

Or specify a different port:
```bash
vecta start -p 8100
```

### Issue: "Flask not installed"

**Solution:**
```bash
pip3 install --user flask flask-cors pandas numpy
```

### Issue: Process won't stop

**Solution:**
```bash
# Get PID
cat vecta_ai.pid

# Force kill
kill -9 <PID>

# Clean up
rm vecta_ai.pid
```

---

## Advanced Usage

### Start with Custom Configuration
```bash
# Custom port and host
export SERVICE_PORT=8090
export SERVICE_HOST=127.0.0.1
vecta start
```

### Monitor in Real-Time
```bash
# Start service
vecta start

# Follow logs
tail -f logs/vecta_ai.log
```

### Health Check
```bash
# Check if service is responding
curl http://localhost:8085/health

# Or use the status command
vecta status
```

---

## CLI Features Summary

[OK] **Easy Management**
- Start/stop/restart with single command
- Background mode by default
- Foreground mode available

[OK] **Smart Port Detection**
- Default: 8085
- Auto-finds free port (8085-8150)
- Manual override available

[OK] **Process Tracking**
- PID file for status tracking
- Graceful shutdown
- Force kill fallback

[OK] **Logging**
- Comprehensive logs
- View recent logs via CLI
- Full log file available

[OK] **Status Monitoring**
- Check if running
- Show PID and port
- Display access URLs

[OK] **User-Friendly**
- Clear status messages
- Helpful error messages
- Examples in help

---

## Quick Reference Card

```bash
# Start (background, default port 8085)
./vecta start

# Start in foreground
./vecta start -f

# Start on custom port
./vecta start -p 8090

# Stop
./vecta stop

# Restart
./vecta restart

# Status
./vecta status

# Logs
./vecta logs

# Help
./vecta help
```

---

## File Locations

- **CLI Script:** `vecta`
- **PID File:** `vecta_ai.pid`
- **Logs:** `logs/vecta_ai.log`
- **Database:** `data/validation.db`
- **App:** `app.py`

---

## Summary

[OK] **Comprehensive CLI** with start/stop/restart/status/logs
[OK] **Smart port detection** (8085-8150 auto-find)
[OK] **Background mode** (default, run as daemon)
[OK] **Foreground mode** (for development)
[OK] **PID tracking** (know what's running)
[OK] **Log viewing** (see what happened)
[OK] **Graceful shutdown** (clean stop)

**Your app now has professional CLI management!**

---

**Created:** 2026-02-13
**Version:** 2.1-with-cli
**Status:** Ready to use
