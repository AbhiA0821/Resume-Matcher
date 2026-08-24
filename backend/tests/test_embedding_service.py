import os
import sys
import math
import pytest

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.embeddings import embed_text, embed_texts, EMBEDDING_DIMENSION

def dot_product(v1: list, v2: list) -> float:
    """Computes dot product between two float vectors. For L2-normalized vectors, this equals cosine similarity."""
    return sum(a * b for a, b in zip(v1, v2))

def test_1_basic_embedding():
    """Test 1 — Basic embedding generation for a single string input."""
    text = "Python backend developer"
    vector = embed_text(text)
    
    assert isinstance(vector, list), "Output must be a Python list"
    assert len(vector) == EMBEDDING_DIMENSION, f"Vector dimension must be {EMBEDDING_DIMENSION}"
    assert all(isinstance(x, float) for x in vector), "Vector elements must be floats"
    assert all(math.isfinite(x) for x in vector), "All vector elements must be finite numbers"

def test_2_batch_embedding():
    """Test 2 — Batch embedding generation for multiple inputs preserving ordering."""
    batch_texts = [
        "Python backend developer",
        "Machine learning engineer"
    ]
    vectors = embed_texts(batch_texts)
    
    assert isinstance(vectors, list), "Batch output must be a list of vectors"
    assert len(vectors) == 2, "Batch output must match input list length"
    
    vec1, vec2 = vectors[0], vectors[1]
    assert len(vec1) == EMBEDDING_DIMENSION
    assert len(vec2) == EMBEDDING_DIMENSION
    assert all(math.isfinite(x) for x in vec1)
    assert all(math.isfinite(x) for x in vec2)
    
    # Ordering verification: vec1 and vec2 should not be identical
    assert vec1 != vec2, "Embeddings for distinct texts must be distinct"

def test_3_empty_input():
    """Test 3 — Empty string input validation error handling."""
    with pytest.raises(ValueError, match="cannot be empty"):
        embed_text("")

def test_4_whitespace_input():
    """Test 4 — Whitespace-only string input validation error handling."""
    with pytest.raises(ValueError, match="cannot be empty"):
        embed_text("   ")

def test_5_semantic_similarity_smoke_test():
    """Test 5 — Semantic similarity smoke test demonstrating relative vector proximity."""
    query = "Python backend developer"
    related = "Backend engineer using Python"
    unrelated = "Classical music performance"
    
    v_query = embed_text(query)
    v_related = embed_text(related)
    v_unrelated = embed_text(unrelated)
    
    # Dot product on L2-normalized embeddings equals cosine similarity
    sim_related = dot_product(v_query, v_related)
    sim_unrelated = dot_product(v_query, v_unrelated)
    
    assert sim_related > sim_unrelated, (
        f"Semantically related pair similarity ({sim_related:.4f}) "
        f"must be higher than unrelated pair similarity ({sim_unrelated:.4f})"
    )
