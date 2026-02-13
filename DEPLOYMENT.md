# Deployment Guide

## Prerequisites

- Python 3.9+
- pip
- Virtual environment support
- (Optional) SLURM for HPC deployment
- (Optional) GPU for faster inference

## Installation

```bash
# 1. Clone repository
git clone https://github.com/phindagijimana/vecta.git
cd vecta

# 2. Install dependencies
./med install

# 3. Configure (optional)
# Edit config.py for custom settings
```

## Deployment Options

### Option 1: HPC with SLURM

```bash
# 1. Configure SLURM script
# Edit med42_service.slurm:
#   - Adjust partition, time, memory, GPU requirements
#   - Set environment variables

# 2. Submit job
./med slurm

# 3. Monitor
./med status
squeue -u $USER
```

### Option 2: Standalone Server

```bash
# 1. Start service
./med start

# 2. Verify
./med test
curl http://localhost:8081/health
```

### Option 3: Systemd Service

```bash
# 1. Create service file
sudo nano /etc/systemd/system/vectaai.service

# Content:
[Unit]
Description=Vecta AI Service
After=network.target

[Service]
Type=forking
User=<your-user>
WorkingDirectory=/path/to/vecta
ExecStart=/path/to/vecta/med start
ExecStop=/path/to/vecta/med stop
Restart=on-failure

[Install]
WantedBy=multi-user.target

# 2. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable vectaai
sudo systemctl start vectaai
```

## Access Methods

### Local Access
```
http://localhost:8081
```

### Remote Access via SSH Tunnel
```bash
# On local machine:
ssh -L 8082:remote-host:8081 user@remote-server

# Then access:
http://localhost:8082
```

### Reverse Proxy (nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Configuration

### config.py
```python
service_port = 8081
service_host = "0.0.0.0"
max_concurrent_users = 10
model_name = "m42-health/Llama3-Med42-8B"
```

### gunicorn_config.py
```python
workers = 1  # Adjust based on CPU/GPU
timeout = 300  # Increase for long operations
```

### Environment Variables
```bash
export SERVICE_PORT=8081
export SERVICE_HOST=0.0.0.0
export MAX_CONCURRENT_USERS=10
export MODEL_NAME="m42-health/Llama3-Med42-8B"
```

## Monitoring

```bash
# Service status
./med status

# View logs
./med logs --tail 100

# Follow logs
./med logs --follow

# Health check
./med test
curl http://localhost:8081/health
```

## Troubleshooting

### Service Won't Start
```bash
# Check dependencies
./med install

# Check logs
./med logs

# Verify port availability
ss -tlnp | grep 8081
```

### Model Loading Issues
```bash
# Check model cache
ls -la model_cache/

# Clear cache if needed
rm -rf model_cache/*

# Restart service
./med restart
```

### Performance Issues
- Increase `timeout` in gunicorn_config.py
- Reduce `max_concurrent_users` in config.py
- Use GPU: Set `device = "cuda"` in config.py
- Check system resources: `htop`, `nvidia-smi`

## Maintenance

```bash
# Stop service
./med stop

# Update code
git pull origin main
./med install  # Update dependencies

# Restart
./med start

# Verify
./med test
```

## Scaling

### Horizontal Scaling
- Run multiple instances on different ports
- Use load balancer (nginx, HAProxy)
- Configure health checks

### Vertical Scaling  
- Increase workers in gunicorn_config.py (CPU-bound)
- Allocate more memory to SLURM job
- Use GPU for faster inference

## Security Checklist

- [ ] Change default ports
- [ ] Enable HTTPS/SSL
- [ ] Restrict file upload types
- [ ] Set upload size limits
- [ ] Enable authentication (add layer)
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Regular security updates

## Backup

```bash
# Backup configuration
tar -czf vecta-config-$(date +%Y%m%d).tar.gz config.py gunicorn*.py

# Backup logs
tar -czf vecta-logs-$(date +%Y%m%d).tar.gz logs/
```

---

For issues, check logs: `./med logs`
