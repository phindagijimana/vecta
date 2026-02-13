# Neurologist Validation System - Design Documentation

## Overview

A web-based validation system where certified neurologists can review and validate AI-generated outputs, providing expert feedback to continuously improve Vecta AI's accuracy and create high-quality labeled datasets.

## System Goals

1. **Collect Expert Validations**: Get yes/no ratings + comments from neurologists
2. **Build Gold-Standard Dataset**: Create validated examples for few-shot learning
3. **Continuous Improvement**: Identify errors and improve prompt engineering
4. **Quality Metrics**: Track AI accuracy against expert opinions
5. **Feedback Loop**: Use validations to refine model outputs

## Architecture

```
┌─────────────────┐
│  Vecta AI Core  │
│   (app.py)      │
└────────┬────────┘
         │
         ↓ Saves outputs
┌─────────────────────────┐
│  Validation Queue       │
│  (SQLite/PostgreSQL)    │
└────────┬────────────────┘
         │
         ↓ Randomly selects
┌─────────────────────────┐
│  Validation UI          │
│  (Flask route /validate)│
└────────┬────────────────┘
         │
         ↓ Neurologist reviews
┌─────────────────────────┐
│  Validated Dataset      │
│  (JSON + Database)      │
└─────────────────────────┘
         │
         ↓ Feeds back to
┌─────────────────────────┐
│  Few-Shot Examples      │
│  (Continuous improvement)│
└─────────────────────────┘
```

## Database Schema

### Table: `ai_outputs`
Stores all AI-generated outputs for potential validation.

```sql
CREATE TABLE ai_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    input_text TEXT NOT NULL,
    input_type VARCHAR(50),  -- 'classification', 'diagnosis', 'summary', etc.
    condition VARCHAR(100),  -- 'epilepsy', 'parkinsons', 'stroke', etc.
    specialty VARCHAR(50) DEFAULT 'neurology',
    
    -- AI Output (structured)
    ai_classification TEXT,
    ai_confidence TEXT,
    ai_evidence TEXT,
    ai_medication_analysis TEXT,
    ai_full_response TEXT,
    
    -- Metadata
    model_version VARCHAR(50),
    prompt_version VARCHAR(50),
    processing_time_ms INTEGER,
    
    -- Validation status
    validation_status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'in_review', 'validated', 'skipped'
    validation_priority INTEGER DEFAULT 1,  -- 1-5, higher = more important
    
    -- Random sampling
    selected_for_validation BOOLEAN DEFAULT FALSE,
    selection_date DATETIME,
    
    -- Session info (optional)
    session_id VARCHAR(100),
    user_context TEXT
);

CREATE INDEX idx_validation_status ON ai_outputs(validation_status);
CREATE INDEX idx_selected_validation ON ai_outputs(selected_for_validation);
CREATE INDEX idx_condition ON ai_outputs(condition);
```

### Table: `validations`
Stores neurologist validations and feedback.

```sql
CREATE TABLE validations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    output_id INTEGER NOT NULL,
    
    -- Neurologist info
    neurologist_id VARCHAR(100) NOT NULL,
    neurologist_name VARCHAR(200),
    neurologist_specialty VARCHAR(100),
    certification_level VARCHAR(50),  -- 'resident', 'attending', 'subspecialist'
    
    -- Validation
    validation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_correct BOOLEAN,  -- True = agree, False = disagree
    confidence_level VARCHAR(20),  -- 'low', 'medium', 'high'
    
    -- Detailed ratings (optional)
    classification_correct BOOLEAN,
    confidence_appropriate BOOLEAN,
    evidence_accurate BOOLEAN,
    medication_appropriate BOOLEAN,
    
    -- Feedback
    comments TEXT,
    preferred_classification TEXT,
    preferred_confidence TEXT,
    preferred_evidence TEXT,
    preferred_medication TEXT,
    
    -- Teaching points
    clinical_pearls TEXT,
    common_pitfalls TEXT,
    
    -- Time tracking
    review_time_seconds INTEGER,
    
    FOREIGN KEY (output_id) REFERENCES ai_outputs(id)
);

CREATE INDEX idx_neurologist ON validations(neurologist_id);
CREATE INDEX idx_output_id ON validations(output_id);
CREATE INDEX idx_is_correct ON validations(is_correct);
```

### Table: `neurologists`
Manages neurologist accounts and credentials.

