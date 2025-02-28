def strip_quotes(text):
    if text is None or not text: # Handle None and empty string explicitly
        return text

    first_char = text[0]
    last_char = text[-1]

    if (first_char == "'" and last_char == "'") or (first_char == '"' and last_char == '"'):
        return text[1:-1]
    else:
        return text
