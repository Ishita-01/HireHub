import os
from dotenv import load_dotenv
import json
from google import genai
from google.genai import types
import re
 # for GenerateContentConfig

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

ANALYSIS_PROMPT = """
You are an expert ATS and recruiter AI specializing in resume-job matching. Analyze the provided RESUME and JOB_DESCRIPTION to compute a precise match score (0-100%) and detailed breakdown.

**STEP 1: Parse and Extract Key Elements**
From JOB_DESCRIPTION, identify and list:
- Top 5-8 required skills/competencies
- Key responsibilities/outcomes (3-5)
- Experience level (years, seniority)
- Preferred qualifications (tools, certifications, education)
- Keywords/phrases (technical, soft skills, industry terms)

From RESUME, extract:
- Candidate's skills, experiences, achievements
- Quantified accomplishments (metrics, impacts)
- Education, certifications, tools
- Total relevant experience years

**STEP 2: Matching Analysis (Score Each Category 0-100%)**
Provide scores with brief justification:

SKILLS MATCH (30% weight):
- Exact matches: [list]
- Partial/related: [list] 
- Missing critical: [list]
- Score: __%

EXPERIENCE ALIGNMENT (30% weight):
- Years match: __/target __ years
- Role relevance: __%
- Score: __%

ACHIEVEMENTS/RESULTS (20% weight):
- Quantified impact similarity: __%
- Score: __%

KEYWORDS/ATS (10% weight):
- Density match: __%
- Score: __%

QUALIFICATIONS (10% weight):
- Education/certifications: __%
- Score: __%

**STEP 3: Overall Score Calculation**
FINAL MATCH SCORE: __% (weighted average)
Formula: (Skills*0.3 + Experience*0.3 + Achievements*0.2 + Keywords*0.1 + Quals*0.1)

**STEP 4: Actionable Recommendations**
TOP 3 IMPROVEMENTS (most impactful first):
1. [Specific gap + how to fix]
2. [Specific gap + how to fix] 
3. [Specific gap + how to fix]

**Output Format (JSON):**
{
  "overall_score": 87,
  "category_scores": {"skills": 92, "experience": 78, ...},
  "strengths": ["bullet 1", "bullet 2"],
  "missing_skills": ["skill 1", "skill 2"],
  "recommendations": ["rec 1", "rec 2", "rec 3"],
  "ats_keywords_to_add": ["keyword1", "keyword2"]
}

Job Description : {job_description}

Be ruthlessly objective. Use exact matching for technical skills. Consider transferrable skills for soft skills. Never inflate scores.
Return ONLY a valid JSON object, with no explanation, no markdown, and no surrounding text.
If you cannot complete the analysis, still return a valid JSON object that matches the schema.

"""

# Create a global client once

client = genai.Client(api_key=GEMINI_API_KEY)

def extract_json(text: str):
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found in Gemini response")
    return match.group()


def analyze_resume(resume_path: str, job_description: str):
    try:
        # 1. Upload the resume file
        resume_file = client.files.upload(file=resume_path)

        # 2. Call the model with file + prompt and force JSON output
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                resume_file,
                ANALYSIS_PROMPT.format(job_description=job_description),
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )

        print("\n================ GEMINI FULL RESPONSE OBJECT ================\n")
        print(response)
        print("\n================ GEMINI response.text ================\n")
        print(repr(response.text))
        print("\n================ END ================\n")
        
        raw = (response.text or "").strip()
        if not raw:
            raise ValueError("Gemini returned empty response")
        
        clean_json = extract_json(raw)
        data = json.loads(clean_json)


        return {
            "overall_score": data.get("overall_score", 0),
            "category_scores": data.get("category_scores", {}),
            "strengths": data.get("strengths", []),
            "missing_skills": data.get("missing_skills", []),
            "recommendations": data.get("recommendations", []),
            "ats_keywords_to_add": data.get("ats_keywords_to_add", []),
        }


        

    except Exception as e:
        return {
            "overall_score": 0,
            "category_scores": {},
            "strengths": [],
            "missing_skills": ["Error or malformed AI response"],
            "recommendations": [str(e)],
            "ats_keywords_to_add": [],
        }
    
    finally:
        # Clean up uploaded file
        if 'resume_file' in locals():
            try:
                client.files.delete(file_id=resume_file.id)
            except Exception:
                pass