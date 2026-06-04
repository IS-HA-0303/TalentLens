from sentence_transformers import CrossEncoder

class RankingService:
    """
    Re-ranks retrieved jobs using cross-encoder.
    Takes (candidate_text, job_list) and returns
    jobs sorted by relevance score.
    """
    def __init__(self):
        print("Loading Ranking Service...")
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2",
            max_length=512,
        )
        print("Ranking Service ready")

    def rerank(self, query_text: str, jobs: list, top_k: int = 10) -> list:
        """
        Score each (query, job) pair and return top_k.
        """
        if not jobs:
            return []

        # Create pairs for cross-encoder
        pairs = [
            [query_text, job.get("text_preview", "")]
            for job in jobs
        ]

        # Score all pairs at once
        scores = self.model.predict(pairs)

        # Attach scores to jobs
        for job, score in zip(jobs, scores):
            job["rerank_score"] = round(float(score), 4)

        # Sort by rerank score descending
        ranked_jobs = sorted(
            jobs,
            key=lambda x: x["rerank_score"],
            reverse=True,
        )

        return ranked_jobs[:top_k]