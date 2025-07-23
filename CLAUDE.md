# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Opik Evaluation Playground - a comprehensive sandbox for testing and evaluating AI applications using Opik (Comet's platform for logging, monitoring, and evaluating LLM calls and chains). The project serves as:

- A learning environment for Opik integration patterns
- A comparison platform for different LLM libraries (LiteLLM vs LangChain)
- An experimental playground for custom evaluation metrics
- A documentation repository for integration best practices

## Project Structure

```
comet-opik/
├── lite-llm/         # LiteLLM + Opik integration examples
│   ├── litellm_test.py      # Basic async LLM calls with Opik logging
│   ├── eval_test.py         # Complete evaluation pipeline with custom metrics
│   ├── tracked_func.py      # Streaming function example
│   └── litellm_opik_learnings.txt  # Implementation insights
├── langchain/        # LangChain + Opik integration examples
│   ├── eval_test.py         # LangChain evaluation implementation
│   └── langchain_opik_learnings.txt  # LangChain-specific insights
├── extract/          # Documentation on retrieving trace comments
├── web-scrape/       # Web scraping utilities for content processing
└── requirements.txt  # Python dependencies
```

## Development Commands

### Environment Setup
- **Package management**: Use `uv` instead of pip for all package operations
- **Install dependencies**: `uv pip install -r requirements.txt`
- **Run scripts**: `uv run <script_name.py>`

### Configuration
- **Opik setup**: Run `opik configure` to set up Opik credentials (should already be configured)
- **Environment variables**: API keys are stored in `.env` file (OpenAI API key is configured)

### Running Examples
- **Basic LiteLLM**: `uv run lite-llm/litellm_test.py`
- **LiteLLM Evaluation**: `uv run lite-llm/eval_test.py`
- **LangChain Evaluation**: `uv run langchain/eval_test.py`

## Architecture

### Core Integration Patterns

#### LiteLLM Integration (Async)
The project uses an async callback pattern for LLM observability:
1. OpikLogger is initialized and registered as a callback with LiteLLM
2. LLM calls are made asynchronously using `litellm.acompletion()`
3. Opik automatically logs interactions through the callback system
4. All LLM calls require async/await context due to OpikLogger requirements
5. Use `get_current_span_data()` for proper tracing in custom metrics

#### LangChain Integration (Sync)
Alternative integration pattern using LangChain:
1. Uses `OpikTracer` as a callback handler
2. Synchronous execution model
3. Handles `AIMessage` objects which require `.content` access
4. More straightforward for non-async workflows

### Evaluation Framework
- Dataset creation and management through Opik client
- Custom metric development inheriting from `BaseMetric`
- Multi-step LLM chains (e.g., movie identifier → rating classifier)
- Structured evaluation with experiment tracking
- Metrics properly display in Opik UI when configured correctly

### Key Files
- `lite-llm/litellm_test.py`: Basic async LLM calls with Opik logging
- `lite-llm/eval_test.py`: Complete evaluation pipeline demonstrating custom metrics
- `langchain/eval_test.py`: LangChain-based evaluation implementation
- `lite-llm/tracked_func.py`: Example of streaming with `@track` decorator
- `.env`: Contains OpenAI API key and other environment variables
- `requirements.txt`: Python dependencies managed with uv

### Dependencies
- **Core**: `opik==1.8.2`, `litellm==1.74.2`, `openai==1.95.1`
- **LangChain**: `langchain-openai` for LangChain integration
- **Testing**: `pytest==8.4.1` (no tests currently implemented)
- **Async**: Uses Python's built-in `asyncio` for async operations
- **Utilities**: `python-docx` for document generation

## Important Notes

### Opik Documentation
Check out `opik-documentation.md` for the Full Opik documentation.

Here is the [full documentation for Opik](https://www.comet.com/docs/opik/llms-full.txt)

Do fetch the contents from this link when I am implementing any Opik Stuff.

### Async Requirement (LiteLLM)
The OpikLogger requires an async event loop context. Always use:
- `litellm.acompletion()` instead of `litellm.completion()`
- Wrap code in `async def main()` and `asyncio.run(main())`

### Custom Metrics Implementation
- Must inherit from `opik.evaluation.metrics.BaseMetric`
- Implement `name` property and `score` method
- For proper UI display in traces, ensure metrics are initialized during evaluation setup
- Use `get_current_span_data()` to access span information in async contexts

### Integration Learnings
Key insights documented in learning files:
1. **LiteLLM**: Custom metrics require proper initialization for UI display
2. **LangChain**: Response objects are `AIMessage` instances requiring `.content` access
3. **Evaluation**: JSON formatting and proper data structure handling is crucial
4. **Tracing**: Comments can be extracted programmatically using Opik GraphQL API

### Package Management
This project uses `uv` as the package manager, not standard pip. All commands should use `uv run` or `uv pip`.