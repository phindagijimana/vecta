# Neurologist Validation System - Implementation Checklist

## Quick Reference

**Goal:** Build a validation system where neurologists review AI outputs and provide yes/no feedback + comments.

**Time:** 27-38 hours development  
**Complexity:** Medium  
**Result:** Gold-standard labeled dataset + continuous improvement

---

## Implementation Checklist

### Phase 1: Database Setup (2-3 hours)

- [ ] **Create SQLite database** (or use existing PostgreSQL)
  ```bash
  sqlite3 data/validation.db
  ```

- [ ] **Run SQL schema** (from NEUROLOGIST_VALIDATION_SYSTEM.md)
  - [ ] Create `ai_outputs` table
  - [ ] Create `validations` table
  - [ ] Create `neurologists` table
  - [ ] Create indexes

- [ ] **Test database connection**
  ```python
  python -c "import sqlite3; conn = sqlite3.connect('data/validation.db'); print('Connected')"
  ```

### Phase 2: Backend Routes (4-6 hours)

- [ ] **Create `routes/validation.py`**
  - [ ] Import dependencies (Flask, Flask-Login, etc.)
  - [ ] Create Blueprint
  - [ ] Implement routes:
    - [ ] `/validate` - Main validation page
    - [ ] `/api/next-case` - Get next case for review
    - [ ] `/api/submit-validation` - Submit validation
    - [ ] `/dashboard` - Analytics dashboard
    - [ ] `/login` - Neurologist login
    - [ ] `/logout` - Logout

- [ ] **Add helper functions**
  - [ ] `get_next_validation_case(neurologist)`
  - [ ] `save_validation(validation_data)`
  - [ ] `mark_output_validated(output_id)`
  - [ ] `get_neurologist_stats(neurologist_id)`

- [ ] **Register Blueprint in `app.py`**
  ```python
  from routes.validation import validation_bp
  app.register_blueprint(validation_bp, url_prefix='/validation')
  ```

### Phase 3: Frontend UI (6-8 hours)

- [ ] **Create templates folder** `templates/validation/`

- [ ] **Create `templates/validation/login.html`**
  - [ ] Email input
  - [ ] Password input
  - [ ] Login button
  - [ ] Error messages

- [ ] **Create `templates/validation/validation.html`**
  - [ ] Header with neurologist info
  - [ ] Progress indicator (X of Y cases)
  - [ ] Case display section
  - [ ] AI output display section
  - [ ] Yes/No/Skip buttons
  - [ ] Comment textarea
  - [ ] Optional detailed ratings checkboxes
  - [ ] Submit button
  - [ ] Timer (track review time)

- [ ] **Create `templates/validation/dashboard.html`**
  - [ ] Overall statistics
  - [ ] Agreement rate chart
  - [ ] Validations by condition
  - [ ] Top validators leaderboard
  - [ ] Recent activity

- [ ] **Add JavaScript**
  - [ ] AJAX for submitting validations
  - [ ] Auto-load next case after submit
  - [ ] Timer functionality
  - [ ] Keyboard shortcuts (Y/N keys)

- [ ] **Make mobile-responsive**
  - [ ] Test on mobile viewport
  - [ ] Collapsible sections
  - [ ] Touch-friendly buttons

### Phase 4: Authentication (3-4 hours)

- [ ] **Install Flask-Login**
  ```bash
  pip install flask-login
  ```

- [ ] **Set up Flask-Login**
  - [ ] Configure LoginManager in `app.py`
  - [ ] Create User class (Neurologist)
  - [ ] Implement user_loader
  - [ ] Add login_required decorators

- [ ] **Create neurologist registration**
  - [ ] Registration form (email, name, specialty, password)
  - [ ] Password hashing with bcrypt
  - [ ] Email verification (optional for Phase 1)
  - [ ] Admin approval workflow

- [ ] **Test authentication**
  - [ ] Create test neurologist account
  - [ ] Test login/logout
  - [ ] Test protected routes

### Phase 5: Random Sampling (2-3 hours)

- [ ] **Implement sampling algorithm**
  - [ ] `select_outputs_for_validation()` function
  - [ ] Stratified sampling by condition
  - [ ] Priority scoring
  - [ ] Daily quota limit

