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

    app.register_blueprint(user_bp, url_prefix='/api/v1/users')
    app.register_blueprint(file_bp, url_prefix='/api/v1/files')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])

