import pandas as pd
import json
import re
import os
from tqdm import tqdm

# ── Paths ──────────────────────────────────────────────────
PROCESSED_PATH = "ml/data/processed/jobs_clean.csv"
NER_TRAIN_PATH = "ml/data/processed/ner_train.json"
NER_VAL_PATH = "ml/data/processed/ner_val.json"
NER_TEST_PATH = "ml/data/processed/ner_test.json"

os.makedirs("ml/data/processed", exist_ok=True)

# ── Skill Dictionary ───────────────────────────────────────
SKILLS = [
    # Programming Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go",
    "Rust", "Scala", "R", "MATLAB", "Swift", "Kotlin", "Ruby", "PHP",
    # ML / DL Frameworks
    "TensorFlow", "PyTorch", "Keras", "scikit-learn", "XGBoost",
    "LightGBM", "CatBoost", "Hugging Face", "transformers", "ONNX",
    "OpenCV", "YOLO", "spaCy", "NLTK", "Gensim",
    # Data Engineering
    "Spark", "Hadoop", "Kafka", "Airflow", "dbt", "Flink",
    "Databricks", "Snowflake", "BigQuery", "Redshift", "Hive",
    # Databases
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Cassandra",
    "Elasticsearch", "Neo4j", "SQLite", "Oracle", "DynamoDB",
    # Cloud
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform",
    "Lambda", "EC2", "S3", "GKE", "EKS", "CloudFormation",
    # MLOps
    "MLflow", "Kubeflow", "SageMaker", "Vertex AI", "DVC",
    "Weights and Biases", "Neptune", "Grafana", "Prometheus",
    # NLP / AI Concepts
    "NLP", "BERT", "GPT", "LLM", "RAG", "embeddings", "transformers",
    "computer vision", "deep learning", "machine learning",
    "reinforcement learning", "transfer learning", "fine-tuning",
    "neural networks", "CNN", "RNN", "LSTM", "GAN", "diffusion",
    # Data Science
    "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "Tableau", "Power BI", "Excel", "statistics", "A/B testing",
    "hypothesis testing", "regression", "classification", "clustering",
    # APIs and Backend
    "FastAPI", "Flask", "Django", "REST", "GraphQL", "gRPC",
    "microservices", "API", "JSON", "YAML",
    # Tools
    "Git", "GitHub", "Linux", "Bash", "CI/CD", "Jenkins",
    "GitHub Actions", "JIRA", "Agile", "Scrum",
    # Vector / Search
    "FAISS", "Pinecone", "Qdrant", "Weaviate", "vector database",
    "semantic search", "recommendation system",
]

# Sort by length descending so longer phrases match first
SKILLS_SORTED = sorted(SKILLS, key=len, reverse=True)


# ── Tokenize text into words ───────────────────────────────
def tokenize(text):
    tokens = re.findall(r'\b\w+(?:\.\w+)*\b|[^\w\s]', text)
    return tokens


# ── Find skill spans in text ───────────────────────────────
def find_skill_spans(text):
    """
    Find all skill mentions in text.
    Returns list of (start_char, end_char, skill_text)
    """
    spans = []
    text_lower = text.lower()

    for skill in SKILLS_SORTED:
        skill_lower = skill.lower()
        start = 0
        while True:
            idx = text_lower.find(skill_lower, start)
            if idx == -1:
                break
            end = idx + len(skill)
            # Make sure it is a whole word match
            before_ok = (idx == 0 or not text[idx-1].isalnum())
            after_ok = (end == len(text) or not text[end].isalnum())
            if before_ok and after_ok:
                # Check no overlap with existing spans
                overlap = any(s < end and e > idx for s, e, _ in spans)
                if not overlap:
                    spans.append((idx, end, text[idx:end]))
            start = idx + 1

    return sorted(spans, key=lambda x: x[0])


# ── Convert to IOB2 token labels ───────────────────────────
def create_iob2_labels(text, skill_spans):
    """
    Convert character-level spans to IOB2 token labels.
    B-SKILL = beginning of skill entity
    I-SKILL = inside skill entity
    O       = outside any entity
    """
    tokens = []
    labels = []
    words = text.split()
    char_idx = 0

    for word in words:
        word_start = text.find(word, char_idx)
        word_end = word_start + len(word)
        char_idx = word_end

        label = "O"
        for span_start, span_end, _ in skill_spans:
            if word_start >= span_start and word_end <= span_end:
                if word_start == span_start:
                    label = "B-SKILL"
                else:
                    label = "I-SKILL"
                break

        tokens.append(word)
        labels.append(label)

    return tokens, labels


# ── Create training examples ───────────────────────────────
def create_training_examples(df):
    examples = []
    print("Creating NER training examples...")

    for _, row in tqdm(df.iterrows(), total=len(df)):
        text = str(row["combined_text"])

        # Find skill spans
        skill_spans = find_skill_spans(text)

        # Skip if no skills found
        if len(skill_spans) == 0:
            continue

        # Create IOB2 labels
        tokens, labels = create_iob2_labels(text, skill_spans)

        # Skip very short examples
        if len(tokens) < 10:
            continue

        examples.append({
            "tokens": tokens,
            "labels": labels,
            "text": text[:200],
            "skills_found": [s[2] for s in skill_spans],
        })

    print(f"Created {len(examples)} training examples")
    return examples


# ── Split and save ─────────────────────────────────────────
def split_and_save(examples):
    n = len(examples)
    train_end = int(0.8 * n)
    val_end = int(0.9 * n)

    train = examples[:train_end]
    val = examples[train_end:val_end]
    test = examples[val_end:]

    with open(NER_TRAIN_PATH, "w") as f:
        json.dump(train, f, indent=2)

    with open(NER_VAL_PATH, "w") as f:
        json.dump(val, f, indent=2)

    with open(NER_TEST_PATH, "w") as f:
        json.dump(test, f, indent=2)

    print(f"\nSaved splits:")
    print(f"  Train: {len(train)} examples")
    print(f"  Val:   {len(val)} examples")
    print(f"  Test:  {len(test)} examples")
    print(f"\nSample from first training example:")
    print(f"  Tokens: {train[0]['tokens'][:10]}")
    print(f"  Labels: {train[0]['labels'][:10]}")
    print(f"  Skills found: {train[0]['skills_found'][:5]}")


# ── Main ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("Creating NER Training Data from Job Postings")
    print("=" * 50)

    df = pd.read_csv(PROCESSED_PATH)
    print(f"Loaded {len(df)} job postings")

    examples = create_training_examples(df)
    split_and_save(examples)

    print("\nNER data creation complete!")