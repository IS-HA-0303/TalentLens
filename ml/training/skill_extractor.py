import re
from transformers import pipeline

# ── Skill Dictionary (same as create_ner_data.py) ─────────
SKILLS = [
    # Programming Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go",
    "Rust", "Scala", "R", "MATLAB", "Swift", "Kotlin", "Ruby", "PHP",
    "HTML", "CSS", "HTML5", "CSS3", "Bash", "Shell", "Perl",

    # ML / DL Frameworks
    "TensorFlow", "PyTorch", "Keras", "scikit-learn", "Scikit-learn",
    "scikit", "XGBoost", "LightGBM", "CatBoost", "Hugging Face",
    "transformers", "ONNX", "OpenCV", "YOLO", "spaCy", "NLTK",
    "Gensim", "JAX", "MXNet",

    # Data Science Libraries
    "NumPy", "numpy", "Pandas", "pandas", "Matplotlib", "matplotlib",
    "Seaborn", "seaborn", "Plotly", "plotly", "SciPy", "scipy",
    "Jupyter", "statsmodels",

    # Data Engineering
    "Spark", "Hadoop", "Kafka", "Airflow", "dbt", "Flink",
    "Databricks", "Snowflake", "BigQuery", "Redshift", "Hive",

    # Databases
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Cassandra",
    "Elasticsearch", "Neo4j", "SQLite", "Oracle", "DynamoDB",
    "Firebase", "Supabase",

    # Web Frameworks
    "React", "React.js", "Node", "Node.js", "Express", "Express.js",
    "Angular", "Vue", "Django", "Flask", "FastAPI", "Spring",
    "Next.js", "GraphQL", "REST", "gRPC",

    # Cloud
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform",
    "Lambda", "EC2", "S3", "GKE", "EKS", "CloudFormation",
    "Heroku", "Vercel",

    # MLOps
    "MLflow", "Kubeflow", "SageMaker", "Vertex AI", "DVC",
    "Weights and Biases", "Neptune", "Grafana", "Prometheus",
    "Airflow", "Prefect", "ZenML",

    # NLP / AI Concepts
    "NLP", "BERT", "GPT", "LLM", "RAG", "embeddings",
    "computer vision", "deep learning", "machine learning",
    "reinforcement learning", "transfer learning", "fine-tuning",
    "neural networks", "neural network", "CNN", "RNN", "LSTM",
    "GAN", "diffusion", "transformers", "attention mechanism",
    "quantization", "pruning", "distillation",

    # Tools and Practices
    "Git", "GitHub", "Linux", "CI/CD", "Jenkins",
    "GitHub Actions", "JIRA", "Agile", "Scrum", "Docker",
    "Kubernetes", "Terraform", "Ansible",

    # Vector / Search
    "FAISS", "Pinecone", "Qdrant", "Weaviate", "vector database",
    "semantic search", "recommendation system",

    # Data Science concepts
    "statistics", "A/B testing", "hypothesis testing",
    "regression", "classification", "clustering",
    "feature engineering", "data preprocessing",
    "Tableau", "Power BI", "Excel",

    # Additional common skills
    "TF-IDF", "ALS", "matrix factorization", "collaborative filtering",
    "content filtering", "EfficientNet", "ResNet", "VGG",
    "object detection", "image classification", "text classification",
    "named entity recognition", "sentiment analysis",
    "Grad-CAM", "SHAP", "LIME",
    "Streamlit", "Gradio", "Hugging Face Spaces",
    "API", "REST API", "microservices",
    "Java", "C++", "JavaScript",
    "MongoDB", "MySQL", "PostgreSQL",
    "NumPy", "Pandas", "Matplotlib",
]

print(f"SKILLS LIST SIZE: {len(SKILLS)}")
SKILLS_SORTED = sorted(SKILLS, key=len, reverse=True)


