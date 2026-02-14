# Vecta AI - Medical Analysis Platform

AI-powered medical analysis platform with expert validation system and clinical guidelines integration.

## Overview

Vecta AI is a comprehensive medical AI system with:
- 50 curated clinical examples across 10 medical conditions
- Clinical guidelines (ILAE, ICHD-3, AAN, AHA/ASA, MDS)
- Medical expert validation system for continuous improvement
- Dual CLI for local and HPC deployment

**Current Focus**: Neurology & Neuroscience (Phase 1 - expanding to all medical specialties)

## Features

- **Clinical Examples**: 50 curated cases covering epilepsy, Parkinson's, stroke, migraine, dementia, MS, neuropathy, myasthenia gravis, spinal cord disorders, and motor neuron disease
- **Clinical Guidelines**: ILAE 2025, ICHD-3, AAN, AHA/ASA, MDS criteria
- **Validation System**: Medical expert review with 10% auto-sampling
- **2-Page Interface**: Main analysis app + expert validator
- **RAG System**: Semantic search with ChromaDB (optional)
- **Dual CLI**: Local workstation and HPC cluster deployment

## Quick Start

### Local Deployment

```bash
git clone https://github.com/phindagijimana/vecta.git
cd vecta
./vecta start
```

Access at http://localhost:8085

### HPC Cluster Deployment

```bash
git clone https://github.com/phindagijimana/vecta.git
cd vecta
module load cuda python gcc
./vecta-hpc install
./vecta-hpc run
./vecta-hpc status  # Shows access instructions
```

## CLI Commands

### Local (vecta)

```bash
./vecta start          # Start service
./vecta status         # Check status
./vecta logs           # View logs
./vecta stop           # Stop service
./vecta restart        # Restart
```

### HPC (vecta-hpc)

```bash
./vecta-hpc install    # Setup (one-time)
./vecta-hpc run        # Submit job
./vecta-hpc status     # Check job
./vecta-hpc logs       # View logs
./vecta-hpc stop       # Cancel job
```

## Requirements

### Minimum
- Python 3.8+
- 2GB RAM
- Flask, pandas, numpy (auto-installed)

### Optional (for AI model)
- PyTorch 2.1+
- 16GB+ GPU VRAM
- CUDA 11.7+

## Architecture

```
Flask App (app.py)
├── Main App (/)
│   ├── 50 few-shot examples
│   ├── Clinical guidelines
│   ├── RAG system (optional)
│   └── Auto-sampling (10%)
│
└── Validator (/validate)
    ├── Case review interface
    ├── Statistics dashboard
    └── Validation tracking
```

## Data

- **Few-shot examples**: 50 medical cases (224KB)
- **Clinical guidelines**: ILAE, ICHD-3, AAN, AHA/ASA, MDS (72KB)
- **Validation database**: SQLite (auto-created)

## Documentation

See `DEPLOYMENT.md` for:
- Complete deployment guide
- GPU setup instructions
- HPC cluster configuration
- Docker deployment
- Performance optimization
- Troubleshooting

## Tech Stack

- Backend: Flask, Python 3
- Database: SQLite
- Vector DB: ChromaDB (optional)
- GPU: PyTorch with CUDA (optional)

## License

MIT

## Support

GitHub Issues: https://github.com/phindagijimana/vecta/issues