- [ ] **Set up scheduled task**
  - [ ] Install APScheduler: `pip install apscheduler`
  - [ ] Schedule daily selection (1 AM)
  - [ ] Log selection results

- [ ] **Test sampling**
  - [ ] Run manually first
  - [ ] Verify stratification
  - [ ] Check priority scores

### Phase 6: Integration with Main App (2-3 hours)

- [ ] **Modify `app.py` analyze() function**
  - [ ] Add `save_for_validation()` call
  - [ ] Implement 10% sampling rate
  - [ ] Save all required fields

- [ ] **Create `save_for_validation()` function**
  - [ ] Calculate priority
  - [ ] Insert into `ai_outputs` table
  - [ ] Handle errors gracefully

- [ ] **Test integration**
  - [ ] Generate several AI outputs
  - [ ] Verify they appear in validation queue
  - [ ] Check sampling rate (~10%)

### Phase 7: Analytics & Export (4-6 hours)

- [ ] **Implement analytics functions**
  - [ ] `aggregate_validations()` - Calculate agreement rates
  - [ ] `get_neurologist_stats()` - Per-neurologist metrics
  - [ ] `get_condition_stats()` - Per-condition metrics
  - [ ] `calculate_inter_rater_reliability()` - Cohen's kappa

- [ ] **Create export functionality**
  - [ ] `export_validated_dataset()` - Export to JSON
  - [ ] Filter by agreement threshold (≥80%)
  - [ ] Filter by minimum reviews (≥2)
  - [ ] Format for few-shot examples

- [ ] **Build dashboard visualizations**
  - [ ] Charts using Chart.js or Plotly
  - [ ] Real-time stats updates
  - [ ] Export buttons

### Phase 8: Testing (4-6 hours)

- [ ] **Unit tests**
  - [ ] Test database functions
  - [ ] Test sampling algorithm
  - [ ] Test validation submission
  - [ ] Test export functions

- [ ] **Integration tests**
  - [ ] Test full validation workflow
  - [ ] Test with multiple neurologists
  - [ ] Test edge cases (no cases, all validated, etc.)

- [ ] **User acceptance testing**
  - [ ] Test with 1-2 neurologists
  - [ ] Collect feedback on UI/UX
  - [ ] Fix usability issues

### Phase 9: Documentation & Training (2-3 hours)

- [ ] **Create user guide for neurologists**
  - [ ] How to log in
  - [ ] How to validate cases
  - [ ] What to include in comments
  - [ ] Best practices

- [ ] **Create admin guide**
  - [ ] How to add neurologists
  - [ ] How to monitor validation progress
  - [ ] How to export datasets
  - [ ] Troubleshooting

- [ ] **Record tutorial video** (optional)
  - [ ] Screen recording of validation process
  - [ ] 3-5 minute walkthrough

---

## Quick Start Commands

### 1. Setup Database
```bash
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/med42_service
python -c "
import sqlite3
conn = sqlite3.connect('data/validation.db')
# Run SQL from NEUROLOGIST_VALIDATION_SYSTEM.md
conn.close()
"
```

### 2. Install Dependencies
```bash
pip install flask-login apscheduler bcrypt
```

### 3. Create First Neurologist
```python
from werkzeug.security import generate_password_hash
import sqlite3

conn = sqlite3.connect('data/validation.db')
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO neurologists (id, email, name, specialty, password_hash, is_active, is_verified)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    'neuro001',
    'dr.smith@example.com',
    'Dr. John Smith',
    'epilepsy',
    generate_password_hash('temporary_password'),
    True,
    True
))

conn.commit()
conn.close()
```

### 4. Test Validation UI
```bash
python app.py
# Navigate to: http://localhost:8081/validation/login
# Login with: dr.smith@example.com / temporary_password
```

### 5. Run Sampling (Manual Test)
```python
python -c "
from routes.validation import select_outputs_for_validation
selected = select_outputs_for_validation(sample_rate=0.10, daily_limit=20)
print(f'Selected {selected} outputs for validation')
"
```

---

## Dependencies

### Python Packages
```bash
pip install flask
pip install flask-login
pip install apscheduler
pip install bcrypt
pip install werkzeug
```

### Optional (for advanced features)
```bash
pip install plotly  # For dashboard charts
pip install pandas  # For data analysis
pip install scikit-learn  # For inter-rater reliability
```

