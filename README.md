# Vecta AI

Medical AI analysis service for clinical data and documents.

## Features

- Medical AI with multi-specialty support (cardiology, neurology, psychiatry, emergency, internal medicine)
- Analysis types: diagnosis, classification, extraction, summarization
- File formats: PDF, DOCX, Excel, CSV, TXT, JSON
- Production CLI and SLURM integration

## Quick Start

```bash
./med install    # Install dependencies
./med start      # Start locally
./med slurm      # Deploy to HPC
./med status     # Check status
```

## CLI

```bash
med install      # Install
med start/stop   # Control service
med slurm        # SLURM deployment
med status       # Status
med logs         # View logs
med test         # Health check
```

## Configuration

Edit `config.py`:

```python
service_port = 8081
model_name = "m42-health/Llama3-Med42-8B"
max_concurrent_users = 10
```

## API

- `GET /` - Web interface
- `GET /health` - Health check
- `POST /analyze` - Analysis endpoint

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment and configuration options.

## Disclaimer

For research and educational use only. Requires medical professional review before clinical use.
