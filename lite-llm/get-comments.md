# How to programatically get comments

## Detailed Summary: Retrieving Trace Comments in Opik Using the Python SDK

### Overview

To programmatically retrieve all comments from traces in an Opik experiment (on the hosted Comet platform), you need to follow a multi-step process. This involves identifying your experiment, collecting trace IDs, and then fetching comments for each trace. You’ll use the Opik Python SDK, which offers both high-level and low-level (REST client) interfaces for these operations.

### Step-by-Step Workflow

#### 1. **Authenticate and Initialize the SDK**

Start by configuring the SDK with your API key and workspace:

```python
import opik

client = opik.Opik(api_key="YOUR_API_KEY", workspace="YOUR_WORKSPACE")
```

#### 2. **Get Your Experiment ID**

If you know your experiment name:

```python
experiment = client.get_experiment_by_name("YOUR_EXPERIMENT_NAME")
experiment_id = experiment.id
```

Or, to list all experiments and pick one:

```python
experiments = client.rest_client.experiments.find_experiments(page=0, size=10)
for exp in experiments:
    print(exp.id, exp.name)
```

#### 3. **List All Trace IDs in the Experiment**

Once you have the experiment ID, retrieve all trace IDs:

```python
experiment = client.get_experiment_by_id(experiment_id)
items = experiment.get_items()
trace_ids = [item.trace_id for item in items]
```

#### 4. **Fetch Comments for Each Trace**

For each trace ID, use the low-level REST client to get trace details and extract comments:

```python
for trace_id in trace_ids:
    trace = client.rest_client.traces.get_trace_by_id(trace_id)
    comment_ids = trace.get("comments", [])
    for comment_id in comment_ids:
        comment = client.rest_client.traces.get_trace_comment(comment_id, trace["id"])
        print(comment)
```

- The `comments` field in the trace object contains a list of comment IDs.
- Use `get_trace_comment` to fetch full details for each comment.

### Understanding `client` Interfaces in the SDK

The Opik Python SDK provides several ways to interact with resources:

| Interface Example                         | Description                                                                                         | Usage Scenario                          |
|--------------------------------------------|-----------------------------------------------------------------------------------------------------|-----------------------------------------|
| `client.get_experiment_by_name()`          | High-level method to fetch an experiment by name                                                    | Quick lookup by name                    |
| `client.get_experiment_by_id()`            | High-level method to fetch an experiment by ID                                                      | When you know the experiment ID         |
| `client.rest_client.experiments`           | Low-level access to all experiment-related REST API endpoints                                       | Advanced operations, full control       |
| `client.rest_client.traces`                | Low-level access to all trace-related REST API endpoints                                            | Fetching trace details, comments, etc.  |

- **High-level methods** are more convenient for common tasks.
- **Low-level REST client** (`rest_client`) mirrors the REST API and exposes all endpoints, giving you maximum flexibility and access to advanced features.

### Key Points

- Use the high-level SDK methods for common workflows (fetching experiments, items).
- Use the low-level `rest_client` for direct access to REST API endpoints, especially for operations like fetching trace comments.
- The SDK handles authentication, request formatting, and response parsing for you.
- The process is: get experiment → get items (trace IDs) → get trace details → get comments.

### Example Summary Table

| Step                      | SDK Method / Attribute                              | Output                        |
|---------------------------|-----------------------------------------------------|-------------------------------|
| Get experiment by name    | `client.get_experiment_by_name("name")`             | Experiment object             |
| List all experiments      | `client.rest_client.experiments.find_experiments()` | List of experiment objects    |
| Get experiment by ID      | `client.get_experiment_by_id("id")`                 | Experiment object             |
| List items (trace IDs)    | `experiment.get_items()`                            | List of items with trace IDs  |
| Get trace details         | `client.rest_client.traces.get_trace_by_id(trace_id)`| Trace object                  |
| Get trace comment         | `client.rest_client.traces.get_trace_comment()`      | Comment object                |

### Final Tips

- Always consult the latest Opik documentation for updates on SDK methods and REST API endpoints.
- For advanced or less-documented features, the `rest_client` is your go-to for full API access.
- You can combine high-level and low-level SDK usage in your workflow for maximum efficiency and flexibility.

This approach ensures you can reliably and programmatically retrieve all trace comments from your experiments using the Opik Python SDK.

You can check out this [Traces Client doc](https://www.comet.com/docs/opik/python-sdk-reference/rest_api/clients/traces.html#opik.rest_api.traces.client.TracesClient.get_trace_by_id)