import numpy as np
from sentence_transformers import SentenceTransformer
import os

class VectorService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorService, cls).__new__(cls)
            cls._instance.model = SentenceTransformer('all-MiniLM-L6-v2')
        return cls._instance

    def generate_embedding(self, text: str) -> bytes:
        """
        Generates an embedding for the given text and returns it as bytes.
        """
        if not text:
            return b""
        embedding = self.model.encode(text)
        # Convert to float32 numpy array and then to bytes
        return np.array(embedding, dtype=np.float32).tobytes()

    def calculate_similarity(self, vec1_bytes: bytes, vec2_bytes: bytes) -> float:
        """
        Calculates cosine similarity between two byte-encoded vectors.
        """
        if not vec1_bytes or not vec2_bytes:
            return 0.0
            
        vec1 = np.frombuffer(vec1_bytes, dtype=np.float32)
        vec2 = np.frombuffer(vec2_bytes, dtype=np.float32)

        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(vec1, vec2) / (norm1 * norm2))

vector_service = VectorService()
