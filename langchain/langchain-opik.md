# Langchain + Opik Integration Key Learnings

Based on our implementation journey, here are the key learnings when using Langchain with Opik:

## 1. **Response Object Handling**
- Langchain returns `AIMessage` objects, not raw strings
- Always extract content using `.content` attribute
- Example: `response.content.strip()` not just `response`

## 2. **JSON Response Format Considerations**
- When using `.with_structured_output(method="json_mode")`, the response is already parsed as a dictionary
- OpenAI requires prompts to contain the word "json" when using JSON response format
- Consider having separate LLM instances for different response formats:
  ```python
  llm1 = ChatOpenAI(model="gpt-3.5-turbo").with_structured_output(method="json_mode")  # For JSON
  llm2 = ChatOpenAI(model="gpt-3.5-turbo")  # For text
  ```

## 3. **Message Format**
- Use `HumanMessage` or `SystemMessage` objects from `langchain_core.messages`
- Not dict format like in LiteLLM

## 4. **Opik Integration**
- Use `OpikTracer()` from `opik.integrations.langchain`
- Pass it as a callback: `config={"callbacks": [opik_tracer]}`
- No need for async/await like in LiteLLM

## 5. **Evaluation Return Format**
- Always return a dictionary with string values for Opik metrics
- Metrics expect strings, not Langchain objects
- Format: `{"output": response.content.strip()}`

## 6. **Installation Requirements**
```bash
uv pip install opik langchain langchain-openai
```

These differences from LiteLLM are crucial for successful integration with Opik's evaluation framework.