from qdrant_client import QdrantClient

COLLECTION_NAME = "job_embeddings"
QDRANT_PATH = "models/qdrant_storage"

class RetrievalService:
    """
    Searches Qdrant vector DB for similar jobs.
    Given a candidate embedding, returns top-K matching jobs.
    """
    def __init__(self):
        print("Loading Retrieval Service...")
        self.client = QdrantClient(path=QDRANT_PATH)
        self.collection = COLLECTION_NAME
        print("Retrieval Service ready")

    def search(self, query_vector: list, top_k: int = 100) -> list:
        """
        Search for top_k similar jobs using ANN search.
        Returns list of job payloads with scores.
        """
        results = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=top_k,
        ).points

        jobs = []
        for result in results:
            job = result.payload.copy()
            job["retrieval_score"] = round(result.score, 4)
            jobs.append(job)

        return jobs