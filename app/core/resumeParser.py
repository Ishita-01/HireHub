import spacy
from spacy.matcher import PhraseMatcher
import fitz
from typing import List,Dict,Any


class ResumeParser:
    def __init__(self, resume_path: str):
        self.resume_path = resume_path
        self.text = self._extract_text()
    
    def _extract_text(self) -> str:
        text = ""
        with fitz.open(self.resume_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    
    def extract_info(self) -> Dict[str, Any]:
        # Placeholder for future extraction logic
        info = {
            "skills":self._extract_skills(),
            "experience_years":self._extract_experience(),
            "graduation_year":self._extract_graduation_year()

        }
        return info
    
    def _extract_skills(self) -> List[str]:
        pass
    def get_text(self) -> str:
        return self.text






# nlp = spacy.load("en_core_web_sm")

# skills = [
#     "Python", "Java", "C++", "JavaScript", "SQL", "HTML", "CSS",
#     "Django", "Flask", "React", "Angular", "Node.js",
#     "Machine Learning", "Data Analysis", "AWS", "Azure", "Docker", "Kubernetes",
#     "AI", "NLP", "Deep Learning", "TensorFlow", "PyTorch","Computer Vision",
#     "Artificial Intelligence", "Data Science", "Big Data", "Hadoop", "Spark",
#     "FastAPI", "TypeScript", "GraphQL", "NoSQL", "MongoDB", "PostgreSQL","MERN","MEAN"
# ]

# def extractKeywords(resumeText:str):
#     doc = nlp(resumeText.lower())
#     matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
#     patterns = [nlp.make_doc(skill.lower()) for skill in skills]
#     matcher.add("Skills", patterns)
#     matches = matcher(doc)
    
#     found_skills = set()
#     for match_id, start, end in matches:
#         found_skills.add(doc[start:end].text)
    
#     return list(found_skills)

# def extract_experience(resumeText:str) -> int:
#     doc = nlp(resumeText)
#     experience_years = 0

#     for ent in doc.ents:
#         if ent.label_ == "DATE":
#             text = ent.text.lower()
#             if "year" in text:
#                 try:
#                     years = int(''.join(filter(str.isdigit, text)))
#                     experience_years = max(experience_years, years)
#                 except ValueError:
#                     continue
#     return experience_years

