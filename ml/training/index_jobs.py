import pandas as pd
import os
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    OptimizersConfigDiff,
)

# ── Configuration ──────────────────────────────────────────
PROCESSED_PATH = "ml/data/processed/jobs_clean.csv"
MODEL_PATH = "models/biencoder_model"
QDRANT_PATH = "models/qdrant_storage"
COLLECTION_NAME = "job_embeddings"
BATCH_SIZE = 64
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 outputs 384-dim vectors

os.makedirs(QDRANT_PATH, exist_ok=True)


# ── Connect to Qdrant (local mode) ─────────────────────────
def get_qdrant_client():
    """
    Local mode: stores data in a folder on your machine.
    No Docker needed.
    In production: QdrantClient(host="localhost", port=6333)
    One line change to switch to server mode.
    """
    client = QdrantClient(path=QDRANT_PATH)
    return client


# ── Create collection ──────────────────────────────────────
def create_collection(client):
    """
    A collection in Qdrant is like a table in SQL.
    We store job embeddings here.

    VectorParams:
      size     = dimension of our embeddings (384)
      distance = how we measure similarity (Cosine)

    Cosine similarity is best for text embeddings because
    it measures the ANGLE between vectors, not magnitude.
    Two texts about the same topic will have similar angles
    regardless of their length.
    """
    # Delete if exists (fresh start)
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in existing:
        print(f"Deleting existing collection: {COLLECTION_NAME}")
        client.delete_collection(COLLECTION_NAME)

    # Create new collection
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
        optimizers_config=OptimizersConfigDiff(
            indexing_threshold=0,  # Index immediately
        ),
    )
    print(f"Created collection: {COLLECTION_NAME}")
    print(f"Vector size: {VECTOR_SIZE}")
    print(f"Distance metric: Cosine")


# ── Load and embed jobs ────────────────────────────────────
def embed_and_index(df, model, client):
    """
    For each job posting:
    1. Convert text to 384-dim vector using bi-encoder
    2. Store vector + metadata in Qdrant

    Metadata (payload) stored alongside each vector:
    - job_id
    - title
    - company_name
    - location
    - experience_level
    - skills (extracted)
    - combined_text preview
    """
    print(f"\nEmbedding and indexing {len(df)} job postings...")
    print("This will take 2-3 minutes...")

    total_indexed = 0

    # Process in batches for efficiency
    for batch_start in tqdm(range(0, len(df), BATCH_SIZE)):
        batch_end = min(batch_start + BATCH_SIZE, len(df))
        batch_df = df.iloc[batch_start:batch_end]

        # Get texts for this batch
        texts = batch_df["combined_text"].tolist()

        # Generate embeddings
        embeddings = model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        # Create Qdrant points
        points = []
        for i, (_, row) in enumerate(batch_df.iterrows()):
            point = PointStruct(
                id=int(row["job_id"]) if str(row["job_id"]).isdigit()
                   else batch_start + i,
                vector=embeddings[i].tolist(),
                payload={
                    "job_id": str(row["job_id"]),
                    "title": str(row["title"]),
                    "company_name": str(row["company_name"]),
                    "location": str(row["location"]),
                    "experience_level": str(row["formatted_experience_level"]),
                    "work_type": str(row["formatted_work_type"]),
                    "remote_allowed": bool(row["remote_allowed"]),
                    "text_preview": str(row["combined_text"])[:300],
                },
            )
            points.append(point)

        # Upsert batch into Qdrant
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )
        total_indexed += len(points)

    print(f"\nIndexed {total_indexed} job postings into Qdrant")
    return total_indexed


# ── Verify indexing ────────────────────────────────────────
def verify_index(client):
    info = client.get_collection(COLLECTION_NAME)
    print(f"\nCollection info:")
    print(f"  Name:          {COLLECTION_NAME}")
    print(f"  Total vectors: {info.points_count}")
    print(f"  Vector size:   {info.config.params.vectors.size}")
    print(f"  Distance:      {info.config.params.vectors.distance}")


# ── Test search ────────────────────────────────────────────
def test_search(client, model):
    """
    Test that we can search the index correctly.
    This simulates what happens when a candidate
    uploads their resume and we find matching jobs.
    """
    print("\n" + "=" * 55)
    print("Testing Vector Search")
    print("=" * 55)

    test_queries = [
        "Python machine learning engineer with PyTorch and AWS",
        "Frontend developer with React JavaScript and TypeScript",
        "Data engineer with Spark Kafka and Airflow pipelines",
    ]

    for query in test_queries:
        # Encode the query
        query_vector = model.encode(query).tolist()

        # Search Qdrant for top 3 matches
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=3,
        ).points

        print(f"\nQuery: {query}")
        print("Top 3 matches:")
        for i, result in enumerate(results):
            print(f"  {i+1}. Score: {result.score:.4f}")
            print(f"     Title:   {result.payload['title']}")
            print(f"     Company: {result.payload['company_name']}")
            print(f"     Level:   {result.payload['experience_level']}")


# ── Main ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("TalentLens — Job Embedding Indexing")
    print("=" * 55)

    # Load data
    print("\nLoading job postings...")
    df = pd.read_csv(PROCESSED_PATH)
    print(f"Loaded {len(df)} job postings")

    # Load bi-encoder model
    print(f"\nLoading bi-encoder model from {MODEL_PATH}...")
    model = SentenceTransformer(MODEL_PATH)
    print("Model loaded successfully")

    # Connect to Qdrant
    print(f"\nConnecting to Qdrant (local mode)...")
    client = get_qdrant_client()
    print("Connected successfully")

    # Create collection
    create_collection(client)

    # Embed and index all jobs
    embed_and_index(df, model, client)

    # Verify
    verify_index(client)

    # Test search
    test_search(client, model)

    print("\n" + "=" * 55)
    print("Indexing Complete!")
    print("All job embeddings stored in Qdrant")
    print(f"Storage location: {QDRANT_PATH}")
    print("=" * 55)