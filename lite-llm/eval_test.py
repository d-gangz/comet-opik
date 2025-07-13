import opik
from opik import track
from opik.opik_context import get_current_span_data
from litellm.integrations.opik.opik import OpikLogger
import litellm
import json
from opik.evaluation.metrics import base_metric, score_result
from typing import Any
from opik.evaluation import evaluate

# Initialise logger
opik_logger = OpikLogger()
litellm.callbacks = [opik_logger]

# Initialise Opik client
client = opik.Opik()

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

# Read metadata from the most recent version of a prompt
print(mi_prompt_template.metadata)

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
    
    response1 = litellm.completion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": mi_prompt}],
        response_format=mi_prompt_template.metadata["response_format"],
        metadata={
            "opik": {
                "current_span_data": get_current_span_data(),
                },
        },
    )
    
    # Parse JSON response from first prompt
    movie_info = json.loads(response1.choices[0].message.content)
    movie_title = movie_info["movie_title"]
    
    # Step 2: Rating Classifier
    rc_prompt = rc_prompt_template.format(movie_title=movie_title)
    
    response2 = litellm.completion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": rc_prompt}],
        metadata={
            "opik": {
                "current_span_data": get_current_span_data(),
                },
        },
    )
    
    # Return final rating as dictionary. note that this is required for the evaluation to work
    return {"output": response2.choices[0].message.content.strip()}

# Test the chain
result = movie_rating_chain({
    "movie_description": "A clownfish searches for his missing son",
    "decade": "2000s"
})
print(f"Final rating: {result['output']}")

"""
Custom Metric: RatingMatch
Scores 1 if output matches expected_output, else 0
"""

class RatingMatch(base_metric.BaseMetric):
    def __init__(self, name: str = "RatingMatch"):
        self.name = name
    
    def score(self, output: str, expected_output: str, **ignored_kwargs: Any):
        # Compare output with expected_output (case-insensitive and stripped)
        match = output.strip().upper() == expected_output.strip().upper()
        
        return score_result.ScoreResult(
            name=self.name,
            value=1.0 if match else 0.0,
            reason=f"Output '{output}' {'matches' if match else 'does not match'} expected '{expected_output}'"
        )

"""
Evaluation using the dataset, movie_rating_chain, and RatingMatch metric
"""

# Create metric instance
rating_match_metric = RatingMatch()

# Run evaluation
evaluation = evaluate(
    dataset=dataset,
    task=movie_rating_chain,
    scoring_metrics=[rating_match_metric],
    experiment_name="movie eval 2",
    experiment_config={"description": "Evaluating movie rating chain eval test"},
)

print("Evaluation completed!")
print(evaluation)

