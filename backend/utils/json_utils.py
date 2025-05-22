#json_utils.py
import re
import json
import string
import ast
from typing import Dict, Optional

def pre_process_the_json_response(response: str) -> str:
    """
    Cleans LLM-generated response that may be wrapped in Markdown code blocks like ```json ... ```.
    Removes triple backticks and any leading 'json' tag. Filters out non-printable characters.
    """
    # Remove markdown-style code fencing and optional 'json' tag
    response = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip(), flags=re.IGNORECASE)

    # Remove non-printable characters
    response = "".join(char for char in response if char in string.printable)

    return response

def load_object_from_string(s: str) -> Optional[Dict]:
    """
    Attempts to load a string as JSON first, then falls back to ast.literal_eval if needed.
    """
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(s)
        except (ValueError, SyntaxError) as e:
            raise Exception("Failed to parse string as JSON or Python literal.") from e

def parse_response_string(response: str) -> Optional[Dict]:
    """
    Safely parses a raw LLM response string into a Python dict.
    Returns None if parsing fails.
    """
    try:
        cleaned = pre_process_the_json_response(response)
        obj = load_object_from_string(cleaned)
        return obj
    except Exception as e:
        print(f"⚠️ Error parsing response string: {e}")
        return None
