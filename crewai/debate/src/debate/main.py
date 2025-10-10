#!/usr/bin/env python
import warnings
from debate.crew import Debate
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {'motion': 'Love exists in the world'}
    
    try:
        result = Debate().crew().kickoff(inputs=inputs)
        print(result)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

