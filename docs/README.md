# Documentation

Local documentation files (not tracked in GitHub, see root for public docs).

## Files

- **`QUICK_START.md`**: Quick reference guide
  - Local and HPC deployment commands
  - Resource mode comparison
  - Common troubleshooting

- **`RESOURCE_MODES.md`**: Detailed resource guide
  - CPU vs GPU modes
  - Performance benchmarks
  - Resource allocation guidelines
  - Advanced configuration

- **`HPC_CLI_GUIDE.md`**: HPC deployment guide
  - SLURM job management
  - Module loading
  - Port forwarding
  - Troubleshooting

## Public Documentation

Main documentation (tracked in GitHub):
- `../README.md`: Project overview and quick start
- `../DEPLOYMENT.md`: Complete deployment guide

## Usage

These files are for local reference. They contain detailed information that complements the main documentation.

### Quick Reference
```bash
# View quick start
cat docs/QUICK_START.md

# View resource modes
cat docs/RESOURCE_MODES.md

# View HPC guide
cat docs/HPC_CLI_GUIDE.md
```

### Search Documentation
```bash
# Find deployment info
grep -r "deployment" docs/

# Find GPU info
grep -r "GPU" docs/
```

## Organization

- **Quick guides**: For fast reference during deployment
- **Detailed guides**: For in-depth understanding
- **Troubleshooting**: Common issues and solutions

## Note

These files are in `.gitignore` as they're intended for local use. The main `README.md` and `DEPLOYMENT.md` in the root directory are the canonical public documentation.
