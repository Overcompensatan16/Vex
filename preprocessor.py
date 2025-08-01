def preprocess_fact(fact_str, mode="generalized", verbose=True):
    """
    Preprocess a fact string.
    - Strips whitespace and lowers case.
    - In 'generalized' mode: adds both specific and general forms (e.g. danger=wolf → danger=wolf, danger)
    - In 'verbose' mode: keeps only the specific form (e.g. danger=wolf)
    """
    fact_str = fact_str.strip().lower()
    facts = [fact_str]

    if '=' in fact_str and mode == "generalized":
        key, _ = fact_str.split('=', 1)
        key = key.strip()
        facts.append(key)

    if verbose:
        print(f"[PREPROCESSOR] Mode: {mode} | Input: '{fact_str}' -> Preprocessed: {facts}")

    return facts

