import json
import os
from typing import Dict

VALIDATION_CRITERIA_DESCRIPTION_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/validation_criteria_description.json'))

def get_validation_criteria_description()-> Dict[str, str]:
    with open(VALIDATION_CRITERIA_DESCRIPTION_FILE_PATH, 'r') as f:
        data = json.load(f)
        return data
