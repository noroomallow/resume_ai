from flask import Blueprint, render_template, request, jsonify, g, redirect, url_for
from routes.auth import login_required
from database.db import query_db, execute_db
from routes.resume import get_full_resume_data

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/portfolio/builder')
@login_required
def builder():
    user_id = g.user['id']
    resumes = query_db('SELECT id, title FROM resumes WHERE user_id = ?', (user_id,))
    portfolio = query_db('SELECT * FROM portfolios WHERE user_id = ?', (user_id,), one=True)
    return render_template('portfolio_builder.html', resumes=resumes, portfolio=portfolio)

@portfolio_bp.route('/api/portfolio', methods=['PUT'])
@login_required
def save_portfolio():
    payload = request.get_json()
    user_id = g.user['id']
    username = payload.get('username', '').strip().lower()
    resume_id = payload.get('resume_id')
    theme = payload.get('theme', 'modern')
    is_public = 1 if payload.get('is_public') else 0

    if not username or not resume_id:
        return jsonify({'success': False, 'message': 'Username and resume mapping required'}), 400

    existing = query_db('SELECT id FROM portfolios WHERE username = ? AND user_id != ?', (username, user_id), one=True)
    if existing:
        return jsonify({'success': False, 'message': 'Username already taken'}), 400

    portfolio = query_db('SELECT id FROM portfolios WHERE user_id = ?', (user_id,), one=True)
    
    if portfolio:
        execute_db('''
            UPDATE portfolios SET resume_id=?, username=?, theme=?, is_public=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (resume_id, username, theme, is_public, portfolio['id']))
    else:
        execute_db('''
            INSERT INTO portfolios (user_id, resume_id, username, theme, is_public)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, resume_id, username, theme, is_public))

    return jsonify({'success': True, 'message': 'Portfolio settings updated successfully'})

@portfolio_bp.route('/portfolio/<username>')
def public_view(username):
    portfolio = query_db('SELECT * FROM portfolios WHERE username = ? AND is_public = 1', (username,), one=True)
    if not portfolio:
        return render_template('404.html', message="Public portfolio not found or marked private."), 404

    resume_data = get_full_resume_data(portfolio['resume_id'], portfolio['user_id'])
    if not resume_data:
        return render_template('404.html', message="Associated resume data unavailable."), 404

    return render_template('public_portfolio.html', resume=resume_data, theme=portfolio['theme'])