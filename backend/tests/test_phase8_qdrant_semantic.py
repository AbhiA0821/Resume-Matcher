import os
import sys
import uuid
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.embeddings import embed_text, EMBEDDING_DIMENSION
from app.services.qdrant_service import (
    get_qdrant_client,
    ensure_collection,
    RESUMES_COLLECTION,
    JOBS_COLLECTION
)
from app.services.resume_chunking import (
    chunk_text_deterministically,
    generate_deterministic_point_id,
    index_user_resume_vectors,
    search_resume_semantic
)
from app.services.job_indexing import (
    construct_job_text_representation,
    generate_deterministic_job_point_id,
    index_all_jobs,
    search_jobs_by_query_semantic,
    retrieve_matched_jobs_for_resume
)

def test_1_embedding_service_dimension():
    """Verify BAAI/bge-small-en-v1.5 generates 384D normalized vectors."""
    vec = embed_text("Senior Full Stack Software Engineer specializing in Python and React")
    assert isinstance(vec, list)
    assert len(vec) == EMBEDDING_DIMENSION
    assert len(vec) == 384

def test_2_qdrant_cloud_collections_creation():
    """Verify safe creation and reuse of hireagent_resumes and hireagent_jobs collections in Qdrant Cloud."""
    assert ensure_collection(RESUMES_COLLECTION) is True
    assert ensure_collection(JOBS_COLLECTION) is True

def test_3_deterministic_chunking_and_point_ids():
    """Verify deterministic text chunking and point ID generation."""
    sample_text = (
        "Alice Smith\nPython Developer with 5 years experience in building high-scale APIs using FastAPI, PostgreSQL, and Redis.\n"
        "Proficient in Docker, Kubernetes, CI/CD pipelines, and AWS cloud infrastructure.\n"
        "Education: Bachelor of Science in Computer Science."
    )
    chunks = chunk_text_deterministically(sample_text)
    assert len(chunks) >= 1
    assert chunks[0]["chunk_id"] == "chunk_0"
    
    id1 = generate_deterministic_point_id(user_id=101, resume_id=1, chunk_id="chunk_0")
    id2 = generate_deterministic_point_id(user_id=101, resume_id=1, chunk_id="chunk_0")
    assert id1 == id2, "Deterministic point IDs for identical input must match exactly"

def test_4_user_isolation_security_verification():
    """EXPLICIT SECURITY TEST: User A data must NEVER be accessible or retrieved by User B."""
    user_a_id = 9991
    user_b_id = 9992
    resume_a_id = 8881
    
    sample_resume_text_a = (
        "CONFIDENTIAL RESUME USER A: Senior Machine Learning Specialist in Computer Vision, PyTorch, PySpark, and CUDA acceleration."
    )
    
    # 1. Index User A resume into Qdrant Cloud
    res_a = index_user_resume_vectors(user_id=user_a_id, resume_id=resume_a_id, extracted_text=sample_resume_text_a)
    assert res_a["status"] == "success"
    assert res_a["indexed_chunks"] > 0
    
    # 2. User A searches for Machine Learning -> SHOULD FIND USER A CHUNKS
    search_results_a = search_resume_semantic(user_id=user_a_id, query="PyTorch Machine Learning", limit=5)
    assert len(search_results_a) > 0
    assert any(r["user_id"] == user_a_id for r in search_results_a)
    
    # 3. User B searches for Machine Learning -> MUST RETURN 0 RESULTS (STRICT USER ISOLATION)
    search_results_b = search_resume_semantic(user_id=user_b_id, query="PyTorch Machine Learning", limit=5)
    assert len(search_results_b) == 0, "SECURITY VIOLATION: User B retrieved User A's resume vectors!"
    assert not any(r["user_id"] == user_a_id for r in search_results_b)

def test_5_idempotent_reindexing():
    """Verify that re-indexing the same resume updates vectors without creating duplicates."""
    user_id = 9993
    resume_id = 8882
    
    text_v1 = "Software Engineer with Python experience."
    res1 = index_user_resume_vectors(user_id, resume_id, text_v1)
    
    text_v2 = "Senior Lead Software Engineer with Python and Distributed Systems experience."
    res2 = index_user_resume_vectors(user_id, resume_id, text_v2)
    
    assert res2["status"] == "success"
    
    # Search for user_id and verify results reflect updated text
    results = search_resume_semantic(user_id=user_id, query="Distributed Systems", limit=5)
    assert len(results) > 0
    assert "Distributed Systems" in results[0]["text"]

def test_6_job_indexing_and_semantic_retrieval():
    """Verify job catalog indexing and semantic retrieval against user resume."""
    synthetic_jobs = [
        {
            "id": 7001,
            "job_title": "AI / ML Engineer",
            "company": "TechCorp India",
            "job_role": "Machine Learning Engineer",
            "required_skills": "Python, PyTorch, TensorFlow, Deep Learning",
            "experience_level": "3-5 years",
            "description": "Develop and deploy scalable machine learning models and deep learning pipelines."
        },
        {
            "id": 7002,
            "job_title": "Classical Violinist Instructor",
            "company": "Symphony Academy",
            "job_role": "Music Teacher",
            "required_skills": "Violin, Orchestral Performance, Music Theory",
            "experience_level": "5+ years",
            "description": "Teach classical violin compositions and orchestral arrangements."
        }
    ]
    
    # Index synthetic jobs
    job_idx_res = index_all_jobs(synthetic_jobs)
    assert job_idx_res["status"] == "success"
    assert job_idx_res["indexed_count"] == 2
    
    # Semantic search query for AI/ML
    job_search_results = search_jobs_by_query_semantic(query_text="Machine Learning Deep Learning PyTorch", limit=2)
    assert len(job_search_results) > 0
    top_job = job_search_results[0]
    assert top_job["job_id"] == 7001
    assert "AI / ML Engineer" in top_job["job_title"]
    
    # Semantic resume-to-job match for User A (from test 4)
    matched_jobs = retrieve_matched_jobs_for_resume(user_id=9991, resume_id=8881, top_k=2)
    assert len(matched_jobs) > 0
    assert matched_jobs[0]["job_id"] == 7001
