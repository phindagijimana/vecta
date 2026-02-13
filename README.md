# Vecta AI - Medical Analysis Platform

Production-ready medical AI analysis service for clinical data, documents, and medical datasets.

## Features

- Specialized Medical AI with clinical training
- Multiple analysis types: Diagnosis, Classification, Extraction, Summarization
- Specialty support: Cardiology, Neurology, Psychiatry, Emergency Medicine, Internal Medicine
- Multi-format processing: PDF, DOCX, Excel, CSV, TXT, JSON
- Tabular data analysis with AI-enhanced columns
- Production-ready: SLURM integration, monitoring, logging, CLI management

## Quick Start

### Installation

```bash
# Install dependencies
./med install
```

### Starting the Service

**On HPC Cluster (SLURM):**
```bash
./med slurm
```

**Local Development:**
```bash
./med start
```

### Check Status

```bash
./med status
```

## CLI Reference

```
Usage: med <command> [options]

Commands:
  install     Install dependencies
  slurm       Submit as SLURM job
  start       Start service locally
  stop        Stop service
  restart     Restart service
  status      Show status and connection info
  logs        Show logs (--tail N, --follow)
  test        Run health checks
  help        Show help

Options:
  --port <port>      Service port (default: 8081)
  --host <host>      Service host (default: 0.0.0.0)
  --no-color         Disable colored output
```

## Configuration

Edit `config.py`:

```python
# Service settings
service_port = 8081
service_host = "0.0.0.0"
max_concurrent_users = 10

# Model settings
model_name = "m42-health/Llama3-Med42-8B"

# File upload
max_content_length = 50 * 1024 * 1024  # 50MB
```

## API Endpoints

### GET /
Web interface with analysis templates

### GET /health
Service health check

```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu",
  "stats": {...}
}
```

### POST /analyze
Main analysis endpoint

**Parameters:**
- `prompt` (required): Analysis prompt
- `analysisType` (required): diagnosis|classification|extraction|custom  
- `specialty` (optional): cardiology|neurology|psychiatry|emergency|internal_medicine
- `directText` or `file`: Input data
- `userId` (optional): User identifier

**Response:**
```json
{
  "success": true,
  "analysis": "...",
  "execution_time": 12.5,
  "timestamp": "..."
}
```

## Deployment

### HPC/SLURM

1. Configure `med42_service.slurm`
2. Submit: `./med slurm`
3. Monitor: `./med status`

### Standalone Server

1. Install: `./med install`
2. Configure: Edit `config.py` and `gunicorn_config.py`
3. Start: `./med start`

### Docker (Optional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
```

## Monitoring

```bash
# View logs
./med logs --tail 50

# Follow logs
./med logs --follow

# Health check
./med test

# Service status
./med status
```

## Architecture

```
Vecta AI
├── app.py              # Flask application
├── med                 # CLI management tool
├── config.py           # Configuration
├── gunicorn*.py        # WSGI server config
├── requirements.txt    # Dependencies
├── services/           # Service modules
│   ├── med42_model.py  # Model loading & inference
│   ├── file_processor.py
│   └── prompt_engine.py
└── utils/              # Utility modules
```

## Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run Flask development server
python app.py

# Run tests
./run_all_tests.sh
```

## Performance Tuning

**Gunicorn Configuration:**
```python
workers = 1  # For GPU workloads
timeout = 300  # Increase for long analyses
```

**Model Optimization:**
- Use GPU: Set `device = "cuda"` in config
- Adjust batch size in model service
- Enable model caching

## Security

- Input validation and sanitization
- File type restrictions
- Request size limits
- PHI filtering (enable in config)
- Audit logging

## License

See LICENSE file

## Medical Disclaimer

This AI tool is for research and educational purposes only. All analyses must be reviewed by qualified medical professionals before any clinical use.

---

**Version:** 2.0  
**Model:** Med42-8B (m42-health/Llama3-Med42-8B)  
**Platform:** Vecta AI
