# Self-Improvement Learning System

Automatic learning system that extracts validated cases and improves AI performance over time.

## Files

- **`learning_engine.py`**: Core learning engine
  - Extracts high-quality validated cases from database
  - Converts to few-shot examples
  - Tracks learning metrics and history
  - Updates knowledge base automatically

- **`auto_learn_scheduler.py`**: Automated learning scheduler
  - Scheduled learning cycles (time-based)
  - Threshold-based learning (validation count)
  - One-time learning checks

## Usage

### Manual Learning Cycle
```bash
python3 -m learning.learning_engine
```

### Check Metrics Only
```bash
python3 -m learning.learning_engine --metrics
```

### Automated Learning
```bash
# Check once and learn if needed
python3 -m learning.auto_learn_scheduler check

# Run every 60 minutes
python3 -m learning.auto_learn_scheduler scheduled 60

# Learn after every 5 validations
python3 -m learning.auto_learn_scheduler threshold 5
```

### From Python
```python
from learning.learning_engine import LearningEngine

engine = LearningEngine()
result = engine.run_learning_cycle()
metrics = engine.calculate_improvement_metrics()
```

## Features

- Automatic extraction of expert-validated cases
- Real-time knowledge base updates
- Learning metrics and history tracking
- Agreement rate monitoring
- Component accuracy analysis

## See Also

- `docs/SELF_IMPROVEMENT.md` - Detailed documentation
- `/learning` endpoint - Web dashboard