class SkillExtractor:
    """
    Hybrid skill extractor combining:
    1. Dictionary-based exact matching (fast, precise)
    2. BERT NER model (context-aware, catches variations)
    """

    def __init__(self, model_path="models/ner_model", use_bert=True):
        self.use_bert = use_bert
        if use_bert:
            try:
                print("Loading BERT NER model...")
                self.ner_pipeline = pipeline(
                    "ner",
                    model=model_path,
                    tokenizer=model_path,
                    aggregation_strategy="simple",
                )
                print("BERT NER model loaded successfully")
            except Exception as e:
                print(f"Could not load BERT model: {e}")
                print("Falling back to dictionary only")
                self.use_bert = False

    def extract_with_dictionary(self, text):
        """Extract skills using exact dictionary matching"""
        found_skills = set()
        
        # Clean text variants for better matching
        text_clean = text.lower()
        # Remove dots from text (React.js → reactjs)
        text_nodot = text_clean.replace(".", "").replace("-", " ")
        
        for skill in SKILLS_SORTED:
            skill_lower = skill.lower()
            skill_nodot = skill_lower.replace(".", "").replace("-", " ")
            
            # Try matching in both original and cleaned text
            for search_text, search_skill in [
                (text_clean, skill_lower),
                (text_nodot, skill_nodot),
            ]:
                idx = search_text.find(search_skill)
                if idx != -1:
                    end = idx + len(search_skill)
                    before_ok = (idx == 0 or not search_text[idx-1].isalnum())
                    after_ok = (end == len(search_text) or not search_text[end].isalnum())
                    if before_ok and after_ok:
                        found_skills.add(skill)
                        break

        return found_skills

    def extract_with_bert(self, text):
        """Extract skills using BERT NER model"""
        if not self.use_bert:
            return set()

        try:
            results = self.ner_pipeline(text)
            # Only take entities with high confidence
            skills = set()
            for r in results:
                if r["entity_group"] == "SKILL" and r["score"] > 0.7:
                    word = r["word"].strip()
                    # Only keep if word is long enough to be meaningful
                    if len(word) > 2:
                        skills.add(word)
            return skills
        except Exception:
            return set()

    def extract_skills(self, text):
        """
        Main extraction function.
        Combines dictionary + BERT results.
        """
        if not isinstance(text, str) or len(text.strip()) == 0:
            return []

        # Dictionary matching (always runs)
        dict_skills = self.extract_with_dictionary(text)

        # BERT matching (runs if model available)
        bert_skills = self.extract_with_bert(text)

        # Remove BERT results that are substrings of dictionary skills
        # e.g. remove 'deep' if 'deep learning' already found
        # e.g. remove 'python' if 'Python' already found
        dict_skills_lower = {s.lower() for s in dict_skills}
        cleaned_bert = set()
        for skill in bert_skills:
            skill_lower = skill.lower()
            # Skip if it is a substring of any dictionary skill
            is_substring = any(
                skill_lower in ds_lower and skill_lower != ds_lower
                for ds_lower in dict_skills_lower
            )
            # Skip if dictionary already has this skill (case insensitive)
            already_exists = skill_lower in dict_skills_lower
            if not is_substring and not already_exists:
                cleaned_bert.add(skill)

        # Combine
        all_skills = dict_skills.union(cleaned_bert)

        # Return as sorted list
        return sorted(list(all_skills))


# ── Test the extractor ─────────────────────────────────────
if __name__ == "__main__":
    extractor = SkillExtractor(model_path="models/ner_model")

    tests = [
        "We need a Python developer with TensorFlow and AWS experience",
        "Required skills: SQL, Docker, Kubernetes and machine learning",
        "Looking for data scientist with PyTorch, pandas and deep learning",
        "Join our ML team with expertise in NLP, BERT and Hugging Face",
        "Backend engineer needed with FastAPI, PostgreSQL and Redis",
        "Senior ML engineer with experience in MLflow, Airflow and DVC",
    ]

    print("=" * 60)
    print("TalentLens Hybrid Skill Extractor Test")
    print("=" * 60)

    for text in tests:
        skills = extractor.extract_skills(text)
        print(f"\nInput:  {text}")
        print(f"Skills: {skills}")

    print("\n" + "=" * 60)
    print("Skill extraction test complete!")