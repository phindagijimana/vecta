# Start Vecta AI

## Quick Start

```bash
# Start service (auto-installs dependencies)
./vecta start
```

The CLI automatically checks and installs Flask, pandas, and numpy if needed.

## Access

- **Main App**: http://localhost:8085
- **Validator**: http://localhost:8085/validate

## Commands

```bash
./vecta start          # Start in background (port 8085)
./vecta start -f       # Start in foreground
./vecta start -p 8090  # Use specific port
./vecta status         # Check status
./vecta logs           # View logs
./vecta stop           # Stop service
./vecta restart        # Restart service
```

## Manual Installation (if auto-install fails)

```bash
pip3 install --user flask flask-cors pandas numpy

# Optional: for RAG system
pip3 install --user chromadb sentence-transformers
```

## Features Ready

- 50 few-shot examples across 10 conditions
- Clinical guidelines (ILAE, ICHD-3, AAN, AHA/ASA)
- 2-page system (Main App + Validator)
- Navy blue theme, no emojis
- 10% auto-sampling for validation
- 5 demo cases pre-loaded

## First Time Setup

```bash
# Clone repository
git clone <your-repo-url>
cd med42_service

# Make CLI executable
chmod +x vecta

# Start service
./vecta start

# Check status
./vecta status
```

## Troubleshooting

### Dependencies Not Installing

```bash
pip3 install --user flask flask-cors pandas numpy
./vecta start
```

### Port Already in Use

CLI auto-detects free port (8085-8150). Check logs:
```bash
./vecta logs
```

### Stop Not Working

```bash
# Force stop
kill -9 $(cat vecta_ai.pid | cut -d: -f1)
rm vecta_ai.pid
```

## Next Steps

1. Start service: `./vecta start`
2. Open Main App: http://localhost:8085
3. Try validator: http://localhost:8085/validate
4. Review 5 demo cases
5. Analyze medical text

## Documentation

- `README.md`: Overview and quick start
- `CLI_GUIDE.md`: Complete CLI reference
- `TWO_PAGE_SYSTEM_GUIDE.md`: System architecture
- `IMPLEMENTATION_COMPLETE.md`: Full implementation details
