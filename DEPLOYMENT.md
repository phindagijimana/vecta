# Deployment Guide - Vecta AI

## Quick Deployment

### Option 1: One-Command Setup (Recommended)

```bash
git clone https://github.com/phindagijimana/vecta.git
cd vecta
./vecta start
```

The CLI automatically checks and installs dependencies (Flask, pandas, numpy).

### Option 2: Manual Setup

```bash
# Clone repository
git clone https://github.com/phindagijimana/vecta.git
cd vecta

# Install dependencies
pip3 install --user flask flask-cors pandas numpy

# Optional: for RAG system
pip3 install --user chromadb sentence-transformers

# Start service
./vecta start
```

## Access URLs

After deployment:

- **Main App**: http://localhost:8085
- **Validator**: http://localhost:8085/validate

## CLI Management

### Basic Commands

```bash
./vecta start          # Start in background (port 8085)
./vecta start -f       # Start in foreground
./vecta start -p 8090  # Use specific port
./vecta stop           # Stop service
./vecta restart        # Restart service
./vecta status         # Check status
./vecta logs           # View logs
./vecta help           # Show help
```

### Port Configuration

Default port: **8085**

Auto-detection range: 8085-8150

Manual override:
```bash
./vecta start -p 8090
# OR
export SERVICE_PORT=8090
./vecta start
```

## System Requirements

### Minimum Requirements

- Python 3.8+
- 2GB RAM
- 1GB disk space

### Required Dependencies

- Flask 3.x
- Flask-CORS
- pandas
- numpy

### Optional Dependencies

For RAG system:
- chromadb
- sentence-transformers
- PyTorch 2.1+ (for AI model)

## Production Deployment

### Using Production WSGI Server

```bash
# Install gunicorn
pip3 install --user gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8085 app:app
```

### Using systemd Service

Create `/etc/systemd/system/vecta.service`:

```ini
[Unit]
Description=Vecta AI Medical Analysis Platform
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/vecta
ExecStart=/path/to/vecta/vecta start -f
ExecStop=/path/to/vecta/vecta stop
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable vecta
sudo systemctl start vecta
sudo systemctl status vecta
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8085;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8085

CMD ["python3", "app.py"]
```

Build and run:
```bash
docker build -t vecta-ai .
docker run -d -p 8085:8085 vecta-ai
```

## Environment Variables

Optional configuration:

```bash
export SERVICE_PORT=8085          # Default port
export LOG_LEVEL=INFO             # Logging level
export DATABASE_PATH=data/validation.db  # Database location
```

## Database Setup

The SQLite database is automatically initialized on first run:

```bash
# Manual initialization (if needed)
python3 init_validation_system.py
```

Database location: `data/validation.db`

Tables created:
- `ai_outputs` - AI-generated analyses
- `validations` - Neurologist feedback
- `neurologists` - User accounts

## Features Enabled

### Core Features

- 50 few-shot examples across 10 neurology conditions
- Clinical guidelines (ILAE, ICHD-3, AAN, AHA/ASA)
- Auto-sampling (10% of outputs for validation)
- 2-page system (Main App + Validator)
- SQLite validation tracking

### Optional Features

Enable RAG system:
```bash
pip3 install --user chromadb sentence-transformers
./vecta restart
```

Enable AI model (requires PyTorch 2.1+):
```bash
pip3 install --user torch>=2.1
./vecta restart
```

## Data Files

### Required Data

- `data/few_shot_examples.json` (224KB) - 50 clinical examples
- `data/guidelines/neurology_guidelines.json` (72KB) - Clinical guidelines

### Auto-Generated

- `data/validation.db` - Validation database
- `data/vector_db/` - ChromaDB storage (if RAG enabled)
- `logs/vecta_ai.log` - Application logs
- `vecta_ai.pid` - Process ID file

## Security Considerations

### Production Checklist

- [ ] Change default database credentials (if applicable)
- [ ] Enable HTTPS with SSL certificate
- [ ] Use gunicorn or uWSGI (not Flask development server)
- [ ] Set up firewall rules
- [ ] Configure CORS appropriately
- [ ] Use environment variables for secrets
- [ ] Regular backups of validation.db
- [ ] Monitor logs for security issues

### File Permissions

```bash
chmod 700 data/
chmod 600 data/validation.db
chmod 755 vecta
```

## Monitoring

### Check Logs