---

## File Structure

```
med42_service/
├── app.py                                    # Main app (add Blueprint registration)
├── routes/
│   └── validation.py                         # NEW - Validation routes
├── templates/
│   └── validation/
│       ├── login.html                        # NEW - Login page
│       ├── validation.html                   # NEW - Validation UI
│       └── dashboard.html                    # NEW - Analytics dashboard
├── static/
│   ├── css/
│   │   └── validation.css                    # NEW - Validation styles
│   └── js/
│       └── validation.js                     # NEW - Validation JavaScript
├── data/
│   ├── validation.db                         # NEW - Validation database
│   ├── few_shot_examples.json               # Existing
│   └── few_shot_examples_expanded.json      # Existing
├── NEUROLOGIST_VALIDATION_SYSTEM.md          # Detailed documentation
└── VALIDATION_IMPLEMENTATION_CHECKLIST.md    # This file
```

---

## Testing Checklist

### Manual Testing
- [ ] Can create neurologist account
- [ ] Can log in successfully
- [ ] See validation cases
- [ ] Can submit yes/no validation
- [ ] Can add comments
- [ ] See next case after submit
- [ ] Stats update correctly
- [ ] Can log out
- [ ] Dashboard shows correct metrics
- [ ] Export produces valid JSON

### Edge Cases
- [ ] No cases available (shows message)
- [ ] All cases validated (shows completion)
- [ ] Multiple neurologists review same case
- [ ] Invalid login credentials
- [ ] Session timeout
- [ ] Network errors during submit

---

## Deployment Checklist

### Before Production
- [ ] **Security**
  - [ ] Change default passwords
  - [ ] Enable HTTPS
  - [ ] Set secure session cookies
  - [ ] Add CSRF protection
  - [ ] Rate limiting on API endpoints

- [ ] **Performance**
  - [ ] Index database tables
  - [ ] Cache dashboard queries
  - [ ] Optimize sampling queries

- [ ] **Monitoring**
  - [ ] Add logging for validations
  - [ ] Set up error alerts
  - [ ] Track validation metrics

- [ ] **Backup**
  - [ ] Set up database backups
  - [ ] Export validated data regularly

---

## Success Criteria

After implementation, you should be able to:

[OK] Log in as a neurologist  
[OK] See a random AI output case  
[OK] Click Yes/No to validate  
[OK] Add comments about the case  
[OK] Submit and see the next case  
[OK] View validation statistics  
[OK] Export validated examples as JSON  
[OK] See ≥10% of AI outputs selected for validation  

---

## Timeline

| Phase | Time | Status |
|-------|------|--------|
| Database Setup | 2-3 hours | ⬜ Not Started |
| Backend Routes | 4-6 hours | ⬜ Not Started |
| Frontend UI | 6-8 hours | ⬜ Not Started |
| Authentication | 3-4 hours | ⬜ Not Started |
| Random Sampling | 2-3 hours | ⬜ Not Started |
| Integration | 2-3 hours | ⬜ Not Started |
| Analytics | 4-6 hours | ⬜ Not Started |
| Testing | 4-6 hours | ⬜ Not Started |
| Documentation | 2-3 hours | ⬜ Not Started |
| **Total** | **27-38 hours** | **⬜** |

---

## Support

**Questions during implementation?**
- Refer to `NEUROLOGIST_VALIDATION_SYSTEM.md` for detailed specs
- Database schema is fully documented
- UI mockups included
- Code examples provided for all major functions

**After implementation:**
- Test with 1-2 neurologists first
- Collect feedback and iterate
- Gradually scale to more validators

---

## Next Steps

1. **Review** `NEUROLOGIST_VALIDATION_SYSTEM.md` (complete documentation)
2. **Start** with Phase 1: Database Setup
3. **Build** incrementally, testing each phase
4. **Deploy** to staging first
5. **Onboard** first neurologists
6. **Iterate** based on feedback

**Estimated completion:** 4-5 weeks (part-time) or 1 week (full-time)

---

**Status:** Ready for implementation  
**Priority:** High (enables continuous improvement)  
**Complexity:** Medium  
**Value:** Very High (gold-standard dataset + expert validation)
