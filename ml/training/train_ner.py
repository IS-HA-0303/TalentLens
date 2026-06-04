import json
import os
import numpy as np
import mlflow
import mlflow.pytorch
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer,
    DataCollatorForTokenClassification,
)
from datasets import Dataset
import evaluate
import torch

# ── Configuration ──────────────────────────────────────────
MODEL_NAME = "bert-base-uncased"
NER_TRAIN_PATH = "ml/data/processed/ner_train.json"
NER_VAL_PATH = "ml/data/processed/ner_val.json"
NER_TEST_PATH = "ml/data/processed/ner_test.json"
OUTPUT_DIR = "models/ner_model"
MLFLOW_EXPERIMENT = "talentlens-ner"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("models", exist_ok=True)

# ── Label definitions ──────────────────────────────────────
LABEL_LIST = ["O", "B-SKILL", "I-SKILL"]
LABEL2ID = {label: i for i, label in enumerate(LABEL_LIST)}
ID2LABEL = {i: label for i, label in enumerate(LABEL_LIST)}

# ── Load data ──────────────────────────────────────────────
def load_ner_data(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data


# ── Tokenize and align labels ──────────────────────────────
def tokenize_and_align_labels(examples, tokenizer):
    """
    BERT uses subword tokenization.
    "TensorFlow" might become ["Tensor", "##Flow"]
    We need to align our word-level labels to subword tokens.
    Only the first subword of each word gets the real label.
    Continuation subwords get -100 (ignored in loss).
    """
    tokenized = tokenizer(
        examples["tokens"],
        truncation=True,
        is_split_into_words=True,
        max_length=512,
        padding=False,
    )

    all_labels = []
    for i, label_list in enumerate(examples["labels"]):
        word_ids = tokenized.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []

        for word_idx in word_ids:
            if word_idx is None:
                # Special tokens [CLS] and [SEP] → ignore
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                # First subword of a word → use real label
                label_str = label_list[word_idx] if word_idx < len(label_list) else "O"
                label_ids.append(LABEL2ID.get(label_str, 0))
            else:
                # Continuation subword → ignore in loss
                label_ids.append(-100)

            previous_word_idx = word_idx

        all_labels.append(label_ids)

    tokenized["labels"] = all_labels
    return tokenized


# ── Compute metrics ────────────────────────────────────────
def get_compute_metrics(label_list):
    seqeval = evaluate.load("seqeval")

    def compute_metrics(eval_preds):
        logits, labels = eval_preds
        predictions = np.argmax(logits, axis=2)

        true_predictions = [
            [label_list[p] for p, l in zip(prediction, label)
             if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [label_list[l] for p, l in zip(prediction, label)
             if l != -100]
            for prediction, label in zip(predictions, labels)
        ]

        results = seqeval.compute(
            predictions=true_predictions,
            references=true_labels
        )
        return {
            "precision": results["overall_precision"],
            "recall": results["overall_recall"],
            "f1": results["overall_f1"],
            "accuracy": results["overall_accuracy"],
        }

    return compute_metrics


# ── Main training function ─────────────────────────────────
def train():
    print("=" * 50)
    print("TalentLens NER Model Training")
    print("=" * 50)

    # Set MLflow experiment
    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    # Load tokenizer
    print(f"\nLoading tokenizer: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Load raw data
    print("Loading training data...")
    train_data = load_ner_data(NER_TRAIN_PATH)
    val_data = load_ner_data(NER_VAL_PATH)
    test_data = load_ner_data(NER_TEST_PATH)

    print(f"Train: {len(train_data)} | Val: {len(val_data)} | Test: {len(test_data)}")

    # Convert to HuggingFace Dataset format
    def to_hf_dataset(data):
        return Dataset.from_dict({
            "tokens": [d["tokens"] for d in data],
            "labels": [d["labels"] for d in data],
        })

    train_dataset = to_hf_dataset(train_data)
    val_dataset = to_hf_dataset(val_data)
    test_dataset = to_hf_dataset(test_data)

    # Tokenize datasets
    print("Tokenizing datasets...")
    train_tokenized = train_dataset.map(
        lambda x: tokenize_and_align_labels(x, tokenizer),
        batched=True,
        remove_columns=["tokens", "labels"],
    )
    val_tokenized = val_dataset.map(
        lambda x: tokenize_and_align_labels(x, tokenizer),
        batched=True,
        remove_columns=["tokens", "labels"],
    )
    test_tokenized = test_dataset.map(
        lambda x: tokenize_and_align_labels(x, tokenizer),
        batched=True,
        remove_columns=["tokens", "labels"],
    )

    # Load model
    print(f"Loading model: {MODEL_NAME}")
    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(LABEL_LIST),
        id2label=ID2LABEL,
        label2id=LABEL2ID,
        ignore_mismatched_sizes=True,
    )

    # Data collator handles padding
    data_collator = DataCollatorForTokenClassification(tokenizer)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        learning_rate=2e-5,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=50,
        fp16=False,  # Set True if you have GPU
        report_to="none",  # We handle MLflow manually
    )

    # Trainer
    trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_tokenized,
    eval_dataset=val_tokenized,
    processing_class=tokenizer,
    data_collator=data_collator,
    compute_metrics=get_compute_metrics(LABEL_LIST),
    )

    # Train with MLflow tracking
    print("\nStarting training...")
    with mlflow.start_run(run_name="ner-bert-v1"):

        # Log hyperparameters
        mlflow.log_params({
            "model_name": MODEL_NAME,
            "epochs": 3,
            "batch_size": 16,
            "learning_rate": 2e-5,
            "train_size": len(train_data),
            "val_size": len(val_data),
            "labels": str(LABEL_LIST),
        })

        # Train
        trainer.train()

        # Evaluate on validation set
        print("\nEvaluating on validation set...")
        val_results = trainer.evaluate(val_tokenized)
        print(f"Validation F1:        {val_results['eval_f1']:.4f}")
        print(f"Validation Precision: {val_results['eval_precision']:.4f}")
        print(f"Validation Recall:    {val_results['eval_recall']:.4f}")

        # Evaluate on test set
        print("\nEvaluating on test set...")
        test_results = trainer.evaluate(test_tokenized)
        print(f"Test F1:        {test_results['eval_f1']:.4f}")
        print(f"Test Precision: {test_results['eval_precision']:.4f}")
        print(f"Test Recall:    {test_results['eval_recall']:.4f}")

        # Log metrics to MLflow
        mlflow.log_metrics({
            "val_f1": val_results["eval_f1"],
            "val_precision": val_results["eval_precision"],
            "val_recall": val_results["eval_recall"],
            "test_f1": test_results["eval_f1"],
            "test_precision": test_results["eval_precision"],
            "test_recall": test_results["eval_recall"],
        })

        # Save model
        print(f"\nSaving model to {OUTPUT_DIR}...")
        trainer.save_model(OUTPUT_DIR)
        tokenizer.save_pretrained(OUTPUT_DIR)

        # Log model to MLflow
        mlflow.pytorch.log_model(model, "ner_model")

        print("\nMLflow run complete!")
        print(f"Run ID: {mlflow.active_run().info.run_id}")

    print("\n" + "=" * 50)
    print("NER Training Complete!")
    print("=" * 50)


# ── Quick test after training ──────────────────────────────
def test_inference(text):
    """Test the trained model on a sample text"""
    from transformers import pipeline

    print(f"\nTesting inference on: '{text}'")
    ner_pipeline = pipeline(
        "ner",
        model=OUTPUT_DIR,
        tokenizer=OUTPUT_DIR,
        aggregation_strategy="simple",
    )
    results = ner_pipeline(text)
    skills = [r["word"] for r in results if r["entity_group"] == "SKILL"]
    print(f"Skills detected: {skills}")
    return skills


if __name__ == "__main__":
    train()

    # Test on sample sentences after training
    test_inference("We are looking for a Python developer with TensorFlow and AWS experience")
    test_inference("Required skills: SQL, Docker, Kubernetes and machine learning")
    test_inference("Join our team as a data scientist with expertise in PyTorch and NLP")