```bash
./vecta logs           # Recent logs
./vecta logs 100       # Last 100 lines
tail -f logs/vecta_ai.log  # Live logs
```

### Check Status

```bash
./vecta status         # Service status
ps aux | grep app.py   # Process details
netstat -tuln | grep 8085  # Port status
```

### Health Check Endpoint

```bash
curl http://localhost:8085/health
```

## Troubleshooting

### Service Won't Start

Check logs:
```bash
./vecta logs
```

Common issues:
- Port already in use (auto-detects alternative)
- Missing dependencies (auto-installs on start)
- PyTorch version (optional, for AI model)

### Port Already in Use

The CLI auto-detects and uses next available port (8085-8150).

Manually specify:
```bash
./vecta start -p 8090
```

### Dependencies Not Installing

Manual install:
```bash
pip3 install --user flask flask-cors pandas numpy
./vecta start
```

### Database Errors

Reinitialize database:
```bash
rm data/validation.db
python3 init_validation_system.py
./vecta restart
```

### Cannot Access from Browser

Try alternative URLs:
- http://localhost:8085
- http://127.0.0.1:8085
- http://YOUR_SERVER_IP:8085

Check firewall:
```bash
sudo firewall-cmd --add-port=8085/tcp --permanent
sudo firewall-cmd --reload
```

## Backup and Recovery

### Backup Important Files

```bash
# Backup validation data
cp data/validation.db data/validation.db.backup

# Backup entire data directory
tar -czf vecta-backup-$(date +%Y%m%d).tar.gz data/
```

### Restore from Backup

```bash
./vecta stop
cp data/validation.db.backup data/validation.db
./vecta start
```

## Scaling

### Horizontal Scaling

Use load balancer (nginx, HAProxy) with multiple instances:

```bash
# Instance 1
./vecta start -p 8085

# Instance 2
./vecta start -p 8086

# Instance 3
./vecta start -p 8087
```

### Database Optimization

For high traffic, consider:
- PostgreSQL instead of SQLite
- Redis for caching
- Separate database server

## Updates and Maintenance

### Update from GitHub

```bash
./vecta stop
git pull origin main
pip3 install --user -r requirements.txt
./vecta start
```

### Database Migrations

When schema changes, backup first:
```bash
cp data/validation.db data/validation.db.backup
# Run migrations if provided
./vecta start
```

## Performance Optimization

### Recommended Settings

For production:
- Use gunicorn with 4-8 workers
- Enable caching (Redis)
- Use CDN for static files
- Monitor with Prometheus/Grafana

### Resource Requirements by Load

- **Low** (<100 requests/day): 2GB RAM, 1 CPU
- **Medium** (<1000 requests/day): 4GB RAM, 2 CPU
- **High** (>1000 requests/day): 8GB RAM, 4 CPU

## Support and Maintenance

### Regular Tasks

- Check logs weekly: `./vecta logs`
- Backup database weekly
- Update dependencies monthly
- Monitor disk space
- Review validation data

### Getting Help

- GitHub Issues: https://github.com/phindagijimana/vecta/issues
- Check logs: `./vecta logs`
- Status check: `./vecta status`

## Implementation Details

### Architecture

```
CLI (vecta) → Flask App (app.py) → Routes
                ├── Main App (/)
                ├── Validator (/validate)
                └── API Endpoints
                     ├── Few-shot examples
                     ├── Clinical guidelines
                     └── RAG system (optional)
```

### Data Flow

1. User submits medical text
2. System detects condition
3. Retrieves few-shot examples
4. Injects clinical guidelines
5. RAG retrieves relevant context (if enabled)
6. AI generates analysis
7. 10% randomly sampled for validation
8. Stored in validation.db

### Port Detection Logic

1. Try port 8085
2. If in use, scan 8086-8150
3. Select first available port
4. Log selection
5. Create PID file with port

## Configuration Files

### requirements.txt

Core dependencies installed by CLI:
```
flask>=3.1.0
flask-cors>=6.0.0
pandas>=2.0.0
numpy>=1.24.0
```

Optional:
```
chromadb>=0.4.22
sentence-transformers>=2.2.2
torch>=2.1.0
```

### .gitignore

Already configured to exclude:
- `__pycache__/`
- `*.log`
- `vecta_ai.pid`
- `data/vector_db/`
- `*.db-journal`

## License

MIT License - See repository for details.

## Version

Current Version: 2.1
Last Updated: 2026-02-13
Status: Production Ready
