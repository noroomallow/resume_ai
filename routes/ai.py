from flask import Blueprint, request, jsonify
from routes.auth import login_required
from services.ai_service import generate_summary, improve_project_description, suggest_skills, get_client
from google.genai import types

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai/assistant')
@login_required
def assistant_page():
    return render_template('ai_assistant.html')

@ai_bp.route('/api/ai/summary', methods=['POST'])
@login_required
def handle_summary():
    data = request.get_json()
    try:
        res = generate_summary(data)
        return jsonify({'success': True, 'data': res})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@ai_bp.route('/api/ai/project', methods=['POST'])
@login_required
def handle_project():
    data = request.get_json()
    try:
        res = improve_project_description(
            data.get('name', ''),
            data.get('technologies', ''),
            data.get('description', '')
        )
        return jsonify({'success': True, 'data': res})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@ai_bp.route('/api/ai/experience', methods=['POST'])
@login_required
def handle_experience():
    data = request.get_json()
    client = get_client()
    prompt = f"""
    Convert the following work experience summary into professional, high-impact resume bullet points:
    Position: {data.get('position')} at {data.get('company')}
    Raw Input: {data.get('description')}
    
    CRITICAL: Never invent metrics, stats, or technologies. Use active past-tense verbs.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2)
        )
        return jsonify({'success': True, 'data': response.text.strip()})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@ai_bp.route('/api/ai/skills', methods=['POST'])
@login_required
def handle_skills():
    data = request.get_json()
    try:
        res = suggest_skills(
            data.get('existing_skills', []),
            data.get('job_title', ''),
            data.get('context', '')
        )
        return jsonify({'success': True, 'data': res})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500