"""
Creating an eval using Langchain with Opik
"""

import opik
from opik import track
from opik.integrations.langchain import OpikTracer
from opik.evaluation.metrics import base_metric, score_result, Equals
from opik.evaluation import evaluate
from typing import Any, Optional
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

# Initialize Opik client
client = opik.Opik()

# Initialize OpikTracer for Langchain
opik_tracer = OpikTracer()

# Initialize ChatOpenAI model
llm1 = ChatOpenAI(model="gpt-3.5-turbo", temperature=0).with_structured_output(method="json_mode")
llm2 = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

"""
Creating a dataset
"""
dataset = client.get_or_create_dataset(name="movies")
# Add dataset items to it
dataset.insert([
    {"movie_description": "A clownfish searches for his missing son", "decade": "2000s", "expected_output": "G"},
    {"movie_description": "People trapped in deadly puzzle games", "decade": "2000s", "expected_output": "R"},
    {"movie_description": "A boy wizard attends a magical school", "decade": "2000s", "expected_output": "PG"},
])

print(dataset)

"""
movie identifier prompt

Input: movie description and decade
Output: object with keys "movie_info" and "movie_title"
"""
mi_prompt_template = client.get_prompt(name="movie identifier")

"""
rating classifier prompt

Input: movie title (from movie identifier prompt)
Output: rating of either G, PG or R
"""
rc_prompt_template = client.get_prompt(name="rating classifier")

# test prompt format
mi_prompt = mi_prompt_template.format(movie_description="A clownfish searches for his missing son", decade="2000s")
print(mi_prompt)

"""
Chain two prompts: movie identifier -> rating classifier
Returns the final age rating (G, PG, or R)
"""
@track
def movie_rating_chain(dataset_item: dict) -> str:
    """
    Chain two prompts: movie identifier -> rating classifier
    Returns the final age rating (G, PG, or R)
    """
    
    # Extract parameters from dataset item
    movie_description = dataset_item["movie_description"]
    decade = dataset_item["decade"]
    
    # Step 1: Movie Identifier
    mi_prompt = mi_prompt_template.format(
        movie_description=movie_description, 
        decade=decade
    )
    
    # Create a human message with the prompt
    messages = [SystemMessage(mi_prompt)]
    
    # Use Langchain with OpikTracer callback
    response1 = llm1.invoke(messages, config={"callbacks": [opik_tracer]})

    print(response1)
    
    # Parse JSON response from first prompt
    movie_title = response1["movie_title"]
    
    # Step 2: Rating Classifier
    rc_prompt = rc_prompt_template.format(movie_title=movie_title)
    
    # Create a human message with the prompt
    messages2 = [SystemMessage(rc_prompt)]
    
    # Use Langchain with OpikTracer callback
    response2 = llm2.invoke(messages2, config={"callbacks": [opik_tracer]})
    
    # Return final rating as dictionary. note that this is required for the evaluation to work
    return {"output": response2.content.strip()}

# Test the chain
result = movie_rating_chain({
    "movie_description": "A clownfish searches for his missing son",
    "decade": "2000s"
})
print(f"Final rating: {result}")

"""
Custom Metric: RatingMatch
Scores 1 if output matches expected_output, else 0
"""

class RatingMatch(base_metric.BaseMetric):
    def __init__(self, name: str = "rating_match", track: bool = True, project_name: Optional[str] = None):
        super().__init__(
            name=name,
            track=track,
            project_name=project_name,
        )
    
    def score(self, output: str, reference: str, **ignored_kwargs: Any):
        # Compare output with reference (case-insensitive and stripped)
        match = output.strip().upper() == reference.strip().upper()
        
        return score_result.ScoreResult(
            name=self.name,
            value=1.0 if match else 0.0,
            reason=f"Output '{output}' {'matches' if match else 'does not match'} expected '{reference}'"
        )

"""
Evaluation using the dataset, movie_rating_chain, and RatingMatch metric
"""

# Create metric instance
rating_match_metric = RatingMatch()
equals_metric = Equals()

# Run evaluation
evaluation = evaluate(
    dataset=dataset,
    task=movie_rating_chain,
    scoring_metrics=[rating_match_metric, equals_metric],
    experiment_name="movie eval langchain",
    experiment_config={"description": "Evaluating movie rating chain eval test for langchain"},
    scoring_key_mapping={"reference": "expected_output"},
)

print("Evaluation completed!")
print(evaluation)