```sql
CREATE TABLE neurologists (
    id VARCHAR(100) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    
    -- Credentials
    specialty VARCHAR(100),  -- 'general_neurology', 'epilepsy', 'movement_disorders', etc.
    subspecialties TEXT,  -- JSON array of subspecialties
    certification_level VARCHAR(50),
    institution VARCHAR(255),
    years_experience INTEGER,
    
    -- Authentication
    password_hash VARCHAR(255),  -- Use bcrypt
    api_token VARCHAR(255),  -- For authentication
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Stats
    total_validations INTEGER DEFAULT 0,
    agreement_rate FLOAT,  -- % agreement with other neurologists
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    
    -- Preferences
    preferred_conditions TEXT,  -- JSON array
    validation_quota_per_session INTEGER DEFAULT 20
);

CREATE INDEX idx_email ON neurologists(email);
CREATE INDEX idx_specialty ON neurologists(specialty);
```

## Validation UI Design

### Page Layout: `/validate`

```
┌─────────────────────────────────────────────────────────────┐
│  Vecta AI - Neurologist Validation Portal                   │
│  👤 Dr. Smith (Epilepsy) | Validated Today: 12/20 | Logout │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Review #1 of 20 - Epilepsy Classification                  │
│  ─────────────────────────────────────────────────────      │
│                                                               │
│   PATIENT CASE:                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 32-year-old female with 2-year history of episodes  │   │
│  │ of brief staring spells lasting 10-15 seconds. EEG  │   │
│  │ shows 3Hz spike-wave pattern. No loss of posture.   │   │
│  │ Family history of epilepsy.                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  🤖 VECTA AI ANALYSIS:                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Classification: Generalized absence epilepsy with │   │
│  │   characteristic 3Hz spike-wave pattern             │   │
│  │                                                      │   │
│  │ • Clinical Confidence: High based on classic EEG    │   │
│  │   findings and clinical semiology                   │   │
│  │                                                      │   │
│  │ • Evidence: 3Hz spike-wave on EEG, brief awareness  │   │
│  │   loss, typical age, family history                 │   │
│  │                                                      │   │
│  │ • Medication Analysis: First-line: Ethosuximide or  │   │
│  │   valproate. Avoid carbamazepine (may worsen).      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  [OK] VALIDATION:                                              │
│                                                               │
│  Do you agree with this AI analysis?                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────────┐                │
│  │ ✓ Yes   │  │ ✗ No    │  │ ⊘ Skip      │                │
│  └─────────┘  └─────────┘  └─────────────┘                │
│                                                               │
│  Your Confidence: [ High ▼ ]                                │
│                                                               │
│  💬 Comments / Preferred Answer (optional):                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [Text area for neurologist feedback]                │   │
│  │                                                      │   │
│  │ Placeholder: "e.g., Classification correct, but     │   │
│  │ would add consideration for juvenile myoclonic      │   │
│  │ epilepsy given age and family history..."           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  📋 Detailed Ratings (optional):                            │
│  Classification correct? [✓] Yes [ ] No [ ] Partial         │
│  Confidence appropriate? [✓] Yes [ ] No                     │
│  Evidence accurate?      [✓] Yes [ ] No                     │
│  Medication appropriate? [✓] Yes [ ] No                     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Submit       │  │ Next Case    │                        │
│  └──────────────┘  └──────────────┘                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Mobile-Friendly Version

```
┌─────────────────────────┐
│ Vecta AI Validation     │
│ Dr. Smith | 12/20       │
├─────────────────────────┤
│                         │
│ Review 1/20             │
│ Epilepsy Case           │
│                         │
│  CASE:                │
│ 32F, staring spells,    │
│ 3Hz spike-wave...       │
│ [Expand ▼]              │
│                         │
│ 🤖 AI ANALYSIS:         │
│ Classification: GAE...  │
│ Confidence: High...     │
│ [Expand ▼]              │
│                         │
│ [OK] AGREE?               │
│ [Yes] [No] [Skip]       │
│                         │
│ 💬 Comments:            │
│ [____________]          │
│                         │
│ [Submit & Next]         │
│                         │
└─────────────────────────┘
```

## Flask Implementation (Backend)

### File: `routes/validation.py`

```python
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from datetime import datetime
import random

validation_bp = Blueprint('validation', __name__)

@validation_bp.route('/validate')
@login_required  # Requires neurologist login
def validation_home():
    """Main validation interface"""
    neurologist = current_user
    
    # Get next case for validation
    next_case = get_next_validation_case(neurologist)
    
    # Get neurologist stats
    stats = get_neurologist_stats(neurologist.id)
    
    return render_template('validation.html', 
                         case=next_case,
                         stats=stats,
                         neurologist=neurologist)

