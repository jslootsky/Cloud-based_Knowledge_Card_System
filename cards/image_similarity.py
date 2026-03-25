from __future__ import annotations

from math import sqrt

#from example code
def parse_signature(signature: str) -> list[float]:
    #if empty or None, return empty list
    if not signature:
        return []
    try:
        #split string by commas, convert each piece into a float, ignore empty values
        return [float(value) for value in signature.split(',') if value]
    except ValueError as exc:
        #if anything cannot be converted to a float, raise a custom error
        raise ValueError("Invalid Histogram Signature") from exc

def compare_image_similarity(query_signature: str, stored_signature: str) -> float:
    """
    TODO(student): compare two histogram signatures and return similarity in [0.0, 1.0].
    HINT: you can parse comma-separated floats and use cosine similarity.
    """
    #convert signatures into numeric vectors 
    vector_a = parse_signature(query_signature)
    vector_b = parse_signature(stored_signature)

    #validate if exists and check if same length (dot product impossible otherwise)
    if not vector_a or not vector_b or len(vector_a) != len(vector_b):
        raise ValueError("Histogram signatures are missing or incompatible.")
    
    #compute dot product
    #sum(a1*b1, a2*b2, ..., an*bn)
    dot = sum(a * b for a, b in zip(vector_a, vector_b))

    #find magnitude of vec a
    norm_a = sqrt(sum(a * a for a in vector_a))

    #find magnitude of vec b
    norm_b = sqrt(sum(b * b for b in vector_b))

    #if either has mag 0 cosine similarity is undefined
    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)
