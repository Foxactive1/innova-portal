from __future__ import annotations

from datetime import datetime, timedelta

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

from .ai import get_ai, AIServiceError, AIUnavailableError
from .database import db
from .extensions import csrf, limiter
from .models import Lead, Product, Service
from .utils import clamp_text, parse_price, validate_email_address

main = Blueprint("main", __name__)


@main.route("/")
def index():
    services = Service.query.order_by(Service.titulo.asc()).all()
    products = Product.query.order_by(Product.nome.asc()).all()
    return render_template("index.html", services=services, products=products)


@main.route("/contact", methods=["POST"])
@limiter.limit(lambda: current_app.config["CONTACT_RATE_LIMIT"])
def contact():
    name_limit = current_app.config["MAX_NAME_LENGTH"]
    message_limit = current_app.config["MAX_CONTACT_MESSAGE_LENGTH"]

    nome = clamp_text(request.form.get("nome"), name_limit)
    raw_message = (request.form.get("mensagem") or "").strip()

    if not nome or not raw_message:
        flash("Preencha todos os campos do formulário.", "warning")
        return redirect(url_for("main.index", _anchor="contact"))

    if len(raw_message) > message_limit:
        flash(
            f"A mensagem ultrapassou o limite de {message_limit} caracteres.",
            "warning",
        )
        return redirect(url_for("main.index", _anchor="contact"))

    try:
        email = validate_email_address(request.form.get("email"))
    except ValueError as exc:
        flash(str(exc), "warning")
        return redirect(url_for("main.index", _anchor="contact"))

    ai = get_ai()
    try:
        analise = ai.classify_lead(raw_message)
    except AIUnavailableError:
        current_app.logger.info("Groq indisponível para classificar lead.")
        analise = "Classificação automática indisponível no momento."
    except AIServiceError:
        current_app.logger.exception("Falha ao classificar lead com IA.")
        analise = "Classificação automática indisponível no momento."

    try:
        lead = Lead(
            nome=nome,
            email=email,
            mensagem=raw_message,
            ai_summary=analise,          # <- campo existente no modelo
        )
        db.session.add(lead)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Falha ao salvar lead.")
        flash("Não foi possível salvar sua mensagem. Tente novamente.", "danger")
        return redirect(url_for("main.index", _anchor="contact"))

    flash("Mensagem enviada com sucesso. Em breve retornaremos.", "success")
    return redirect(url_for("main.index"))


@main.route("/api/chat", methods=["POST"])
@csrf.exempt
@limiter.limit(lambda: current_app.config["CHAT_RATE_LIMIT"])
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get("message") or "").strip()
    max_length = current_app.config["MAX_CHAT_MESSAGE_LENGTH"]

    if not user_message:
        return jsonify({"reply": "Envie uma mensagem para continuar."}), 400

    if len(user_message) > max_length:
        return (
            jsonify(
                {
                    "reply": (
                        f"Mensagem muito longa. Limite máximo de {max_length} caracteres."
                    )
                }
            ),
            400,
        )

    ai = get_ai()
    try:
        reply, intent = ai.generate_chat_reply(user_message)
    except AIUnavailableError:
        return jsonify({"reply": "Assistente de IA indisponível no momento."}), 503
    except AIServiceError:
        current_app.logger.exception("Falha no endpoint público de chat.")
        return (
            jsonify(
                {
                    "reply": (
                        "Assistente temporariamente indisponível. "
                        "Tente novamente em instantes."
                    )
                }
            ),
            503,
        )

    return jsonify({"reply": reply, "meta": {"intent": intent}})


@main.route("/dashboard")
@login_required
def dashboard():
    leads = Lead.query.order_by(Lead.created_at.desc()).all()   # campo correto
    services = Service.query.order_by(Service.titulo.asc()).all()
    products = Product.query.order_by(Product.nome.asc()).all()
    return render_template(
        "dashboard.html",
        leads=leads,
        services=services,
        products=products,
        ai_enabled=bool(current_app.config.get("GROQ_API_KEY")),
        hide_chat=True,
    )


