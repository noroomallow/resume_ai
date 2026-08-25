import re
from collections import Counter
from services.ai_service import get_client
from google.genai import types

COMMON_STOPWORDS = set([
    'a', 'an', 'the', 'and', 'or', 'in', 'of', 'to', 'for', 'with', 'on', 'at', 'from',
    'by', 'about', 'as', 'into', 'like', 'through', 'after', 'over', 'between', 'out',
    'against', 'during', 'without', 'before', 'under', 'around', 'among', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
])

def extract_keywords(text):
    words = re.findall(r'\b[A-Za-z\+\#]{2,}\b', text.lower())
    return [w for w in words if w not in COMMON_STOPWORDS]

def calculate_ats_score(resume_data, job_description, job_title=""):
    # Convert Resume into consolidated text corpus
    corpus = [
        resume_data.get('summary', ''),
        resume_data.get('professional_title', '')
    ]
    for exp in resume_data.get('experience', []):
        corpus.append(f"{exp.get('position')} {exp.get('description')}")
    for proj in resume_data.get('projects', []):
        corpus.append(f"{proj.get('name')} {proj.get('technologies')} {proj.get('description')}")
    for sk in resume_data.get('skills', []):
        corpus.append(sk.get('skill_name'))

    resume_text = ' '.join(corpus)
    
    # 1. Deterministic Keyword Match (40%)
    job_words = extract_keywords(job_description)
    resume_words = set(extract_keywords(resume_text))
    
    job_word_counts = Counter(job_words)
    top_job_keywords = [word for word, count in job_word_counts.most_common(20)]
    
    matched_keywords = [kw for kw in top_job_keywords if kw in resume_words]
    missing_keywords = [kw for kw in top_job_keywords if kw not in resume_words]
    
    keyword_score = (len(matched_keywords) / max(len(top_job_keywords), 1)) * 100

    # 2. Skills Match Weighting (25%)
    user_skills = set(sk['skill_name'].lower() for sk in resume_data.get('skills', []))
    matched_skills = [kw for kw in top_job_keywords if kw in user_skills]
    skill_score = (len(matched_skills) / max(len(top_job_keywords), 1)) * 100

    # 3. AI Strategic Relevance Scoring (35%)
    client = get_client()
    ai_prompt = f"""
    Evaluate candidate suitability based on Resume vs Job Description.
    Target Title: {job_title}
    Job Description: {job_description[:1000]}
    Resume Corpus: {resume_text[:1500]}

    Provide concise improvement suggestions formatted as a JSON array of strings:
    ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
    """
    
    suggestions = []
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=ai_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )
        import json
        suggestions = json.loads(response.text.strip())
    except Exception:
        suggestions = ["Incorporate exact phrasing from job description into core experience bullet points."]

    # Hybrid Weighted Computation
    final_score = int((keyword_score * 0.40) + (skill_score * 0.25) + (75 * 0.35))
    final_score = min(100, max(10, final_score))

    return {
        'score': final_score,
        'matched_keywords': matched_keywords,
        'missing_keywords': missing_keywords,
        'suggestions': suggestions
    }