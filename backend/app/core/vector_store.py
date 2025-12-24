from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Tuple

from app.core.config import settings
from sqlalchemy import select
from sqlalchemy.sql import text
from app.database.db import get_db
class VectorStore:
    """Manage embeddings and vector similarity search with cosine similarity"""


    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        model_name = embedding_model
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = self.model.encode(texts, normalize_embeddings=True, batch_size=32)
        return embeddings.tolist()
    
    def find_similar_jobs_for_cv(self, cv_id: int, job_ids:List[int]) -> List[Tuple[int, float]]:
        """Find most similarity between vectors in the vector store"""
        query = text("""
        SELECT
            j.job_id,
            1 - (c.embedding <=> j.embedding) AS similarity_score
        FROM cv_embeddings c
        JOIN job_embeddings j
            ON j.job_id = ANY(:job_ids)
        WHERE c.cv_id = :cv_id
        ORDER BY similarity_score DESC
        """)

        db = next(get_db())
        result = db.execute(
            query,
            {
                "cv_id": cv_id,
                "job_ids": job_ids
            }
        ).fetchall()

        return result


    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
    

    


vector_store = VectorStore(settings.EMBEDDING_MODEL)