@validation_bp.route('/api/next-case', methods=['GET'])
@login_required
def get_next_case():
    """API endpoint to get next validation case"""
    neurologist = current_user
    case = get_next_validation_case(neurologist)
    
    if not case:
        return jsonify({'status': 'complete', 'message': 'No more cases for today'})
    
    return jsonify({
        'status': 'success',
        'case': {
            'id': case['id'],
            'input_text': case['input_text'],
            'condition': case['condition'],
            'ai_output': {
                'classification': case['ai_classification'],
                'confidence': case['ai_confidence'],
                'evidence': case['ai_evidence'],
                'medication': case['ai_medication_analysis']
            }
        }
    })

@validation_bp.route('/api/submit-validation', methods=['POST'])
@login_required
def submit_validation():
    """Submit a validation"""
    data = request.json
    neurologist = current_user
    
    validation = {
        'output_id': data['case_id'],
        'neurologist_id': neurologist.id,
        'neurologist_name': neurologist.name,
        'neurologist_specialty': neurologist.specialty,
        'certification_level': neurologist.certification_level,
        'is_correct': data['is_correct'],
        'confidence_level': data.get('confidence_level', 'medium'),
        'comments': data.get('comments', ''),
        'preferred_classification': data.get('preferred_classification'),
        'preferred_confidence': data.get('preferred_confidence'),
        'preferred_evidence': data.get('preferred_evidence'),
        'preferred_medication': data.get('preferred_medication'),
        'classification_correct': data.get('classification_correct'),
        'confidence_appropriate': data.get('confidence_appropriate'),
        'evidence_accurate': data.get('evidence_accurate'),
        'medication_appropriate': data.get('medication_appropriate'),
        'review_time_seconds': data.get('review_time_seconds', 0)
    }
    
    # Save to database
    save_validation(validation)
    
    # Update ai_outputs status
    mark_output_validated(data['case_id'])
    
    # Update neurologist stats
    update_neurologist_stats(neurologist.id)
    
    return jsonify({'status': 'success', 'message': 'Validation saved'})

def get_next_validation_case(neurologist):
    """Get next case for validation based on neurologist specialty"""
    from database import get_db
    
    db = get_db()
    
    # Priority: 1) Neurologist's specialty, 2) Random unvalidated cases
    query = """
        SELECT * FROM ai_outputs 
        WHERE validation_status = 'pending'
        AND selected_for_validation = TRUE
        AND (condition = ? OR condition IS NULL)
        ORDER BY validation_priority DESC, RANDOM()
        LIMIT 1
    """
    
    case = db.execute(query, (neurologist.specialty,)).fetchone()
    
    if not case:
        # No specialty-specific cases, get any case
        query = """
            SELECT * FROM ai_outputs 
            WHERE validation_status = 'pending'
            AND selected_for_validation = TRUE
            ORDER BY validation_priority DESC, RANDOM()
            LIMIT 1
        """
        case = db.execute(query).fetchone()
    
    return case

def save_validation(validation):
    """Save validation to database"""
    from database import get_db
    
    db = get_db()
    db.execute("""
        INSERT INTO validations (
            output_id, neurologist_id, neurologist_name, neurologist_specialty,
            certification_level, is_correct, confidence_level, comments,
            preferred_classification, preferred_confidence, preferred_evidence,
            preferred_medication, classification_correct, confidence_appropriate,
            evidence_accurate, medication_appropriate, review_time_seconds
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        validation['output_id'],
        validation['neurologist_id'],
        validation['neurologist_name'],
        validation['neurologist_specialty'],
        validation['certification_level'],
        validation['is_correct'],
        validation['confidence_level'],
        validation['comments'],
        validation['preferred_classification'],
        validation['preferred_confidence'],
        validation['preferred_evidence'],
        validation['preferred_medication'],
        validation['classification_correct'],
        validation['confidence_appropriate'],
        validation['evidence_accurate'],
        validation['medication_appropriate'],
        validation['review_time_seconds']
    ))
    db.commit()

def mark_output_validated(output_id):
    """Mark output as validated"""
    from database import get_db
    
    db = get_db()
    db.execute("""
        UPDATE ai_outputs 
        SET validation_status = 'validated'
        WHERE id = ?
    """, (output_id,))
    db.commit()
```

## Random Selection Strategy

### Sampling Algorithm

```python
def select_outputs_for_validation(sample_rate=0.10, daily_limit=100):
    """
    Randomly select AI outputs for validation
    
    Args:
        sample_rate: Percentage of outputs to validate (0.10 = 10%)
        daily_limit: Maximum outputs to select per day
    """
    from database import get_db
    import random
    
    db = get_db()
    
    # Get unvalidated outputs from today
    today_outputs = db.execute("""
        SELECT id, condition, validation_priority 
        FROM ai_outputs 
        WHERE DATE(timestamp) = DATE('now')
        AND validation_status = 'pending'
        AND selected_for_validation = FALSE
    """).fetchall()
    
    # Stratified sampling by condition
    selected = stratified_sample(today_outputs, sample_rate)
    
    # Limit to daily quota
    selected = selected[:daily_limit]
    
    # Mark as selected
    for output_id in selected:
        db.execute("""
            UPDATE ai_outputs 
            SET selected_for_validation = TRUE,
                selection_date = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (output_id,))
    
    db.commit()
    
    return len(selected)

