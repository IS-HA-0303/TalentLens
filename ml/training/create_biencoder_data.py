import pandas as pd
import json
import random
import os
from tqdm import tqdm

# ── Paths ──────────────────────────────────────────────────
PROCESSED_PATH = "ml/data/processed/jobs_clean.csv"
PAIRS_TRAIN_PATH = "ml/data/processed/biencoder_train.json"
PAIRS_VAL_PATH = "ml/data/processed/biencoder_val.json"

os.makedirs("ml/data/processed", exist_ok=True)

random.seed(42)

# ── Candidate profile templates ────────────────────────────
# These templates simulate how a real candidate writes
# their resume or LinkedIn summary
PROFILE_TEMPLATES = [
    "I am a {level} {title} with {years} years of experience in {skills}. "
    "I have worked on {domain} projects and am passionate about {interest}.",

    "Experienced {title} skilled in {skills}. "
    "{years} years of hands-on experience building {domain} solutions. "
    "Looking for opportunities in {interest}.",

    "Results-driven {title} with expertise in {skills}. "
    "Background in {domain} with {years} years of professional experience.",

    "Passionate {level} engineer with strong {skills} skills. "
    "Experienced in developing {domain} applications for {years} years.",

    "Dedicated {title} with {years} years in {domain}. "
    "Core competencies include {skills}. "
    "Seeking challenging roles in {interest}.",
]

LEVELS = ["junior", "mid-level", "senior", "lead", "principal"]
YEARS_MAP = {
    "junior": ["1", "2"],
    "mid-level": ["3", "4", "5"],
    "senior": ["6", "7", "8"],
    "lead": ["8", "9", "10"],
    "principal": ["10", "12", "15"],
}

DOMAINS = [
    "machine learning", "data science", "software engineering",
    "backend development", "cloud infrastructure", "NLP",
    "computer vision", "data engineering", "MLOps", "AI research",
    "recommendation systems", "distributed systems",
]

INTERESTS = [
    "artificial intelligence", "deep learning", "large language models",
    "scalable systems", "open source", "research and development",
    "production ML systems", "data-driven products",
]


# ── Extract skills from job text ───────────────────────────
def extract_skills_simple(text, skill_list):
    """Simple dictionary-based skill extraction"""
    found = []
    text_lower = text.lower()
    for skill in skill_list:
        if skill.lower() in text_lower:
            found.append(skill)
    return found


SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "Go", "Scala",
    "TensorFlow", "PyTorch", "Keras", "scikit-learn", "XGBoost",
    "Spark", "Kafka", "Airflow", "dbt", "Databricks", "Snowflake",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform",
    "MLflow", "Kubeflow", "SageMaker", "DVC", "Grafana",
    "NLP", "BERT", "GPT", "LLM", "RAG", "deep learning",
    "machine learning", "computer vision", "reinforcement learning",
    "pandas", "numpy", "matplotlib", "statistics", "A/B testing",
    "FastAPI", "Flask", "Django", "REST", "GraphQL",
    "Git", "Linux", "CI/CD", "Agile",
    "FAISS", "Qdrant", "recommendation system",
]


# ── Generate synthetic candidate profile ──────────────────
def generate_candidate_profile(job_row, match_level="high"):
    """
    Generate a synthetic candidate profile that matches a job.

    match_level:
      "high"   → candidate has most required skills (positive pair)
      "medium" → candidate has some skills (weak positive)
      "low"    → candidate has few/wrong skills (negative pair)
    """
    # Extract skills from job
    job_text = str(job_row["combined_text"])
    job_skills = extract_skills_simple(job_text, SKILLS)

    # Get job title and level
    job_title = str(job_row["title"])
    exp_level = str(job_row["formatted_experience_level"])

    # Map experience level
    if "entry" in exp_level.lower() or "associate" in exp_level.lower():
        level = "junior"
    elif "mid" in exp_level.lower() or "not specified" in exp_level.lower():
        level = "mid-level"
    elif "senior" in exp_level.lower() or "director" in exp_level.lower():
        level = "senior"
    elif "executive" in exp_level.lower():
        level = "lead"
    else:
        level = random.choice(LEVELS)

    years = random.choice(YEARS_MAP[level])

    # Select skills based on match level
    if match_level == "high" and len(job_skills) > 0:
        # Take 70-100% of job skills
        n_skills = max(1, int(len(job_skills) * random.uniform(0.7, 1.0)))
        selected_skills = random.sample(job_skills, min(n_skills, len(job_skills)))
        # Add 1-2 random extra skills
        extra = random.sample(SKILLS, min(2, len(SKILLS)))
        selected_skills = list(set(selected_skills + extra))

    elif match_level == "medium" and len(job_skills) > 0:
        # Take 30-60% of job skills
        n_skills = max(1, int(len(job_skills) * random.uniform(0.3, 0.6)))
        selected_skills = random.sample(job_skills, min(n_skills, len(job_skills)))

    else:
        # Low match — pick random skills unrelated to job
        selected_skills = random.sample(SKILLS, random.randint(2, 5))

    if len(selected_skills) == 0:
        selected_skills = random.sample(SKILLS, 3)

    skills_str = ", ".join(selected_skills[:6])
    domain = random.choice(DOMAINS)
    interest = random.choice(INTERESTS)
    template = random.choice(PROFILE_TEMPLATES)

    profile = template.format(
        level=level,
        title=job_title,
        years=years,
        skills=skills_str,
        domain=domain,
        interest=interest,
    )

    return profile, selected_skills


# ── Create training pairs ──────────────────────────────────
def create_training_pairs(df):
    """
    Create (job, candidate, label) triplets for bi-encoder training.

    For Multiple Negatives Ranking Loss we need:
    - Positive pairs: (job, matching_candidate)
    - The negatives are automatically other jobs in the same batch

    So we just need positive pairs.
    """
    pairs = []
    jobs_list = df.to_dict("records")

    print("Creating training pairs...")

    for job in tqdm(jobs_list):
        job_text = str(job["combined_text"])

        # Create 2 positive candidate profiles per job
        for _ in range(2):
            candidate_text, _ = generate_candidate_profile(job, match_level="high")
            pairs.append({
                "anchor": job_text,        # job posting
                "positive": candidate_text, # matching candidate
            })

        # Create 1 medium match
        candidate_text, _ = generate_candidate_profile(job, match_level="medium")
        pairs.append({
            "anchor": job_text,
            "positive": candidate_text,
        })

    print(f"Created {len(pairs)} training pairs")
    return pairs


# ── Split and save ─────────────────────────────────────────
def split_and_save(pairs):
    random.shuffle(pairs)
    n = len(pairs)
    split = int(0.9 * n)

    train_pairs = pairs[:split]
    val_pairs = pairs[split:]

    with open(PAIRS_TRAIN_PATH, "w") as f:
        json.dump(train_pairs, f, indent=2)

    with open(PAIRS_VAL_PATH, "w") as f:
        json.dump(val_pairs, f, indent=2)

    print(f"\nSaved:")
    print(f"  Train pairs: {len(train_pairs)}")
    print(f"  Val pairs:   {len(val_pairs)}")
    print(f"\nSample pair:")
    print(f"  Job:       {train_pairs[0]['anchor'][:100]}...")
    print(f"  Candidate: {train_pairs[0]['positive'][:100]}...")


# ── Main ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("TalentLens Bi-Encoder Training Data Creation")
    print("=" * 55)

    df = pd.read_csv(PROCESSED_PATH)
    print(f"Loaded {len(df)} job postings")

    pairs = create_training_pairs(df)
    split_and_save(pairs)

    print("\nTraining data creation complete!")