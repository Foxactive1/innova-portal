from __future__ import annotations

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from .database import db
from .extensions import limiter
from .models import User
from .utils import clamp_text, validate_username

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config["LOGIN_RATE_LIMIT"], methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = clamp_text(request.form.get("username"), 30)
        password = request.form.get("password", "")

        if not username or not password:
            flash("Preencha usuario e senha para continuar.", "warning")
            return render_template("login.html", hide_chat=True)

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session.clear()
            login_user(user)
            session.permanent = True
            flash("Login realizado com sucesso.", "success")
            return redirect(url_for("main.dashboard"))

        flash("Usuario ou senha invalidos.", "danger")

    return render_template("login.html", hide_chat=True)


@auth.route("/register", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config["REGISTER_RATE_LIMIT"], methods=["POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        try:
            username = validate_username(request.form.get("username"))
        except ValueError as exc:
            flash(str(exc), "warning")
            return render_template("register.html", hide_chat=True)

        if len(password) < 8:
            flash("A senha deve ter pelo menos 8 caracteres.", "warning")
            return render_template("register.html", hide_chat=True)

        if password != password_confirm:
            flash("As senhas nao coincidem.", "danger")
            return render_template("register.html", hide_chat=True)

        if User.query.filter_by(username=username).first():
            flash("Este nome de usuario ja esta em uso.", "danger")
            return render_template("register.html", hide_chat=True)

        try:
            user = User(username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Nao foi possivel concluir o cadastro. Tente novamente.", "danger")
            return render_template("register.html", hide_chat=True)

        flash("Cadastro concluido. Agora voce ja pode fazer login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", hide_chat=True)


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Sessao encerrada com sucesso.", "info")
    return redirect(url_for("main.index"))