def stratified_sample(outputs, sample_rate):
    """
    Stratified sampling to ensure diversity across conditions
    """
    from collections import defaultdict
    import random
    
    # Group by condition
    by_condition = defaultdict(list)
    for output in outputs:
        by_condition[output['condition']].append(output['id'])
    
    # Sample from each condition
    selected = []
    for condition, ids in by_condition.items():
        sample_size = max(1, int(len(ids) * sample_rate))
        selected.extend(random.sample(ids, min(sample_size, len(ids))))
    
    return selected
```

### Priority Scoring

```python
def calculate_validation_priority(output):
    """
    Calculate priority score for validation
    Higher score = higher priority
    """
    priority = 1  # Base priority
    
    # Priority factors:
    
    # 1. Low AI confidence
    if 'low' in output['ai_confidence'].lower():
        priority += 2
    
    # 2. Complex cases (long input)
    if len(output['input_text']) > 500:
        priority += 1
    
    # 3. Rare conditions
    rare_conditions = ['myasthenia_gravis', 'motor_neuron_disease', 'spinal_cord']
    if output['condition'] in rare_conditions:
        priority += 2
    
    # 4. Emergency cases
    emergency_keywords = ['status epilepticus', 'crisis', 'acute', 'emergency']
    if any(kw in output['input_text'].lower() for kw in emergency_keywords):
        priority += 3
    
    # 5. Novel presentations
    if output.get('is_novel_presentation'):
        priority += 2
    
    return min(priority, 5)  # Cap at 5
```

## Validation Workflow

### Step-by-Step Process

1. **Output Capture (Automatic)**
   ```python
   # In app.py, after generating AI response
   def save_for_validation(input_text, ai_output, metadata):
       db = get_db()
       priority = calculate_validation_priority({
           'input_text': input_text,
           'ai_confidence': ai_output['confidence'],
           'condition': metadata['condition']
       })
       
       db.execute("""
           INSERT INTO ai_outputs (
               input_text, input_type, condition, specialty,
               ai_classification, ai_confidence, ai_evidence,
               ai_medication_analysis, ai_full_response,
               model_version, validation_priority
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
       """, (
           input_text, metadata['type'], metadata['condition'], 'neurology',
           ai_output['classification'], ai_output['confidence'],
           ai_output['evidence'], ai_output['medication'],
           ai_output['full_response'], '2.0', priority
       ))
       db.commit()
   ```

2. **Random Selection (Daily Cron Job)**
   ```python
   # Schedule with cron or APScheduler
   from apscheduler.schedulers.background import BackgroundScheduler
   
   scheduler = BackgroundScheduler()
   scheduler.add_job(
       func=select_outputs_for_validation,
       trigger="cron",
       hour=1,  # Run at 1 AM daily
       args=[0.10, 100]  # 10% sample rate, max 100/day
   )
   scheduler.start()
   ```

3. **Neurologist Reviews (Web UI)**
   - Neurologist logs in
   - Sees cases matching their specialty
   - Reviews and validates
   - Submits feedback

4. **Data Aggregation (Nightly)**
   ```python
   def aggregate_validations():
       """Aggregate validation results for analysis"""
       db = get_db()
       
       # Calculate agreement rates
       agreement_stats = db.execute("""
           SELECT 
               output_id,
               COUNT(*) as total_reviews,
               SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as agrees,
               AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) as agreement_rate
           FROM validations
           GROUP BY output_id
           HAVING total_reviews >= 2
       """).fetchall()
       
       return agreement_stats
   ```

5. **Export Gold-Standard Examples (Weekly)**
   ```python
   def export_validated_examples(min_agreement=0.80, min_reviews=2):
       """Export high-quality validated examples"""
       db = get_db()
       
       validated = db.execute("""
           SELECT 
               ao.input_text,
               ao.condition,
               ao.input_type,
               v.preferred_classification,
               v.preferred_confidence,
               v.preferred_evidence,
               v.preferred_medication,
               v.comments
           FROM ai_outputs ao
           JOIN validations v ON ao.id = v.output_id
           WHERE ao.id IN (
               SELECT output_id 
               FROM validations 
               GROUP BY output_id 
               HAVING AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) >= ?
               AND COUNT(*) >= ?
           )
       """, (min_agreement, min_reviews)).fetchall()
       
       # Export to JSON
       export_to_few_shot_format(validated)
   ```

## Authentication & Security

### Simple Authentication (Phase 1)

```python
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

