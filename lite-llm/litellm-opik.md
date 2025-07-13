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
- The `score` method receives merged dataset + task output
- Return `ScoreResult` with value, name, and optional reason
```python
class RatingMatch(base_metric.BaseMetric):
    def score(self, output: str, expected_output: str, **ignored_kwargs):
        match = output.strip().upper() == expected_output.strip().upper()
        return score_result.ScoreResult(
            name=self.name,
            value=1.0 if match else 0.0,
            reason=f"Output '{output}' {'matches' if match else 'does not match'} expected '{expected_output}'"
        )
```

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

## Prompt Chaining Example
For multi-step LLM chains:
1. Parse intermediate outputs carefully (e.g., JSON parsing)
2. Pass data between prompts using extracted fields
3. Return final output in dictionary format

## Dependencies
- opik==1.8.2
- litellm==1.74.2
- ipywidgets (for Jupyter notebook progress bars)