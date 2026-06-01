from __future__ import annotations

from datetime import datetime
from pathlib import Path
import os

import click
from dotenv import load_dotenv
from flask import Flask

from config import get_config

from .database import db
from .extensions import csrf, limiter, login_manager
from .models import User


def create_app(config_class=None):
    # 📍 Base path
    project_root = Path(__file__).resolve().parent.parent

    # 📍 Load .env
    load_dotenv(project_root / ".env")

    app = Flask(__name__, instance_relative_config=True)

    # 📍 Config
    app.config.from_object(config_class or get_config())

    # 🔐 HARDENING: garante SECRET_KEY
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-key-insegura")

    # 📁 Instance folder
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # 🔌 Extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # ⚠️ Limiter com fallback seguro
    if not app.config.get("RATELIMIT_STORAGE_URI"):
        app.config["RATELIMIT_STORAGE_URI"] = "memory://"

    limiter.init_app(app)

    # 🤖 Inicializa o módulo de IA (AIOrchestrator)
    from .ai import init_ai
    init_ai(app)  # registra app.extensions["ai"]

    # 📦 Blueprints
    from .auth import auth
    from .routes import main

    app.register_blueprint(main)
    app.register_blueprint(auth)

    # 👤 User loader
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    # 🌐 Context globals
    @app.context_processor
    def inject_globals():
        return {
            "app_name": "InNovaIdeia",
            "support_email": "innovaideia2023@gmail.com",
            "current_year": datetime.now().year,
            "chat_max_length": app.config.get("MAX_CHAT_MESSAGE_LENGTH", 500),
        }

    # 🛠 CLI - init db
    @app.cli.command("init-db")
    def init_db_command():
        with app.app_context():
            db.create_all()
        click.echo("Banco inicializado com sucesso.")

    # 🌱 CLI - seed
    @app.cli.command("seed-demo")
    def seed_demo_command():
        from .seed import seed_demo_data

        with app.app_context():
            created = seed_demo_data()

        click.echo(
            "Seed concluído. "
            f"Serviços: {created['services']}, "
            f"Produtos: {created['products']}."
        )

    return app