login_manager = LoginManager()

class Neurologist(UserMixin):
    def __init__(self, id, email, name, specialty):
        self.id = id
        self.email = email
        self.name = name
        self.specialty = specialty

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute(
        "SELECT * FROM neurologists WHERE id = ?", (user_id,)
    ).fetchone()
    if user:
        return Neurologist(user['id'], user['email'], user['name'], user['specialty'])
    return None

@validation_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        user = db.execute(
            "SELECT * FROM neurologists WHERE email = ?", (email,)
        ).fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            user_obj = Neurologist(user['id'], user['email'], 
                                  user['name'], user['specialty'])
            login_user(user_obj)
            return redirect(url_for('validation.validation_home'))
        
        flash('Invalid credentials')
    
    return render_template('login.html')
```

### Security Considerations

1. **HTTPS Required**: Always use HTTPS in production
2. **Password Hashing**: Use bcrypt for password storage
3. **Session Management**: Flask-Login for session handling
4. **API Tokens**: Optional API token authentication
5. **Rate Limiting**: Limit validation submissions per hour
6. **Audit Logging**: Log all validation actions

## Analytics Dashboard

### Metrics to Track

```python
@validation_bp.route('/dashboard')
@login_required
def dashboard():
    """Analytics dashboard for validation program"""
    db = get_db()
    
    # Overall metrics
    total_outputs = db.execute(
        "SELECT COUNT(*) FROM ai_outputs"
    ).fetchone()[0]
    
    validated_count = db.execute(
        "SELECT COUNT(*) FROM ai_outputs WHERE validation_status = 'validated'"
    ).fetchone()[0]
    
    agreement_rate = db.execute("""
        SELECT AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) 
        FROM validations
    """).fetchone()[0]
    
    # By condition
    condition_stats = db.execute("""
        SELECT 
            ao.condition,
            COUNT(v.id) as validations,
            AVG(CASE WHEN v.is_correct THEN 1.0 ELSE 0.0 END) as agreement
        FROM ai_outputs ao
        LEFT JOIN validations v ON ao.id = v.output_id
        GROUP BY ao.condition
    """).fetchall()
    
    # Top validators
    top_validators = db.execute("""
        SELECT 
            neurologist_name,
            COUNT(*) as total_validations,
            AVG(review_time_seconds) as avg_time
        FROM validations
        GROUP BY neurologist_id
        ORDER BY total_validations DESC
        LIMIT 10
    """).fetchall()
    
    return render_template('dashboard.html',
                         total_outputs=total_outputs,
                         validated_count=validated_count,
                         agreement_rate=agreement_rate,
                         condition_stats=condition_stats,
                         top_validators=top_validators)
```

## Integration with Existing App

### Modify `app.py`

```python
# Add to app.py
from routes.validation import validation_bp

app.register_blueprint(validation_bp, url_prefix='/validation')

# Modify analyze() function
def analyze(text, analysis_type='classification', specialty='neurology'):
    # ... existing code ...
    
    # Generate AI response
    response = generate_ai_response(text, analysis_type, specialty)
    
    # Save for potential validation (10% sample rate)
    if random.random() < 0.10:
        save_for_validation(text, response, {
            'type': analysis_type,
            'condition': specialty,
            'timestamp': datetime.now()
        })
    
    return response
