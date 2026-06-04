import pandas as pd
import re
import os
from tqdm import tqdm

# ── Paths ──────────────────────────────────────────────────
RAW_PATH = "ml/data/raw/postings.csv"
PROCESSED_PATH = "ml/data/processed/jobs_clean.csv"

os.makedirs("ml/data/processed", exist_ok=True)


# ── Load data ──────────────────────────────────────
def load_data(path):
    print(f"Loading data from {path}...")
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


# ── Select only the columns we need ────────────────
def select_columns(df):
    cols = [
        "job_id",
        "title",
        "company_name",
        "description",
        "skills_desc",
        "location",
        "formatted_experience_level",
        "remote_allowed",
        "formatted_work_type",
    ]
    df = df[cols].copy()
    print(f"Selected {len(cols)} columns")
    return df


# ──  Drop rows with missing critical fields ─────────
def drop_missing(df):
    before = len(df)
    # Drop if description is missing
    df = df.dropna(subset=["description"])
    df = df[df["description"].str.strip() != ""]
    # Fill remaining NaN values with empty string or unknown
    df["company_name"] = df["company_name"].fillna("Unknown Company")
    df["title"] = df["title"].fillna("Unknown Title")
    df["location"] = df["location"].fillna("Unknown Location")
    df["formatted_experience_level"] = df["formatted_experience_level"].fillna("Not Specified")
    df["remote_allowed"] = df["remote_allowed"].fillna(0)
    df["formatted_work_type"] = df["formatted_work_type"].fillna("Not Specified")
    df["skills_desc"] = df["skills_desc"].fillna("")
    after = len(df)
    print(f"Dropped {before - after} rows with missing description")
    print(f"Remaining NaN values: {df.isnull().sum().sum()}")
    return df

# ──Clean the description text ────────────────────
def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)
    # Remove special characters but keep letters, numbers, punctuation
    text = re.sub(r"[^\w\s\.,\-\(\)]", " ", text)
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_descriptions(df):
    print("Cleaning description text...")
    tqdm.pandas()
    df["description"] = df["description"].progress_apply(clean_text)
    df["skills_desc"] = df["skills_desc"].fillna("").apply(clean_text)
    return df


# ── Create combined text field ────────────────────
def create_combined_text(df):
    print("Creating combined text field...")

    def combine(row):
        title = str(row["title"]) if pd.notna(row["title"]) else ""
        skills = str(row["skills_desc"]) if pd.notna(row["skills_desc"]) else ""
        desc = str(row["description"]) if pd.notna(row["description"]) else ""
        # Title repeated twice to give it more weight
        combined = f"{title}. {title}. {skills}. {desc}"
        # Truncate to 512 words (safe for BERT)
        words = combined.split()[:512]
        return " ".join(words)

    df["combined_text"] = df.apply(combine, axis=1)
    return df


# ── Remove duplicates ─────────────────────────────
def remove_duplicates(df):
    before = len(df)
    df = df.drop_duplicates(subset=["combined_text"])
    after = len(df)
    print(f"Removed {before - after} duplicate entries")
    return df


# ── Filter to ML / Data / Software roles ──────────
def filter_relevant_roles(df):
    keywords = [
        "machine learning", "data science", "data engineer",
        "software engineer", "backend", "python developer",
        "ai engineer", "deep learning", "nlp", "computer vision",
        "data analyst", "mlops", "devops", "full stack",
        "frontend", "cloud engineer", "research scientist"
    ]
    pattern = "|".join(keywords)
    before = len(df)
    mask = df["title"].str.lower().str.contains(pattern, na=False)
    df = df[mask].copy()
    after = len(df)
    print(f"Filtered to {after} relevant tech roles (from {before})")
    return df


# ── Reset index and save ──────────────────────────
def save_data(df, path):
    df = df.reset_index(drop=True)
    df.to_csv(path, index=False)
    print(f"\nSaved {len(df)} clean job postings to {path}")
    print(f"Columns: {df.columns.tolist()}")


# ── Main pipeline ──────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("TalentLens Data Preprocessing Pipeline")
    print("=" * 50)

    df = load_data(RAW_PATH)
    df = select_columns(df)
    df = drop_missing(df)
    df = clean_descriptions(df)
    df = create_combined_text(df)
    df = remove_duplicates(df)
    df = filter_relevant_roles(df)
    save_data(df, PROCESSED_PATH)

    print("\nPreprocessing complete!")
    print(f"Final dataset: {len(df)} job postings ready for training")