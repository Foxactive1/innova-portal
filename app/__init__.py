from __future__ import annotations

from datetime import datetime
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import Flask

from config import get_config

from .database import db
from .extensions import csrf, limiter, login_manager
from .models import User


def create_app(config_class=None):
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class or get_config())

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    from .auth import auth
    from .routes import main

    app.register_blueprint(main)
    app.register_blueprint(auth)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    @app.context_processor
    def inject_globals():
        return {
            "app_name": "InNovaIdeia",
            "support_email": "innovaideia2023@gmail.com",
            "current_year": datetime.now().year,
            "chat_max_length": app.config["MAX_CHAT_MESSAGE_LENGTH"],
        }

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        click.echo("Banco inicializado com sucesso.")

    @app.cli.command("seed-demo")
    def seed_demo_command():
        from .seed import seed_demo_data

        created = seed_demo_data()
        click.echo(
            "Seed concluido. "
            f"Servicos criados: {created['services']}, "
            f"produtos criados: {created['products']}."
        )

    return app
