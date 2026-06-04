import mlflow

# ── Log NER metrics ────────────────────────────────────────
mlflow.set_experiment("talentlens-ner")
with mlflow.start_run(run_name="ner-bert-v1-results"):
    mlflow.log_params({
        "model_name": "bert-base-uncased",
        "epochs": 1,
        "batch_size": 16,
        "learning_rate": "2e-05",
        "train_size": 2294,
        "val_size": 287,
        "labels": "O, B-SKILL, I-SKILL",
    })
    mlflow.log_metrics({
        "val_f1": 0.916,
        "val_precision": 0.883,
        "val_recall": 0.951,
        "val_accuracy": 0.9977,
        "test_f1": 0.916,
        "test_precision": 0.883,
        "test_recall": 0.951,
    })
print("NER metrics logged")

# ── Log Bi-encoder metrics ─────────────────────────────────
mlflow.set_experiment("talentlens-biencoder")
with mlflow.start_run(run_name="biencoder-minilm-results"):
    mlflow.log_params({
        "base_model": "all-MiniLM-L6-v2",
        "epochs": 3,
        "batch_size": 32,
        "learning_rate": "2e-05",
        "train_pairs": 8372,
        "val_pairs": 931,
        "loss": "MultipleNegativesRankingLoss",
    })
    mlflow.log_metrics({
        "recall_at_10": 0.850,
        "ndcg_at_10": 0.7488,
        "mrr_at_10": 0.7161,
        "cosine_accuracy_at_1": 0.645,
        "cosine_accuracy_at_3": 0.780,
        "cosine_accuracy_at_10": 0.850,
    })
print("Bi-encoder metrics logged")

# ── Log Cross-encoder metrics ──────────────────────────────
mlflow.set_experiment("talentlens-crossencoder")
with mlflow.start_run(run_name="crossencoder-minilm-results"):
    mlflow.log_params({
        "base_model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
        "epochs": 3,
        "batch_size": 16,
        "learning_rate": "2e-05",
        "train_examples": 4000,
        "negative_ratio": 1,
    })
    mlflow.log_metrics({
        "train_loss": 0.3317,
        "ranking_improvement": 0.15,
        "top1_accuracy": 0.92,
    })
print("Cross-encoder metrics logged")

print("\nAll metrics logged successfully!")
print("Refresh MLflow at http://127.0.0.1:5000")