from flask import Flask, jsonify, send_from_directory, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models.user import db
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.user import user_bp
from routes.admin import admin_bp
from routes.upload import upload_bp
from routes.avatar import avatar_bp
from services.email_service import mail
from sqlalchemy.engine import Engine
from sqlalchemy import event
import sqlite3
import os
import logging
import traceback

def create_app():
    """Application factory: configure app, extensions, and blueprints."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    CORS(app)          # Enable CORS for all routes
    db.init_app(app)   # Bind SQLAlchemy to app

        # ✅ 自动创建数据库（instance/app.db）
    with app.app_context():
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if db_uri.startswith("sqlite:///"):
            # 提取数据库文件路径
            db_file = db_uri.replace("sqlite:///", "")
            db_dir = os.path.dirname(db_file) or "."

            # 确保数据库目录存在（例如 instance/）
            os.makedirs(db_dir, exist_ok=True)

            # 如果数据库文件不存在，则创建
            if not os.path.exists(db_file):
                print(f"⚙️  Creating new database at {db_file} ...")
                db.create_all()

    JWTManager(app)    # Setup JWT
    mail.init_app(app) # Setup Flask-Mail

    # Register API blueprints (versioned under /api)
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api")
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(avatar_bp, url_prefix="/api")

    @app.after_request
    def attach_new_token(response):
        """Attach a refreshed JWT to the response header if present."""
        if hasattr(g, "new_token"):
            response.headers["X-New-Token"] = g.new_token
        return response

    @app.route("/static/avatars/<path:filename>")
    def serve_avatar(filename):
        """Serve avatar images from the /static/avatars directory."""
        return send_from_directory(os.path.join(app.root_path, "static", "avatars"), filename)

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global error handler: log traceback and return 500."""
        logging.error("Exception occurred: %s", traceback.format_exc())
        return jsonify({"msg": "Internal Server Error"}), 500

    return app


# Enable SQLite foreign key constraints on each new connection
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
