# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Opik Evaluation Playground - a sandbox for testing and evaluating AI applications using Opik (Comet's platform for logging, monitoring, and evaluating LLM calls and chains).

## Development Commands

### Environment Setup
- **Package management**: Use `uv` instead of pip for all package operations
- **Install dependencies**: `uv pip install -r requirements.txt`
- **Run scripts**: `uv run <script_name.py>`

### Configuration
- **Opik setup**: Run `opik configure` to set up Opik credentials (should already be configured)
- **Environment variables**: API keys are stored in `.env` file (OpenAI API key is configured)

### Running the Application
- **Main script**: `uv run litellm_test.py`
- The script demonstrates LiteLLM + Opik integration with async LLM calls

## Architecture

### Core Integration Pattern
The project uses an async callback pattern for LLM observability:
1. OpikLogger is initialized and registered as a callback with LiteLLM
2. LLM calls are made asynchronously using `litellm.acompletion()`
3. Opik automatically logs interactions through the callback system
4. All LLM calls require async/await context due to OpikLogger requirements

### Key Files
- `litellm_test.py`: Main demonstration script showing Opik + LiteLLM integration
- `.env`: Contains OpenAI API key and other environment variables
- `requirements.txt`: Python dependencies managed with uv

### Dependencies
- **Core**: `opik==1.8.2`, `litellm==1.74.2`, `openai==1.95.1`
- **Testing**: `pytest==8.4.1` (no tests currently implemented)
- **Async**: Uses Python's built-in `asyncio` for async operations

## Important Notes

### Async Requirement
The OpikLogger requires an async event loop context. Always use:
- `litellm.acompletion()` instead of `litellm.completion()`
- Wrap code in `async def main()` and `asyncio.run(main())`

### Package Management
This project uses `uv` as the package manager, not standard pip. All commands should use `uv run` or `uv pip`.