from flask import Blueprint, render_template, request, jsonify, g
from routes.auth import login_required
from database.db import query_db, execute_db
from services.ats_service import calculate_ats_score

ats_bp = Blueprint('ats', __name__)

@ats_bp.route('/ats')
@login_required
def ats_page():
    resumes = query_db('SELECT id, title FROM resumes WHERE user_id = ?', (g.user['id'],))
    return render_template('ats_analyzer.html', resumes=resumes)

@ats_bp.route('/api/ats/analyze', methods=['POST'])
@login_required
def analyze_resume():
    payload = request.get_json()
    resume_id = payload.get('resume_id')
    job_title = payload.get('job_title')
    job_description = payload.get('job_description')

    if not resume_id or not job_description:
        return jsonify({'success': False, 'message': 'Resume selection and Job Description required'}), 400

    from routes.resume import get_full_resume_data
    resume_data = get_full_resume_data(resume_id, g.user['id'])
    
    if not resume_data:
        return jsonify({'success': False, 'message': 'Resume not found'}), 404

    results = calculate_ats_score(resume_data, job_description, job_title)

    # Cache scan result
    execute_db('''
        INSERT INTO ats_analysis (user_id, resume_id, job_title, job_description, score, matched_keywords, missing_keywords, suggestions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        g.user['id'], resume_id, job_title, job_description,
        results['score'],
        ','.join(results['matched_keywords']),
        ','.join(results['missing_keywords']),
        '\n'.join(results['suggestions'])
    ))

    return jsonify({'success': True, 'data': results})