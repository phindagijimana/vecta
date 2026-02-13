# Vecta AI

AI-powered medical analysis service for clinical data and documents.

**Phase 1: Neurology & Neuroscience Focus**

## Features

- Specialized neurological analysis (epilepsy, movement disorders, cognitive assessment, stroke, neurodegenerative diseases)
- Analysis types: diagnosis, classification, extraction, summarization
- File formats: PDF, DOCX, Excel, CSV, TXT, JSON
- Production CLI and SLURM integration

**Note:** Currently focused on neurology/neuroscience. Other specialties planned for future releases (see Roadmap below).

## Quick Start

```bash
git clone https://github.com/phindagijimana/vecta.git
cd vecta
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
- `POST /analyze` - Analysis endpoint (parameters: prompt, analysisType, specialty, directText/file)

## Roadmap

**Phase 1 (Current):** Neurology & Neuroscience  
**Phase 2 (Future):** Cardiology, Psychiatry, Emergency Medicine, Internal Medicine

Code structure supports future expansion - additional specialties will be activated based on validation and demand.

## Documentation

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options and configuration details.

## Disclaimer

For research and educational use only. Requires medical professional review before clinical use.
