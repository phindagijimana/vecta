# Vecta AI - Neurology & Neuroscience Analysis Platform

AI-powered neurological text analysis platform specialized in neurology and neuroscience with neurologist validation system.

## Current Focus: Neurology & Neuroscience

This platform is currently focused exclusively on neurological and neuroscience conditions. All features, examples, and guidelines are optimized for neurology practice.

## Neurology-Focused Features

- **50 Few-Shot Examples**: Curated neurological cases across 10 neurology conditions
  - Epilepsy, Parkinson's Disease, Stroke, Migraine, Dementia
  - Multiple Sclerosis, Peripheral Neuropathy, Myasthenia Gravis
  - Spinal Cord Disorders, Motor Neuron Disease
- **Clinical Guidelines**: Neurology-specific guidelines integrated
  - ILAE 2025 (Epilepsy Classification)
  - ICHD-3 (Headache/Migraine)
  - AAN Guidelines (Parkinson's, Dementia)
  - AHA/ASA Stroke Guidelines
  - MDS Criteria (Movement Disorders)
- **RAG System**: Semantic search with ChromaDB (optional)
- **2-Page System**: Main analysis app + neurologist validator
- **Dual CLI**: Local deployment + HPC cluster deployment
- **Smart Port Detection**: Auto-finds free port (8085-8150)

## Quick Start

### Local Deployment

```bash
# Clone repository
git clone https://github.com/phindagijimana/vecta.git
cd vecta

# Start service (auto-installs dependencies)
./vecta start
```

The CLI automatically checks and installs required dependencies (Flask, pandas, numpy).

### HPC Cluster Deployment

```bash
# Clone repository on HPC
git clone https://github.com/phindagijimana/vecta.git
cd vecta

# Load modules and install
module load cuda/12.2 python/3.9 gcc/11.2
./vecta-hpc install

# Submit job to SLURM
./vecta-hpc run

# Check status and access instructions
./vecta-hpc status
```

See `HPC_CLI_GUIDE.md` for complete HPC deployment guide.

## Access

- **Main App**: http://localhost:8085
- **Validator**: http://localhost:8085/validate

## CLI Commands

### Local Deployment (vecta)

```bash
./vecta start          # Start service (background)
./vecta start -f       # Start in foreground
./vecta start -p 8090  # Start on specific port
./vecta stop           # Stop service
./vecta restart        # Restart service
./vecta status         # Check status
./vecta logs           # View logs
./vecta help           # Show help
```

### HPC Deployment (vecta-hpc)

```bash
./vecta-hpc install    # Setup on HPC (one-time)
./vecta-hpc run        # Submit SLURM job
./vecta-hpc status     # Check job status
./vecta-hpc logs       # View job logs
./vecta-hpc logs -f    # Follow logs
./vecta-hpc stop       # Cancel job
./vecta-hpc list       # List your jobs
./vecta-hpc info       # HPC environment info
```

## Manual Installation (Optional)

If auto-install doesn't work:

```bash
pip3 install --user flask flask-cors pandas numpy

# Optional: for RAG system
pip3 install --user chromadb sentence-transformers

# Optional: for GPU support
pip3 install --user torch --index-url https://download.pytorch.org/whl/cu121
```

## Architecture

- **Flask App** (`app.py`): Main application with prompt engineering
- **Validation System** (`routes/validation.py`): Neurologist portal
- **Database** (`database.py`): SQLite for tracking validations
- **RAG System** (`utils/rag_system.py`): Semantic search (optional)
- **Few-Shot Loader** (`utils/few_shot_loader.py`): Example injection
- **Port Finder** (`utils/port_finder.py`): Smart port detection

## Data

- `data/few_shot_examples.json`: 50 clinical examples (224KB)
- `data/guidelines/neurology_guidelines.json`: Clinical guidelines (72KB)
- `data/validation.db`: Validation tracking database (auto-created)

## Documentation

- `README.md`: This file - overview and quick start
- `DEPLOYMENT.md`: General deployment guide
- `HPC_CLI_GUIDE.md`: HPC cluster deployment with SLURM
- `GPU_DEPLOYMENT_GUIDE.md`: GPU hardware setup and optimization
- `UI_UX_IMPROVEMENTS.md`: Interface enhancement recommendations

## Development

### Run in Foreground (Local)

```bash
./vecta start -f
```

### Submit HPC Job

```bash
# Default (1 GPU, 64G RAM, 24h)
./vecta-hpc run

# Custom resources
./vecta-hpc run --gpus 4 --memory 256G --time 72:00:00
```

### Check Logs

```bash
# Local
./vecta logs 100

# HPC
./vecta-hpc logs --follow
```

## Configuration

### Port Configuration

Default port: 8085

**Local override:**
```bash
./vecta start -p 8090
# OR
export SERVICE_PORT=8090
./vecta start
```

**HPC override:**
```bash
./vecta-hpc run --port 8090
```

### Database Location

`data/validation.db` (auto-created on first run)

## Prompt Engineering

### Phase 1: Few-Shot Examples
- 50 examples across 10 conditions
- Automatic condition detection
- Dynamic injection

### Phase 2: Clinical Guidelines
- ILAE 2025, ICHD-3, AAN, AHA/ASA
- Condition-specific retrieval
- Formatted for LLM

### Phase 3: RAG System (Optional)
- ChromaDB vector database
- Semantic search
- Dynamic context retrieval

## Validation System

- Auto-samples 10% of outputs
- Neurologist review interface
- Statistics dashboard
- Comment system
- Demo data included (10 cases)

## Tech Stack

- **Backend**: Flask, Python 3
- **Database**: SQLite
- **Vector DB**: ChromaDB (optional)
- **Embeddings**: sentence-transformers (optional)
- **Data Processing**: pandas, numpy
- **GPU**: PyTorch with CUDA (optional)

## Deployment Options

1. **Local GPU Workstation**: Use `vecta` CLI
2. **HPC Cluster (SLURM)**: Use `vecta-hpc` CLI
3. **Docker**: See `DEPLOYMENT.md`
4. **Cloud (AWS/Azure/GCP)**: See `GPU_DEPLOYMENT_GUIDE.md`

## License

MIT

## Support

For issues or questions, please open a GitHub issue at:
https://github.com/phindagijimana/vecta/issues

## Status

PRODUCTION READY - Dual CLI system with auto-install for local and HPC deployments.