@main.route("/add-service", methods=["POST"])
@login_required
def add_service():
    title_limit = current_app.config["MAX_TITLE_LENGTH"]
    description_limit = current_app.config["MAX_DESCRIPTION_LENGTH"]

    titulo = clamp_text(request.form.get("titulo"), title_limit)
    descricao = clamp_text(request.form.get("descricao"), description_limit)

    if not titulo or not descricao:
        flash("Título e descrição são obrigatórios.", "warning")
        return redirect(url_for("main.dashboard"))

    try:
        service = Service(titulo=titulo, descricao=descricao)
        db.session.add(service)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Falha ao criar serviço.")
        flash("Não foi possível cadastrar o serviço.", "danger")
        return redirect(url_for("main.dashboard"))

    flash("Serviço cadastrado com sucesso.", "success")
    return redirect(url_for("main.dashboard"))


@main.route("/add-product", methods=["POST"])
@login_required
def add_product():
    title_limit = current_app.config["MAX_TITLE_LENGTH"]
    description_limit = current_app.config["MAX_DESCRIPTION_LENGTH"]

    nome = clamp_text(request.form.get("nome"), title_limit)
    descricao = clamp_text(request.form.get("descricao"), description_limit)

    if not nome or not descricao:
        flash("Nome e descrição são obrigatórios.", "warning")
        return redirect(url_for("main.dashboard"))

    try:
        preco = parse_price(request.form.get("preco"))
    except ValueError as exc:
        flash(str(exc), "warning")
        return redirect(url_for("main.dashboard"))

    try:
        product = Product(nome=nome, preco=preco, descricao=descricao)
        db.session.add(product)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Falha ao criar produto.")
        flash("Não foi possível cadastrar o produto.", "danger")
        return redirect(url_for("main.dashboard"))

    flash("Produto cadastrado com sucesso.", "success")
    return redirect(url_for("main.dashboard"))


@main.route("/delete-service/<int:item_id>", methods=["POST"])
@login_required
def delete_service(item_id):
    service = Service.query.get_or_404(item_id)

    try:
        db.session.delete(service)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Falha ao remover serviço.")
        flash("Não foi possível remover o serviço.", "danger")
        return redirect(url_for("main.dashboard"))

    flash(f'Serviço "{service.titulo}" removido com sucesso.', "success")
    return redirect(url_for("main.dashboard"))


@main.route("/delete-product/<int:item_id>", methods=["POST"])
@login_required
def delete_product(item_id):
    product = Product.query.get_or_404(item_id)

    try:
        db.session.delete(product)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Falha ao remover produto.")
        flash("Não foi possível remover o produto.", "danger")
        return redirect(url_for("main.dashboard"))

    flash(f'Produto "{product.nome}" removido com sucesso.', "success")
    return redirect(url_for("main.dashboard"))


@main.route("/generate-description", methods=["POST"])
@login_required
@limiter.limit(lambda: current_app.config["AI_RATE_LIMIT"])
def generate_description():
    title_limit = current_app.config["MAX_TITLE_LENGTH"]
    titulo = clamp_text(request.form.get("titulo"), title_limit)
    item_type = clamp_text(request.form.get("tipo"), 20)

    if not titulo or item_type not in {"service", "product"}:
        return jsonify({"error": "Parâmetros inválidos."}), 400

    ai = get_ai()
    try:
        description = ai.generate_marketing_description(titulo, item_type)
    except AIUnavailableError:
        return jsonify({"error": "IA indisponível no momento."}), 503
    except AIServiceError:
        current_app.logger.exception("Falha ao gerar descrição com IA.")
        return jsonify({"error": "Erro ao gerar descrição."}), 503

    return jsonify({"description": description})


@main.route("/health")
def health():
    return {"status": "ok"}, 200


@main.route("/weekly-summary", methods=["POST"])
@login_required
@limiter.limit(lambda: current_app.config["AI_RATE_LIMIT"])
def weekly_summary():
    week_ago = datetime.utcnow() - timedelta(days=7)
    max_leads = current_app.config["MAX_SUMMARY_LEADS"]
    leads = (
        Lead.query.filter(Lead.created_at >= week_ago)   # campo correto
        .order_by(Lead.created_at.desc())
        .limit(max_leads)
        .all()
    )

    if not leads:
        flash("Nenhum lead recebido nos últimos 7 dias.", "info")
        return redirect(url_for("main.dashboard"))

    ai = get_ai()
    try:
        summary = ai.generate_weekly_summary(leads)
    except (AIUnavailableError, AIServiceError):
        current_app.logger.exception("Falha ao gerar resumo semanal.")
        flash("Não foi possível gerar o resumo semanal.", "danger")
        return redirect(url_for("main.dashboard"))

    return render_template(
        "summary.html",
        summary=summary,
        total_leads=len(leads),
        period_days=7,
        hide_chat=True,
    )