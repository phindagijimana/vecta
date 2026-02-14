# Core System Modules

Core functionality and shared modules used across the application.

## Files

- **`database.py`**: Database setup and connection management
  - SQLite database for validation system
  - Context manager for safe DB operations
  - Schema initialization

- **`config.py`**: Application configuration
  - Environment variable management
  - Pydantic-based configuration
  - Type-safe settings

## Usage

```python
from core.database import get_db, init_db
from core.config import Med42Config

# Initialize database
init_db()

# Get database connection
with get_db() as db:
    results = db.execute("SELECT * FROM table")

# Load configuration
config = Med42Config()
```
