from flask import Blueprint, render_template, request, jsonify, g, redirect, url_for, send_file
from routes.auth import login_required
from database.db import query_db, execute_db
from services.pdf_service import generate_resume_pdf

resume_bp = Blueprint('resume', __name__)

def get_full_resume_data(resume_id, user_id):
    resume = query_db('SELECT * FROM resumes WHERE id = ? AND user_id = ?', (resume_id, user_id), one=True)
    if not resume:
        return None

    data = dict(resume)
    data['education'] = [dict(r) for r in query_db('SELECT * FROM education WHERE resume_id = ?', (resume_id,))]
    data['experience'] = [dict(r) for r in query_db('SELECT * FROM experience WHERE resume_id = ?', (resume_id,))]
    data['projects'] = [dict(r) for r in query_db('SELECT * FROM projects WHERE resume_id = ?', (resume_id,))]
    data['skills'] = [dict(r) for r in query_db('SELECT * FROM skills WHERE resume_id = ?', (resume_id,))]
    data['certifications'] = [dict(r) for r in query_db('SELECT * FROM certifications WHERE resume_id = ?', (resume_id,))]
    data['achievements'] = [dict(r) for r in query_db('SELECT * FROM achievements WHERE resume_id = ?', (resume_id,))]
    data['languages'] = [dict(r) for r in query_db('SELECT * FROM languages WHERE resume_id = ?', (resume_id,))]
    
    return data

@resume_bp.route('/resumes')
@login_required
def list_resumes():
    resumes = query_db('SELECT * FROM resumes WHERE user_id = ? ORDER BY updated_at DESC', (g.user['id'],))
    return render_template('dashboard.html', resumes=resumes)

@resume_bp.route('/resume/builder', methods=['GET'])
@resume_bp.route('/resume/builder/<int:resume_id>', methods=['GET'])
@login_required
def builder(resume_id=None):
    resume_data = None
    if resume_id:
        resume_data = get_full_resume_data(resume_id, g.user['id'])
        if not resume_data:
            return redirect(url_for('dashboard.dashboard'))
    return render_template('resume_builder.html', resume=resume_data)

@resume_bp.route('/api/resume', methods=['POST'])
@login_required
def save_resume():
    payload = request.get_json()
    user_id = g.user['id']
    resume_id = payload.get('id')

    if resume_id:
        # Verify ownership
        existing = query_db('SELECT id FROM resumes WHERE id = ? AND user_id = ?', (resume_id, user_id), one=True)
        if not existing:
            return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
            
        execute_db('''
            UPDATE resumes SET title=?, full_name=?, professional_title=?, email=?, phone=?, location=?, 
            website=?, linkedin=?, github=?, summary=?, template=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (
            payload.get('title', 'Untitled'), payload.get('full_name'), payload.get('professional_title'),
            payload.get('email'), payload.get('phone'), payload.get('location'), payload.get('website'),
            payload.get('linkedin'), payload.get('github'), payload.get('summary'), payload.get('template', 'classic'),
            resume_id
        ))
    else:
        resume_id = execute_db('''
            INSERT INTO resumes (user_id, title, full_name, professional_title, email, phone, location, website, linkedin, github, summary, template)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, payload.get('title', 'Untitled'), payload.get('full_name'), payload.get('professional_title'),
            payload.get('email'), payload.get('phone'), payload.get('location'), payload.get('website'),
            payload.get('linkedin'), payload.get('github'), payload.get('summary'), payload.get('template', 'classic')
        ))

    # Cascade clear child records for atomic re-insertion
    for table in ['education', 'experience', 'projects', 'skills', 'certifications', 'achievements', 'languages']:
        execute_db(f'DELETE FROM {table} WHERE resume_id = ?', (resume_id,))

    # Dynamic Array Insertions
    for ed in payload.get('education', []):
        execute_db('INSERT INTO education (resume_id, degree, institution, location, start_date, end_date, description) VALUES (?,?,?,?,?,?,?)',
                   (resume_id, ed.get('degree'), ed.get('institution'), ed.get('location'), ed.get('start_date'), ed.get('end_date'), ed.get('description')))

    for exp in payload.get('experience', []):
        execute_db('INSERT INTO experience (resume_id, company, position, location, start_date, end_date, description) VALUES (?,?,?,?,?,?,?)',
                   (resume_id, exp.get('company'), exp.get('position'), exp.get('location'), exp.get('start_date'), exp.get('end_date'), exp.get('description')))

    for proj in payload.get('projects', []):
        execute_db('INSERT INTO projects (resume_id, name, technologies, description, github_url, live_url) VALUES (?,?,?,?,?,?)',
                   (resume_id, proj.get('name'), proj.get('technologies'), proj.get('description'), proj.get('github_url'), proj.get('live_url')))

    for sk in payload.get('skills', []):
        execute_db('INSERT INTO skills (resume_id, skill_name, category) VALUES (?,?,?)',
                   (resume_id, sk.get('skill_name'), sk.get('category', 'Technical')))

    for cert in payload.get('certifications', []):
        execute_db('INSERT INTO certifications (resume_id, name, issuer, date, credential_url) VALUES (?,?,?,?,?)',
                   (resume_id, cert.get('name'), cert.get('issuer'), cert.get('date'), cert.get('credential_url')))

    for ach in payload.get('achievements', []):
        execute_db('INSERT INTO achievements (resume_id, title, description, date) VALUES (?,?,?,?)',
                   (resume_id, ach.get('title'), ach.get('description'), ach.get('date')))

    for lang in payload.get('languages', []):
        execute_db('INSERT INTO languages (resume_id, language, proficiency) VALUES (?,?,?)',
                   (resume_id, lang.get('language'), lang.get('proficiency')))

    return jsonify({'success': True, 'message': 'Resume saved successfully', 'resume_id': resume_id})

@resume_bp.route('/api/resume/<int:resume_id>', methods=['GET'])
@login_required
def get_resume(resume_id):
    data = get_full_resume_data(resume_id, g.user['id'])
    if not data:
        return jsonify({'success': False, 'message': 'Resume not found'}), 404
    return jsonify({'success': True, 'data': data})

@resume_bp.route('/api/resume/<int:resume_id>', methods=['DELETE'])
@login_required
def delete_resume(resume_id):
    execute_db('DELETE FROM resumes WHERE id = ? AND user_id = ?', (resume_id, g.user['id']))
    return jsonify({'success': True, 'message': 'Resume deleted successfully'})

@resume_bp.route('/resume/<int:resume_id>/preview')
@login_required
def preview(resume_id):
    data = get_full_resume_data(resume_id, g.user['id'])
    if not data:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('resume_preview.html', resume=data)

@resume_bp.route('/resume/<int:resume_id>/download')
@login_required
def download_pdf(resume_id):
    data = get_full_resume_data(resume_id, g.user['id'])
    if not data:
        return jsonify({'error': 'Resume not found'}), 404
    
    pdf_buffer = generate_resume_pdf(data)
    filename = f"{data['full_name'].replace(' ', '_')}_Resume.pdf"
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)