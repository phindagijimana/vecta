# Vecta AI - Medical Analysis Platform

Production-ready medical AI analysis service for clinical data and documents.

## Features

- Specialized medical AI with clinical training across multiple specialties
- Multiple analysis types: Diagnosis, Classification, Extraction, Summarization
- Multi-format processing: PDF, DOCX, Excel, CSV, TXT, JSON
- Tabular data analysis with AI-enhanced columns
- Production CLI for deployment and monitoring
- SLURM integration for HPC environments

## Quick Start

```bash
# Install
./med install

# Start (HPC)
./med slurm

# Start (Local)
./med start

# Check status
./med status
```

## CLI Commands

```bash
med install     # Install dependencies
med slurm       # Submit SLURM job
med start       # Start locally
med stop        # Stop service
med restart     # Restart service
med status      # Show status
med logs        # View logs (--tail N, --follow)
med test        # Health check
```

## Configuration

Edit `config.py`:

```python
service_port = 8081
service_host = "0.0.0.0"
max_concurrent_users = 10
model_name = "m42-health/Llama3-Med42-8B"
```

## API Endpoints

**GET /** - Web interface

**GET /health** - Health check
```json
{"status": "healthy", "model_loaded": true}
```

**POST /analyze** - Main endpoint
```json
{
  "prompt": "Analysis prompt",
  "analysisType": "diagnosis|classification|extraction|custom",
  "specialty": "cardiology|neurology|psychiatry|emergency|internal_medicine",
  "directText": "text" OR "file": file,
  "userId": "optional"
}
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment options.

**Quick Deploy:**
1. Configure `med42_service.slurm` or `config.py`
2. Run `./med slurm` (HPC) or `./med start` (local)
3. Monitor with `./med status`

## Monitoring

```bash
./med logs --tail 50   # View logs
./med test             # Health check
./med status           # Service info
```

## Security

- Input validation and sanitization
- File type and size restrictions
- Optional PHI filtering
- Audit logging

## Medical Disclaimer

This tool is for research and educational purposes only. All analyses must be reviewed by qualified medical professionals before clinical use.

---

**Version:** 2.0 | **Model:** Med42-8B | **Platform:** Vecta AI
