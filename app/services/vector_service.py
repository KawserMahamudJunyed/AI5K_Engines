"""Service for semantic vector embeddings."""
from __future__ import annotations

import os

# Load model lazily to save memory during startup
_model = None

def get_model():
    global _model
    if _model is None:
        # Import lazily to avoid heavy ML loading unless actually needed
        from sentence_transformers import SentenceTransformer
        # Use a lightweight, fast model for CPU embeddings
        # We set an environment variable to prevent it from downloading repeatedly in some environments
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model
async def generate_embedding(text: str) -> list[float]:
    """
    Generate a 384-dimensional vector embedding for the given text.
    
    Args:
        text: The string to embed (e.g. 'FastAPI developer' or a required skill)
        
    Returns:
        A list of floats representing the semantic vector.
    """
    if not text or not text.strip():
        return [0.0] * 384
        
    model = get_model()
    # encode returns a numpy array. We convert to standard float list for pgvector.
    embedding = model.encode(text.strip())
    return embedding.tolist()
