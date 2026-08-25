from flask import Blueprint, render_template, g
from routes.auth import login_required
from database.db import query_db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = g.user['id']
    
    resumes = query_db('''
        SELECT r.*, 
        (SELECT MAX(score) FROM ats_analysis WHERE resume_id = r.id) as best_ats_score
        FROM resumes r 
        WHERE r.user_id = ? 
        ORDER BY r.updated_at DESC
    ''', (user_id,))

    portfolio = query_db('SELECT * FROM portfolios WHERE user_id = ?', (user_id,), one=True)
    ats_scans = query_db('SELECT COUNT(*) as count FROM ats_analysis WHERE user_id = ?', (user_id,), one=True)
    
    # Calculate profile completion metric
    completion_score = 40  # Base score for registering
    if len(resumes) > 0:
        completion_score += 30
    if portfolio:
        completion_score += 30

    stats = {
        'total_resumes': len(resumes),
        'portfolio_active': portfolio['is_public'] if portfolio else 0,
        'ats_scans': ats_scans['count'] if ats_scans else 0,
        'completion_score': completion_score
    }

    return render_template('dashboard.html', resumes=resumes, stats=stats, portfolio=portfolio)