```

## Usage Workflow for Neurologists

### Onboarding

1. **Registration**
   - Email + credentials submitted
   - Admin verifies medical license
   - Account activated

2. **First Login**
   - Complete profile (specialty, experience)
   - Tutorial on validation UI
   - Start validating

### Daily Workflow

1. **Log in** to `/validate`
2. **Review quota**: 10-20 cases per session
3. **Validate cases**:
   - Read case
   - Review AI output
   - Click Yes/No
   - Add comments if needed
   - Submit
4. **Track progress**: See stats dashboard
5. **Log out**

### Incentives

- **Leaderboard**: Top validators
- **Academic credit**: Co-authorship on papers using data
- **CME credits**: If applicable
- **Recognition**: Featured on website
- **Impact metrics**: Show how validations improve AI

## Data Export for Research

### Export Validated Dataset

```python
def export_validated_dataset(output_format='json'):
    """Export validated examples for research/publication"""
    db = get_db()
    
    # Get consensus validations (≥80% agreement, ≥2 reviews)
    dataset = db.execute("""
        WITH agreement AS (
            SELECT 
                output_id,
                COUNT(*) as reviews,
                AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) as agreement
            FROM validations
            GROUP BY output_id
            HAVING reviews >= 2 AND agreement >= 0.8
        )
        SELECT 
            ao.input_text,
            ao.condition,
            ao.ai_classification,
            ao.ai_confidence,
            ao.ai_evidence,
            ao.ai_medication_analysis,
            v.comments,
            v.preferred_classification,
            a.agreement,
            a.reviews
        FROM ai_outputs ao
        JOIN agreement a ON ao.id = a.output_id
        JOIN validations v ON ao.id = v.output_id
    """).fetchall()
    
    if output_format == 'json':
        return json.dumps([dict(row) for row in dataset], indent=2)
    elif output_format == 'csv':
        return convert_to_csv(dataset)
```

## Implementation Phases

### Phase 1: Basic Validation (Week 1-2)
- [OK] Create database schema
- [OK] Build simple validation UI
- [OK] Implement yes/no validation
- [OK] Add comment box
- [OK] Basic authentication

### Phase 2: Enhanced Features (Week 3-4)
- [OK] Random sampling algorithm
- [OK] Stratified selection by condition
- [OK] Priority scoring
- [OK] Neurologist dashboard
- [OK] Stats tracking

### Phase 3: Advanced Analytics (Week 5-6)
- [OK] Inter-rater reliability metrics
- [OK] Automated quality reports
- [OK] Export gold-standard dataset
- [OK] Feedback loop to improve prompts

### Phase 4: Scale & Optimize (Ongoing)
- [OK] Mobile-friendly UI
- [OK] Batch validation mode
- [OK] Gamification elements
- [OK] API for external integration

## Estimated Effort

| Component | Development Time | Complexity |
|-----------|-----------------|------------|
| Database schema | 2 hours | Low |
| Backend routes | 4-6 hours | Medium |
| Validation UI | 6-8 hours | Medium |
| Authentication | 3-4 hours | Medium |
| Random sampling | 2-3 hours | Low |
| Analytics dashboard | 4-6 hours | Medium |
| Testing | 4-6 hours | Medium |
| Documentation | 2-3 hours | Low |
| **Total** | **27-38 hours** | **Medium** |

## Benefits

### Short-term (1-3 months)
- Validate AI accuracy (establish baseline)
- Identify common errors
- Build initial gold-standard dataset (100-500 examples)
- Improve neurologist engagement

### Medium-term (3-6 months)
- Create high-quality labeled dataset (500-1000 examples)
- Improve few-shot examples with validated data
- Publish validation metrics
- Attract more neurologist validators

### Long-term (6-12 months)
- Continuous improvement feedback loop
- Research publications using validated dataset
- Industry-leading accuracy metrics
- Scale to other specialties

## Success Metrics

- **Validation Rate**: Target 10% of all outputs reviewed
- **Neurologist Engagement**: ≥5 active validators
- **Agreement Rate**: ≥80% inter-rater agreement
- **Dataset Size**: 1000+ validated examples in 6 months
- **AI Improvement**: Measurable accuracy increase from feedback

---

## Summary

This validation system enables:
1. **Expert feedback collection** via simple yes/no + comments
2. **Random sampling** with stratification by condition
3. **Gold-standard dataset** creation for continuous improvement
4. **Quality metrics** to track AI performance
5. **Scalable architecture** for growing neurologist network

**Implementation:** 27-38 hours of development, phases over 6 weeks

**Result:** High-quality, expert-validated dataset to continuously improve Vecta AI accuracy.
