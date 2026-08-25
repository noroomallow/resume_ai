import os
import json
from google import genai
from google.genai import types
from flask import current_app

def get_client():
    api_key = current_app.config.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Gemini API key is missing. Configure GEMINI_API_KEY in environment variables.")
    return genai.Client(api_key=api_key)

def generate_summary(user_data):
    """Generates an ATS-optimized professional summary using user data."""
    client = get_client()
    prompt = f"""
    Act as a professional resume editor. Create a strong, professional summary (3-5 sentences) based on the following background:
    Name: {user_data.get('full_name')}
    Professional Title: {user_data.get('professional_title')}
    Target Role: {user_data.get('target_role', user_data.get('professional_title'))}
    Skills: {', '.join(user_data.get('skills', []))}
    Experience Highlights: {user_data.get('experience_summary', 'N/A')}
    Education: {user_data.get('education_summary', 'N/A')}

    CRITICAL CONSTRAINTS:
    - Never invent fictitious accomplishments, titles, or years of experience.
    - Write in professional, objective third-person style or implicit first-person without using "I", "me", or "my".
    - Use active voice and high-impact action keywords.
    - Return ONLY the generated summary text.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=300
        )
    )
    return response.text.strip()

def improve_project_description(project_name, technologies, raw_description):
    """Refines project descriptions into high-impact bullet points without fabricating data."""
    client = get_client()
    prompt = f"""
    Refine the following software engineering / project description into 2 to 4 high-impact resume bullet points.
    Project Name: {project_name}
    Technologies Used: {technologies}
    Current Description: {raw_description}

    CRITICAL CONSTRAINTS:
    - Do NOT invent metrics, percentages, or achievements not backed by the input.
    - Start each bullet point with a strong past-tense action verb.
    - Emphasize proper technical usage and modern methodologies.
    - Output ONLY bullet points starting with '• '.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=350
        )
    )
    return response.text.strip()

def suggest_skills(existing_skills, job_title, project_descriptions):
    """Suggests relevant technical and soft skills categorized properly."""
    client = get_client()
    prompt = f"""
    Analyze the current profile and suggest complementary, relevant skills for a {job_title} role.
    Existing Skills: {', '.join(existing_skills)}
    Project Context: {project_descriptions}

    Return a valid JSON object strictly matching this schema:
    {{
       "Technical": ["skill1", "skill2"],
       "Tools": ["tool1", "tool2"],
       "Frameworks": ["fw1", "fw2"],
       "Cloud": ["cloud1"],
       "Soft Skills": ["skill1", "skill2"]
    }}

    Rules:
    - Do NOT suggest skills the user already has listed.
    - Output strictly valid raw JSON without code blocks or backticks.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )
    return json.loads(response.text.strip())