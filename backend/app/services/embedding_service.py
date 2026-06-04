import os
import json
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    """
    Converts text into 384-dim vectors using bi-encoder.
    Simple in-memory cache to avoid re-encoding same text.
    """
    def __init__(self):
        print("Loading Embedding Service...")
        self.model = SentenceTransformer("models/biencoder_model")
        self.cache = {}
        print("Embedding Service ready")

    def embed(self, text: str) -> list:
        # Check cache first
        cache_key = hash(text[:200])
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Generate embedding
        embedding = self.model.encode(text).tolist()

        # Store in cache (max 1000 entries)
        if len(self.cache) < 1000:
            self.cache[cache_key] = embedding

        return embedding

    def embed_batch(self, texts: list) -> list:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()