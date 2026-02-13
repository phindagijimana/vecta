# Vecta AI - Medical Analysis Platform

AI-powered medical text analysis platform with neurologist validation system.

## Features

- **50 Few-Shot Examples**: Curated clinical cases across 10 neurology conditions
- **Clinical Guidelines**: ILAE, ICHD-3, AAN, AHA/ASA guidelines integrated
- **RAG System**: Semantic search with ChromaDB (optional)
- **2-Page System**: Main analysis app + neurologist validator
- **CLI Management**: Start, stop, restart, status, logs
- **Smart Port Detection**: Auto-finds free port (8085-8150)

## Quick Start

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd med42_service

# Start service (auto-installs dependencies)
./vecta start
```

The CLI will automatically check and install required dependencies (Flask, pandas, numpy).

### Access

- **Main App**: http://localhost:8085
- **Validator**: http://localhost:8085/validate

## CLI Commands

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

## Manual Installation (Optional)

If auto-install doesn't work:

```bash
pip3 install --user flask flask-cors pandas numpy

# Optional: for RAG system
pip3 install --user chromadb sentence-transformers
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

- `CLI_GUIDE.md`: Complete CLI reference
- `TWO_PAGE_SYSTEM_GUIDE.md`: System architecture
- `IMPLEMENTATION_COMPLETE.md`: Implementation details
- `START_APP_NOW.md`: Detailed startup guide

## Development

### Run in Foreground

```bash
./vecta start -f
```

### Check Logs

```bash
./vecta logs 100
```

### Restart After Changes

```bash
./vecta restart
```

## Configuration

### Port Configuration

Default port: 8085

Override:
```bash
./vecta start -p 8090
# OR
export SERVICE_PORT=8090
./vecta start
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
- Demo data included (5 cases)

## Tech Stack

- **Backend**: Flask, Python 3
- **Database**: SQLite
- **Vector DB**: ChromaDB (optional)
- **Embeddings**: sentence-transformers (optional)
- **Data Processing**: pandas, numpy

## License

MIT

## Support

For issues or questions, please open a GitHub issue.

## Status

READY - All features implemented and tested. Auto-installs dependencies on first start.
