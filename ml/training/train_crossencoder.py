import json
import os
import random
import mlflow
from sentence_transformers import CrossEncoder
from sentence_transformers.cross_encoder.evaluation import (
    CEBinaryClassificationEvaluator,
)
from torch.utils.data import DataLoader
from sentence_transformers import InputExample

# ── Configuration ──────────────────────────────────────────
MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
TRAIN_PATH = "ml/data/processed/biencoder_train.json"
VAL_PATH = "ml/data/processed/biencoder_val.json"
OUTPUT_DIR = "models/crossencoder_model"
MLFLOW_EXPERIMENT = "talentlens-crossencoder"

EPOCHS = 3
BATCH_SIZE = 16
LEARNING_RATE = 2e-5

os.makedirs(OUTPUT_DIR, exist_ok=True)
random.seed(42)


# ── Load data ──────────────────────────────────────────────
def load_pairs(path):
    with open(path, "r") as f:
        return json.load(f)


# ── Create training examples ───────────────────────────────
def create_cross_encoder_examples(pairs, negative_ratio=1):
    """
    Cross-encoder needs BOTH positive and negative pairs.
    
    Positive pair (label=1): job + matching candidate
    Negative pair (label=0): job + random non-matching candidate
    
    We create negatives by randomly pairing jobs with
    candidates from DIFFERENT jobs. This teaches the model
    to distinguish genuine matches from random pairs.
    """
    examples = []
    
    # All candidate texts for creating negatives
    all_candidates = [p["positive"] for p in pairs]
    all_jobs = [p["anchor"] for p in pairs]
    
    for i, pair in enumerate(pairs):
        job_text = pair["anchor"]
        matching_candidate = pair["positive"]
        
        # Positive example — genuine match
        examples.append(InputExample(
            texts=[job_text, matching_candidate],
            label=1.0,
        ))
        
        # Negative examples — random non-matching candidates
        for _ in range(negative_ratio):
            # Pick a random candidate that is NOT from this job
            neg_idx = random.randint(0, len(all_candidates) - 1)
            # Make sure it is not the same job
            attempts = 0
            while neg_idx == i and attempts < 5:
                neg_idx = random.randint(0, len(all_candidates) - 1)
                attempts += 1
            
            negative_candidate = all_candidates[neg_idx]
            examples.append(InputExample(
                texts=[job_text, negative_candidate],
                label=0.0,
            ))
    
    return examples


# ── Create evaluator ───────────────────────────────────────
def create_evaluator(val_pairs):
    """
    Binary classification evaluator:
    - Positive pairs should score close to 1.0
    - Negative pairs should score close to 0.0
    - Reports AUC (Area Under Curve) and AP (Average Precision)
    """
    sentence_pairs = []
    labels = []
    
    all_candidates = [p["positive"] for p in val_pairs]
    
    for i, pair in enumerate(val_pairs[:200]):
        # Positive pair
        sentence_pairs.append([pair["anchor"], pair["positive"]])
        labels.append(1)
        
        # Negative pair
        neg_idx = random.randint(0, len(all_candidates) - 1)
        while neg_idx == i:
            neg_idx = random.randint(0, len(all_candidates) - 1)
        sentence_pairs.append([pair["anchor"], all_candidates[neg_idx]])
        labels.append(0)
    
    evaluator = CEBinaryClassificationEvaluator(
        sentence_pairs=sentence_pairs,
        labels=labels,
        name="job-candidate-eval",
    )
    return evaluator


# ── Main training ──────────────────────────────────────────
def train():
    print("=" * 55)
    print("TalentLens Cross-Encoder Training")
    print("=" * 55)
    
    mlflow.set_experiment(MLFLOW_EXPERIMENT)
    
    # Load data
    print("\nLoading training pairs...")
    train_pairs = load_pairs(TRAIN_PATH)
    val_pairs = load_pairs(VAL_PATH)
    print(f"Train: {len(train_pairs)} | Val: {len(val_pairs)}")
    
    # Load cross-encoder model
    # ms-marco-MiniLM-L-6-v2:
    # - Pre-trained on MS MARCO passage ranking dataset
    # - Small and fast (6 layers)
    # - Perfect for re-ranking tasks
    print(f"\nLoading cross-encoder: {MODEL_NAME}")
    model = CrossEncoder(
        MODEL_NAME,
        num_labels=1,
        max_length=512,
    )
    print("Model loaded successfully")
    
    # Create training examples with negatives
    print("\nCreating training examples...")
    train_examples = create_cross_encoder_examples(
        train_pairs[:2000],  # Use first 2000 for speed
        negative_ratio=1,    # 1 negative per positive
    )
    print(f"Total examples: {len(train_examples)}")
    print(f"  Positive pairs: {len(train_examples) // 2}")
    print(f"  Negative pairs: {len(train_examples) // 2}")
    
    # Create evaluator
    evaluator = create_evaluator(val_pairs)
    
    # Calculate steps
    steps_per_epoch = len(train_examples) // BATCH_SIZE
    warmup_steps = steps_per_epoch // 10
    print(f"\nSteps per epoch: {steps_per_epoch}")
    print(f"Warmup steps: {warmup_steps}")
    
    # Train with MLflow tracking
    print("\nStarting training...")
    with mlflow.start_run(run_name="crossencoder-minilm-v1"):
        
        mlflow.log_params({
            "base_model": MODEL_NAME,
            "epochs": EPOCHS,
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
            "train_examples": len(train_examples),
            "negative_ratio": 1,
        })
        
        model.fit(
            train_dataloader=DataLoader(
                train_examples,
                shuffle=True,
                batch_size=BATCH_SIZE,
            ),
            evaluator=evaluator,
            epochs=EPOCHS,
            warmup_steps=warmup_steps,
            output_path=OUTPUT_DIR,
            show_progress_bar=True,
        )
        
        print(f"\nModel saved to: {OUTPUT_DIR}")
        print(f"MLflow Run ID: {mlflow.active_run().info.run_id}")
    
    print("\n" + "=" * 55)
    print("Cross-Encoder Training Complete!")
    print("=" * 55)


# ── Test inference ─────────────────────────────────────────
def test_inference():
    print("\nTesting cross-encoder re-ranking...")
    model = CrossEncoder(OUTPUT_DIR, max_length=512)
    
    job = "Senior Machine Learning Engineer with Python PyTorch AWS. Build recommendation systems."
    
    # Simulate top-5 candidates retrieved by bi-encoder
    candidates = [
        "Senior ML engineer 6 years Python PyTorch AWS. Built production recommendation systems.",
        "Junior web developer React JavaScript 1 year experience frontend only.",
        "Data scientist pandas scikit-learn SQL 4 years data analysis.",
        "NLP researcher BERT transformers Python deep learning expertise.",
        "DevOps engineer Docker Kubernetes CI/CD pipelines cloud infrastructure.",
    ]
    
    print(f"\nJob: {job[:70]}...")
    print("\nRe-ranking candidates:")
    print("-" * 55)
    
    # Score all (job, candidate) pairs together
    pairs = [[job, candidate] for candidate in candidates]
    scores = model.predict(pairs)
    
    # Sort by score
    ranked = sorted(
        zip(scores, candidates),
        key=lambda x: x[0],
        reverse=True,
    )
    
    for rank, (score, candidate) in enumerate(ranked, 1):
        print(f"Rank {rank}: {score:.4f}")
        print(f"  {candidate[:70]}")
        print()
    
    print("Expected: ML engineer should be Rank 1")


if __name__ == "__main__":
    train()
    test_inference()