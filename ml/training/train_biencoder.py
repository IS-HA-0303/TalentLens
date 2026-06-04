import json
import os
import mlflow
from sentence_transformers import (
    SentenceTransformer,
    InputExample,
    losses,
    evaluation,
)
from torch.utils.data import DataLoader
import torch

# ── Configuration ──────────────────────────────────────────
MODEL_NAME = "all-MiniLM-L6-v2"
TRAIN_PATH = "ml/data/processed/biencoder_train.json"
VAL_PATH = "ml/data/processed/biencoder_val.json"
OUTPUT_DIR = "models/biencoder_model"
MLFLOW_EXPERIMENT = "talentlens-biencoder"

EPOCHS = 3
BATCH_SIZE = 32
LEARNING_RATE = 2e-5
WARMUP_STEPS = 100

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("models", exist_ok=True)


# ── Load data ──────────────────────────────────────────────
def load_pairs(path):
    with open(path, "r") as f:
        return json.load(f)


# ── Create InputExamples ───────────────────────────────────
def create_examples(pairs):
    """
    Convert pairs to sentence-transformers InputExample format.
    For MultipleNegativesRankingLoss we only need
    (anchor, positive) pairs — no explicit negatives needed.
    Other items in the batch automatically become negatives.
    """
    examples = []
    for pair in pairs:
        examples.append(InputExample(
            texts=[pair["anchor"], pair["positive"]]
        ))
    return examples


# ── Create evaluator ───────────────────────────────────────
def create_evaluator(val_pairs, model):
    """
    Information Retrieval Evaluator:
    - Queries = candidate profiles
    - Corpus  = job postings
    - Checks if correct job is in top-K results
    - Reports Recall@10, MRR@10, NDCG@10
    """
    queries = {}
    corpus = {}
    relevant_docs = {}

    for i, pair in enumerate(val_pairs[:200]):  # Use first 200 for speed
        q_id = f"q_{i}"
        c_id = f"c_{i}"

        queries[q_id] = pair["positive"]    # candidate profile
        corpus[c_id] = pair["anchor"]       # job posting
        relevant_docs[q_id] = {c_id}        # this job is relevant to this candidate

    evaluator = evaluation.InformationRetrievalEvaluator(
        queries=queries,
        corpus=corpus,
        relevant_docs=relevant_docs,
        name="job-candidate-eval",
        show_progress_bar=False,
    )
    return evaluator


# ── Main training function ─────────────────────────────────
def train():
    print("=" * 55)
    print("TalentLens Bi-Encoder Training")
    print("=" * 55)

    # Set MLflow experiment
    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    # Load data
    print(f"\nLoading training pairs...")
    train_pairs = load_pairs(TRAIN_PATH)
    val_pairs = load_pairs(VAL_PATH)
    print(f"Train: {len(train_pairs)} | Val: {len(val_pairs)}")

    # Load base model
    # We use all-MiniLM-L6-v2 because:
    # - Smaller than BERT (22M params vs 110M)
    # - Faster inference (important for production)
    # - Already trained on sentence similarity tasks
    # - Perfect starting point for fine-tuning
    print(f"\nLoading base model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    # Create training examples
    print("Creating training examples...")
    train_examples = create_examples(train_pairs)
    print(f"Training examples: {len(train_examples)}")

    # Create dataloader
    train_dataloader = DataLoader(
        train_examples,
        shuffle=True,
        batch_size=BATCH_SIZE,
    )

    # Loss function: MultipleNegativesRankingLoss
    # This is the key loss for bi-encoder training.
    # For each (job, candidate) positive pair in a batch:
    # - The matching candidate is the positive
    # - All other candidates in the batch are negatives
    # - Model learns to rank positive higher than all negatives
    # This is the same loss used by OpenAI, Google, and Meta
    # for their embedding models
    train_loss = losses.MultipleNegativesRankingLoss(model)

    # Create evaluator
    print("Creating evaluator...")
    evaluator = create_evaluator(val_pairs, model)

    # Calculate training steps
    steps_per_epoch = len(train_dataloader)
    total_steps = steps_per_epoch * EPOCHS
    print(f"\nSteps per epoch: {steps_per_epoch}")
    print(f"Total steps: {total_steps}")
    print(f"Warmup steps: {WARMUP_STEPS}")

    # Train with MLflow tracking
    print("\nStarting training...")

    with mlflow.start_run(run_name="biencoder-minilm-v1"):

        # Log hyperparameters
        mlflow.log_params({
            "base_model": MODEL_NAME,
            "epochs": EPOCHS,
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
            "warmup_steps": WARMUP_STEPS,
            "train_pairs": len(train_pairs),
            "val_pairs": len(val_pairs),
            "loss": "MultipleNegativesRankingLoss",
        })

        # Train the model
        model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            evaluator=evaluator,
            epochs=EPOCHS,
            evaluation_steps=steps_per_epoch,  # Evaluate once per epoch
            warmup_steps=WARMUP_STEPS,
            output_path=OUTPUT_DIR,
            show_progress_bar=True,
            optimizer_params={"lr": LEARNING_RATE},
        )

        # Load best model (saved automatically by sentence-transformers)
        best_model = SentenceTransformer(OUTPUT_DIR)

        # Final evaluation
        print("\nRunning final evaluation...")
        final_score = evaluator(best_model)
        print(f"Final evaluator score: {final_score}")

        # Log final score
        mlflow.log_metric("final_eval_score", final_score)

        print(f"\nModel saved to: {OUTPUT_DIR}")
        print(f"MLflow Run ID: {mlflow.active_run().info.run_id}")

    print("\n" + "=" * 55)
    print("Bi-Encoder Training Complete!")
    print("=" * 55)


# ── Test inference after training ─────────────────────────
def test_inference():
    print("\nTesting bi-encoder inference...")
    model = SentenceTransformer(OUTPUT_DIR)

    job = "Senior Machine Learning Engineer with Python, PyTorch and AWS. Build recommendation systems at scale."
    candidates = [
        "I am a senior ML engineer with 7 years experience in Python, PyTorch and AWS. Built production recommendation systems.",
        "Junior web developer with React and JavaScript. 1 year experience in frontend development.",
        "Data scientist with pandas, scikit-learn and SQL. 4 years in data analysis and visualization.",
        "DevOps engineer with Docker, Kubernetes and CI/CD pipelines. 5 years in cloud infrastructure.",
    ]

    job_embedding = model.encode(job)
    candidate_embeddings = model.encode(candidates)

    # Compute cosine similarities
    from sentence_transformers import util
    scores = util.cos_sim(job_embedding, candidate_embeddings)[0]

    print(f"\nJob: {job[:60]}...")
    print("\nCandidate Match Scores:")
    for i, (candidate, score) in enumerate(zip(candidates, scores)):
        print(f"  {score:.4f} | {candidate[:70]}...")

    print("\nExpected: First candidate should have highest score")


if __name__ == "__main__":
    train()
    test_inference()