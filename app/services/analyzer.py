import os
from dotenv import load_dotenv
import json
from google import genai
from google.genai import types
import re
import traceback
 # for GenerateContentConfig

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

ANALYSIS_PROMPT = """
You are an recruiter AI specializing in resume-job matching. Analyze the provided RESUME and JOB_DESCRIPTION to compute a precise match score (0-100%) and detailed breakdown.

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
Provide recommendations based on the job description.
TOP 3 IMPROVEMENTS (most impactful first):
1. [Specific gap + how to fix]
2. [Specific gap + how to fix] 
3. [Specific gap + how to fix]

**Output Format (JSON):**
{{
  "overall_score": 87,
  "category_scores": {"skills": 92, "experience": 78, ...},
  "strengths": ["bullet 1", "bullet 2"],
  "missing_skills": ["skill 1", "skill 2"],
  "recommendations": ["rec 1", "rec 2", "rec 3"],
  "ats_keywords_to_add": ["keyword1", "keyword2"]
}}

Job Description : {job_description}

Be ruthlessly objective. Use exact matching for technical skills. Consider transferrable skills for soft skills. Never inflate scores.
Return ONLY a valid JSON object, with no explanation, no markdown, and no surrounding text.
If you cannot complete the analysis, still return a valid JSON object that matches the schema.
Return ONLY a raw, valid JSON object. 
DO NOT use markdown formatting or triple backticks (```json).

Ensure the response starts immediately with the opening curly brace {
"""

# Create a global client once

client = genai.Client(api_key=GEMINI_API_KEY)

# app/services/analyzer.py

def extract_json(text: str):
    # This regex is more robust for finding JSON objects amidst extra text/newlines
    match = re.search(r"(\{[\s\S]*\})", text)
    if not match:
        raise ValueError("No valid JSON object found in response")
    return match.group(1).strip()

def analyze_resume(resume_path: str, job_description: str):
    try:

        print("inside analyze resume function (try)")
        resume_file = client.files.upload(path=resume_path)
        print(f"Uploaded resume file with name: {resume_file.name}")


        
        response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=[
        types.Content(role="user", parts=[
            types.Part.from_uri(
                file_uri=resume_file.uri,
                mime_type=resume_file.mime_type
            ),
            types.Part.from_text(
                text=ANALYSIS_PROMPT.replace("<<JOB_DESCRIPTION>>", job_description)
            )
        ])
    ],
    config=types.GenerateContentConfig(),
)
        if response and response.text:
            print("\n--- SUCCESS: RAW AI OUTPUT FOUND ---")
            print(repr(response.text)) 
            raw_text = response.text
        else:
            print("\n--- ERROR: Response object exists but .text is empty ---")
            raw_text = str(response)
        # =====================

        raw = (response.text or "").strip()
        if not raw:
            raise ValueError("Gemini returned empty response")

        # Standardize response text and strip markdown blocks if they exist
        raw_output = response.text.strip()
        if "```json" in raw_output:
            raw_output = raw_output.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_output:
            raw_output = raw_output.split("```")[1].split("```")[0].strip()
            
        clean_json = extract_json(raw_output)
        data = json.loads(clean_json)
        print(repr(response.text))
        return {
            "overall_score": data.get("overall_score", 0),
            "category_scores": data.get("category_scores", {}),
            "strengths": data.get("strengths", []),
            "missing_skills": data.get("missing_skills", []),
            "recommendations": data.get("recommendations", []),
            "ats_keywords_to_add": data.get("ats_keywords_to_add", []),
        }

    except Exception as e:
        # This will now print the actual error to your terminal for debugging
        traceback.print_exc()
        print(f"Detailed Analysis Error: {e}")
        
        return {
            "overall_score": 0,
            "category_scores": {},
            "strengths": [],
            "missing_skills": ["Analysis parsing error"],
            "recommendations": [f"Please try again. Error: {str(e)}"],
            "ats_keywords_to_add": [],
        }
    finally:
        if 'resume_file' in locals():
            try:
                client.files.delete(name=resume_file.name)
            except: pass



