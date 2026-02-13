# Few-Shot Examples Integration Guide

## Overview

This guide shows how to integrate the curated few-shot examples and clinical guidelines into Vecta AI for enhanced prompt engineering.

## Data Structure

```
data/
├── few_shot_examples.json          # 22 curated clinical examples
├── guidelines/
│   └── neurology_guidelines.json   # Clinical guideline snippets
└── context/                         # (Future: RAG vector store)
```

## Available Examples

### By Condition
- **Epilepsy**: 5 examples (generalized, focal, refractory, JME, status epilepticus)
- **Parkinson's**: 5 examples (advanced, early, motor fluctuations, non-motor, differential)
- **Stroke**: 5 examples (capsular warning, posterior circulation, acute tPA, TIA, hemorrhagic transformation)
- **Headache**: 2 examples (migraine with aura, cluster headache)
- **Dementia**: 2 examples (Alzheimer's, Lewy body dementia)

### By Analysis Type
- Classification: 10 examples
- Diagnosis: 9 examples
- Extraction: 2 examples
- Summary: 1 example

## Quick Integration (Option 1: Direct Import)

### Step 1: Test the Loader

```bash
python utils/few_shot_loader.py
```

Expected output shows available conditions, statistics, and sample formatted examples.

### Step 2: Import in Your Code

```python
from utils.few_shot_loader import FewShotExampleLoader

# Initialize loader
loader = FewShotExampleLoader()

# Get examples for epilepsy classification
examples = loader.get_examples_by_condition(
    condition='epilepsy',
    n=2,
    analysis_type='classification'
)

# Format for prompt
formatted_examples = loader.format_few_shot_examples_for_prompt(
    examples, 
    'classification'
)

# Get guidelines
guidelines = loader.get_guideline_context('epilepsy')

# Get complete enhanced context
context = loader.get_enhanced_prompt_context(
    condition='epilepsy',
    analysis_type='classification',
    n_examples=2,
    include_guidelines=True
)
```

## Integration into app.py (Option 2: Modify Prompt Construction)

### Current Prompt Construction (app.py ~line 360-380)

```python
def construct_vecta_prompt(self, system_prompt: str, user_prompt: str, 
                          medical_data: str, is_tabular: bool = False, 
                          analysis_type: str = "custom") -> str:
    """Construct optimized Vecta AI prompt with proper formatting"""
    
    # Add clinical reasoning activation
    clinical_activation = self.get_clinical_reasoning_activation()
    
    # ... rest of current code
```

### Enhanced Version with Few-Shot Examples

```python
from utils.few_shot_loader import FewShotExampleLoader

class VectaAIPromptEngine:
    def __init__(self):
        self.few_shot_loader = FewShotExampleLoader()
    
    def construct_vecta_prompt(self, system_prompt: str, user_prompt: str, 
                              medical_data: str, is_tabular: bool = False, 
                              analysis_type: str = "custom",
                              specialty: str = "neurology") -> str:
        """Enhanced prompt construction with few-shot examples and guidelines"""
        
        # Get clinical reasoning activation (existing)
        clinical_activation = self.get_clinical_reasoning_activation()
        
        # NEW: Get few-shot examples and guidelines
        enhanced_context = self.few_shot_loader.get_enhanced_prompt_context(
            condition=specialty,  # 'epilepsy', 'parkinsons', 'stroke', etc.
            analysis_type=analysis_type,
            n_examples=2,
            include_guidelines=True
        )
        
        # Construct enhanced prompt
        final_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}

{clinical_activation}

RELEVANT CLINICAL GUIDELINES:
{enhanced_context['guidelines'][:1000]}  # Limit to 1000 chars to avoid token overflow

{enhanced_context['examples']}

{data_instructions}

<|eot_id|><|start_header_id|>user<|end_header_id|>

Vecta AI, please apply your specialized medical training to this analysis:

ANALYSIS REQUEST: {user_prompt}

MEDICAL DATA FOR ANALYSIS:
{medical_data}

Use your comprehensive medical knowledge and clinical reasoning to provide a thorough, evidence-based analysis. Apply the appropriate medical frameworks from your training and structure your response for maximum clinical utility.

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        return final_prompt
```

## Minimal Integration (Option 3: Add to Existing Prompts)

If you want minimal changes, just add examples to your existing specialty prompts:

### Modify app.py

```python
from utils.few_shot_loader import load_few_shot_examples, load_guidelines

# Around line 90 in app.py, modify get_specialty_prompts()
@staticmethod
def get_specialty_prompts():
    """Vecta AI specialty-specific reasoning prompts with few-shot examples"""
    
    # Load examples once at module level (or cache in class)
    epilepsy_examples = load_few_shot_examples('epilepsy', n=1, analysis_type='classification')
    parkinsons_examples = load_few_shot_examples('parkinsons', n=1)
    
    return {
        "neurology": f"""Vecta AI NEUROLOGICAL ANALYSIS:
Activate neurology knowledge module:
- Anatomical localization: Use your neuroanatomy training
- Seizure classification: Apply ILAE 2025 criteria from your database
- Cognitive assessment: Use your neuropsychology knowledge
- Motor function analysis: Apply your movement disorder training
- Medication optimization: Use your neuropharmacology expertise

EXAMPLE CASE:
Input: {epilepsy_examples[0]['input']}
Analysis: 
- {epilepsy_examples[0]['expected_output']['classification']}
- {epilepsy_examples[0]['expected_output']['clinical_confidence']}
"""
    }
```

## Testing the Integration

### Test Script

Create `test_few_shot_integration.py`:

```python
#!/usr/bin/env python3
"""Test few-shot example integration"""

from utils.few_shot_loader import FewShotExampleLoader

def test_integration():
    loader = FewShotExampleLoader()
    
    # Test 1: Load examples
    print("Test 1: Loading epilepsy examples...")
    examples = loader.get_examples_by_condition('epilepsy', n=2)
    assert len(examples) == 2, "Failed to load 2 examples"
    print(f"✓ Loaded {len(examples)} epilepsy examples")
    
    # Test 2: Format for prompt
    print("\nTest 2: Formatting examples for prompt...")
    formatted = loader.format_few_shot_examples_for_prompt(examples, 'classification')
    assert len(formatted) > 0, "Failed to format examples"
    print(f"✓ Formatted examples ({len(formatted)} characters)")
    
    # Test 3: Load guidelines
    print("\nTest 3: Loading epilepsy guidelines...")
    guidelines = loader.get_guideline_context('epilepsy')
    assert len(guidelines) > 0, "Failed to load guidelines"
    print(f"✓ Loaded guidelines ({len(guidelines)} characters)")
    
    # Test 4: Enhanced context
    print("\nTest 4: Getting enhanced context...")
    context = loader.get_enhanced_prompt_context('stroke', 'diagnosis', n_examples=2)
    assert 'examples' in context, "Missing examples in context"
    assert 'guidelines' in context, "Missing guidelines in context"
    print(f"✓ Enhanced context complete")
    
    # Test 5: Statistics
    print("\nTest 5: Getting statistics...")
    stats = loader.get_example_statistics()
    print(f"✓ Statistics: {stats}")
    
    print("\n✓✓✓ All tests passed! ✓✓✓")

if __name__ == "__main__":
    test_integration()
```

Run the test:
```bash
python test_few_shot_integration.py
```

## Expected Improvements

### Before Few-Shot Examples
```
User: "Patient with 3Hz spike-wave on EEG and brief staring spells"

Vecta AI Response (without examples):
"Based on the EEG findings showing 3Hz spike-wave pattern and brief staring spells, 
this appears consistent with absence seizures..."
[Generic, less specific medication recommendations]
```

### After Few-Shot Examples
```
User: "Patient with 3Hz spike-wave on EEG and brief staring spells"

Vecta AI Response (with examples):
- Classification: Generalized absence epilepsy with characteristic 3Hz spike-wave pattern per ILAE 2025 classification
- Clinical_Confidence: High based on classic EEG findings and clinical semiology (brief awareness loss, typical pattern)
- Evidence: Bilaterally synchronous 3Hz spike-wave on EEG, brief awareness loss episodes, absence semiology
- Medication_Analysis: First-line: Ethosuximide or valproate per guideline recommendations, avoid carbamazepine and oxcarbazepine (may worsen absence seizures)
```

## Performance Benchmarking

### Create Benchmark Script

```python
# benchmark_prompts.py
from utils.few_shot_loader import FewShotExampleLoader
import time

def benchmark():
    loader = FewShotExampleLoader()
    
    # Timing tests
    start = time.time()
    for _ in range(100):
        examples = loader.get_examples_by_condition('epilepsy', n=2)
        formatted = loader.format_few_shot_examples_for_prompt(examples, 'classification')
    elapsed = time.time() - start
    
    print(f"100 iterations took {elapsed:.2f}s ({elapsed/100*1000:.1f}ms per call)")
    print("Expected overhead per request: <2ms")

if __name__ == "__main__":
    benchmark()
```

## Condition Mapping

Map user input/specialty to condition for example selection:

```python
CONDITION_MAPPING = {
    'neurology': 'epilepsy',  # Default to epilepsy for general neurology
    'epilepsy': 'epilepsy',
    'seizure': 'epilepsy',
    'parkinsons': 'parkinsons',
    'parkinson': 'parkinsons',
    'movement disorder': 'parkinsons',
    'stroke': 'stroke',
    'cerebrovascular': 'stroke',
    'tia': 'stroke',
    'headache': 'headache',
    'migraine': 'headache',
    'cluster headache': 'headache',
    'dementia': 'dementia',
    'alzheimers': 'dementia',
    'cognitive': 'dementia'
}

def get_condition_from_input(user_input: str, specialty: str) -> str:
    """Determine condition type from user input and specialty"""
    input_lower = user_input.lower()
    
    # Check for specific conditions in input
    for keyword, condition in CONDITION_MAPPING.items():
        if keyword in input_lower:
            return condition
    
    # Fall back to specialty
    return CONDITION_MAPPING.get(specialty, 'epilepsy')
```

## Gradual Rollout Strategy

### Phase 1 (Week 1): Testing
- Integrate loader utility
- Test with sample prompts
- Verify no performance degradation

### Phase 2 (Week 2): Epilepsy Only
- Add few-shot examples only for epilepsy/seizure queries
- Monitor accuracy improvements
- Collect user feedback

### Phase 3 (Week 3): All Conditions
- Extend to all neurology conditions
- Add guideline context
- A/B test with baseline

### Phase 4 (Week 4): Optimization
- Adjust number of examples based on performance
- Fine-tune guideline selection
- Implement caching for frequently used examples

## Troubleshooting

### Issue: FileNotFoundError
```python
FileNotFoundError: data/few_shot_examples.json not found
```
**Solution**: Ensure data directory structure exists:
```bash
mkdir -p data/few_shot data/guidelines data/context
```

### Issue: Import Error
```python
ModuleNotFoundError: No module named 'utils.few_shot_loader'
```
**Solution**: Add project root to Python path:
```python
import sys
sys.path.insert(0, '/path/to/med42_service')
```

### Issue: Token Limit Exceeded
```
Model input too long: exceeded context window
```
**Solution**: Limit guideline context length:
```python
guidelines = context['guidelines'][:1000]  # Limit to 1000 chars
```

## Next Steps

1. **Test the loader**: `python utils/few_shot_loader.py`
2. **Run integration test**: `python test_few_shot_integration.py`
3. **Choose integration approach**: Direct import (Option 2) recommended
4. **Modify app.py**: Add few-shot loading to prompt construction
5. **Test with real queries**: Compare outputs before/after
6. **Measure improvements**: Track accuracy, consistency, guideline compliance

## Additional Resources

- Few-shot examples: `data/few_shot_examples.json`
- Guidelines: `data/guidelines/neurology_guidelines.json`
- Loader utility: `utils/few_shot_loader.py`
- Analysis docs: `PROMPT_ENGINEERING_ANALYSIS.md`
- Recommendations: `PROMPT_IMPROVEMENTS.md`

## Questions?

Review the detailed analysis in:
- `PROMPT_ENGINEERING_ANALYSIS.md` - Current techniques and improvements
- `PROMPT_IMPROVEMENTS.md` - Public data sources and implementation plan
