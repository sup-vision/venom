# app.py
from flask import Flask
from db import init_db

def create_app():
    app = Flask(__name__)
    
    app.config.from_pyfile('config.py', silent=True)

    client, db, fs = init_db(app)
    # attach for global access inside blueprints
    app.mongo_client = client
    app.db = db
    app.fs = fs

    from routes.user_routes import bp as user_bp
    from routes.file_routes import bp as file_bp
    from routes.student_routes import bp as student_bp
    from routes.schedule_routes import bp as shcedule_bp
    from routes.attendance_routes import bp as attendance_bp

    app.register_blueprint(user_bp, url_prefix='/api/v1/users')
    app.register_blueprint(file_bp, url_prefix='/api/v1/files')
    app.register_blueprint(student_bp, url_prefix='/api/v1/students')
    app.register_blueprint(shcedule_bp, url_prefix='/api/v1/schedule')
    app.register_blueprint(attendance_bp, url_prefix='/api/v1/attendance')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])

