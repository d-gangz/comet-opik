# LiteLLM + Opik Integration Learnings

## Overview
This document captures key learnings from implementing evaluations using LiteLLM and Opik for LLM tracing and evaluation.

## Key Integration Points

### 1. LiteLLM Setup with Opik
```python
from litellm.integrations.opik.opik import OpikLogger
import litellm

# Initialize Opik logger
opik_logger = OpikLogger()
litellm.callbacks = [opik_logger]
```

### 2. Using @track Decorator
- Always use `@track` decorator on functions that call LiteLLM to enable tracing
- For synchronous code, use `litellm.completion()` (not `acompletion()`)
- Include `get_current_span_data()` in metadata for proper span context:
```python
metadata={
    "opik": {
        "current_span_data": get_current_span_data(),
    },
}
```

### 3. Task Functions for Evaluation
**Important**: Task functions must return a dictionary, not a plain string:
```python
# ❌ Wrong
def task(dataset_item):
    return "some_output"

# ✅ Correct
def task(dataset_item):
    return {"output": "some_output"}
```

### 4. Custom Metrics
- Inherit from `base_metric.BaseMetric`
- **IMPORTANT**: Must call `super().__init__()` to register the metric with Opik's tracking system
- The `score` method receives merged dataset + task output
- Use `reference` parameter name (not `expected_output`) for proper data mapping
- Return `ScoreResult` with value, name, and optional reason

**Critical for UI Display**: Your custom metric won't appear as a separate unit in the Opik trace unless you:
1. Call `super().__init__()` with `track=True`
2. Use the standard parameter name `reference` in your score method

```python
class RatingMatch(base_metric.BaseMetric):
    def __init__(self, name: str = "rating_match", track: bool = True, project_name: Optional[str] = None):
        # MUST call super().__init__() to register with Opik!
        super().__init__(
            name=name,
            track=track,  # This enables UI tracking
            project_name=project_name,
        )
    
    def score(self, output: str, reference: str, **ignored_kwargs):
        # Use 'reference' not 'expected_output' for proper mapping
        match = output.strip().upper() == reference.strip().upper()
        return score_result.ScoreResult(
            name=self.name,
            value=1.0 if match else 0.0,
            reason=f"Output '{output}' {'matches' if match else 'does not match'} expected '{reference}'"
        )
```

**Why This Matters**:
- Without `super().__init__()`: Your metric calculates scores but isn't registered with Opik's tracking system
- Without `track=True`: The metric won't create a separate trace span in the UI
- Without `reference` parameter: Opik can't properly map your expected values from the dataset

### 5. Dataset Structure
Dataset items should contain all inputs and expected outputs:
```python
dataset.insert([
    {"movie_description": "...", "decade": "2000s", "expected_output": "G"},
])
```

### 6. Evaluation Pattern
```python
evaluation = evaluate(
    dataset=dataset,
    task=your_task_function,
    scoring_metrics=[your_metric],
    experiment_name="descriptive_name"
)
```

## Common Pitfalls

1. **Missing ipywidgets**: Install with `uv pip install ipywidgets` for Jupyter progress bars

2. **Task Return Type**: The evaluate function expects task output to be a dictionary, not a string

3. **Async vs Sync**: Use synchronous `litellm.completion()` for standard evaluations

4. **Prompt Templates**: When using structured outputs, ensure response_format is properly set:
```python
response_format=prompt_template.metadata["response_format"]
```

5. **Custom Metrics Not Showing in UI**: 
   - Forgetting to call `super().__init__()` in custom metric constructor
   - Not passing `track=True` to enable UI tracking
   - Using wrong parameter names (e.g., `expected_output` instead of `reference`)

## Prompt Chaining Example
For multi-step LLM chains:
1. Parse intermediate outputs carefully (e.g., JSON parsing)
2. Pass data between prompts using extracted fields
3. Return final output in dictionary format

## Dependencies
- opik==1.8.2
- litellm==1.74.2
- ipywidgets (for Jupyter notebook progress bars)