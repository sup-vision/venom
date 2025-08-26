from flask import Flask
from mongoengine import connect
from config import Config
from routes.user_routes import user_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Connect MongoEngine
    connect(host=Config.MONGO_URI)

    # Register routes
    app.register_blueprint(user_bp, url_prefix="/api/v1/users")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)