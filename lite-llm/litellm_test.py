from litellm.integrations.opik.opik import OpikLogger
from opik.opik_context import get_current_span_data
import litellm
import asyncio

async def main():
    """
Basic test using litellm as instructed in their docs

When I ran this script, it created a trace in the `Default Project` in the Opik UI.
"""
    opik_logger = OpikLogger()
    litellm.callbacks = [opik_logger]

    response = await litellm.acompletion(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Why is tracking and evaluation of LLMs important?"}
        ],
        # metadata={
        #     "opik": {
        #         "project_name": "1st Test Project",  # Set your project name here
        #         "current_span_data": get_current_span_data(),
        #     }
        # }
        # stream=True
    )
    
    print("Response:", response.choices[0].message.content)
    
    # # Handle streaming response
    # async for part in response:
    #     print(part.choices[0].delta.content or "", end="")

if __name__ == "__main__":
    asyncio.run(main())
