import os
from flask import Flask, render_template
from config import Config
from database.db import close_db, init_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register Database Teardown
    app.teardown_appcontext(close_db)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.resume import resume_bp
    from routes.ai import ai_bp
    from routes.ats import ats_bp
    from routes.portfolio import portfolio_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(ats_bp)
    app.register_blueprint(portfolio_bp)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('404.html', message="Internal Server Error"), 500

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        init_db(app)
    app.run(debug=True, host='127.0.0.1', port=5000)