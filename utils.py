import json

def strip_quotes(text):
    if text is None or not text: # Handle None and empty string explicitly
        return text

    first_char = text[0]
    last_char = text[-1]

    if (first_char == "'" and last_char == "'") or (first_char == '"' and last_char == '"'):
        return text[1:-1]
    else:
        return text

def parse_json_attribute(value):
    """
    Attempts to parse a string as JSON.
    Returns the parsed JSON object if successful, or the original string if not.
    """
    if value is None or not value:
        return value
        
    # Strip quotes first if present
    value = strip_quotes(value)
    
    # Try to parse as JSON
    if value.startswith('{') and value.endswith('}'):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value
