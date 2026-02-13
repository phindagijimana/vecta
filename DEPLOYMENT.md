# Deployment Guide

## Prerequisites

- Python 3.9+
- pip and virtual environment support
- (Optional) SLURM for HPC
- (Optional) GPU for faster inference

## Installation

```bash
git clone https://github.com/phindagijimana/vecta.git
cd vecta
./med install
```

## Deployment Options

### HPC with SLURM

```bash
# 1. Edit med42_service.slurm (partition, time, memory, GPU)
# 2. Submit job
./med slurm

# 3. Monitor
./med status
squeue -u $USER
```

### Standalone Server

```bash
./med start
./med test
```

### Systemd Service

```bash
# Create /etc/systemd/system/vectaai.service
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

# Enable
sudo systemctl daemon-reload
sudo systemctl enable vectaai
sudo systemctl start vectaai
```

## Access

**Local:** `http://localhost:8081`

**SSH Tunnel:**
```bash
ssh -L 8082:remote-host:8081 user@server
# Access: http://localhost:8082
```

**Nginx Reverse Proxy:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
    }
}
```

## Configuration

**config.py**
```python
service_port = 8081
service_host = "0.0.0.0"
max_concurrent_users = 10
model_name = "m42-health/Llama3-Med42-8B"
```

**gunicorn_config.py**
```python
workers = 1
timeout = 300
```

**Environment Variables**
```bash
export SERVICE_PORT=8081
export MAX_CONCURRENT_USERS=10
export MODEL_NAME="m42-health/Llama3-Med42-8B"
```

## Monitoring

```bash
./med status              # Service status
./med logs --tail 100     # View logs
./med logs --follow       # Stream logs
./med test                # Health check
curl http://localhost:8081/health
```

## Troubleshooting

**Service won't start:**
```bash
./med install
./med logs
ss -tlnp | grep 8081
```

**Model loading issues:**
```bash
ls -la model_cache/
rm -rf model_cache/*
./med restart
```

**Performance issues:**
- Increase `timeout` in gunicorn_config.py
- Reduce `max_concurrent_users` in config.py
- Use GPU: Set `device = "cuda"` in config.py

## Maintenance

```bash
./med stop
git pull origin main
./med install
./med start
./med test
```

## Security

- Change default ports
- Enable HTTPS/SSL
- Restrict file types and sizes
- Add authentication layer
- Configure firewall
- Enable audit logging
- Regular updates

---

For issues: `./med logs`
