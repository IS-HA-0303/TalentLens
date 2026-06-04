import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from ml.training.skill_extractor import SkillExtractor

class NERService:
    """
    Wraps the hybrid skill extractor for use in the API.
    Loaded once at startup, reused for every request.
    """
    def __init__(self):
        print("Loading NER Service...")
        self.extractor = SkillExtractor(
            model_path="models/ner_model",
            use_bert=True,
        )
        print("NER Service ready")

    def extract_skills(self, text: str) -> list:
        return self.extractor.extract_skills(text)