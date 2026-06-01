from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from flask_login import UserMixin
from sqlalchemy import Numeric
from sqlalchemy.orm import relationship

from .database import db


# ============================================================================
# USER
# ============================================================================

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        index=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(30),
        default="admin",
        nullable=False,
        index=True
    )

    is_active_user = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    last_login = db.Column(
        db.DateTime,
        nullable=True
    )

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# ============================================================================
# LEAD
# ============================================================================

class Lead(db.Model):
    __tablename__ = "lead"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        index=True,
        nullable=False
    )

    telefone = db.Column(
        db.String(30),
        nullable=True
    )

    empresa = db.Column(
        db.String(120),
        nullable=True
    )

    mensagem = db.Column(
        db.Text,
        nullable=False
    )

    # ------------------------------------------------------------------------
    # PIPELINE
    # ------------------------------------------------------------------------

    status = db.Column(
        db.String(30),
        default="novo",
        nullable=False,
        index=True
    )

    lead_temperature = db.Column(
        db.String(20),
        default="warm",
        nullable=False,
        index=True
    )

    lead_score = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        index=True
    )

    # ------------------------------------------------------------------------
    # IA / NLP
    # ------------------------------------------------------------------------

    intent = db.Column(
        db.String(50),
        nullable=True,
        index=True
    )

    confidence = db.Column(
        db.Float,
        nullable=True
    )

    source_channel = db.Column(
        db.String(50),
        nullable=True
    )

    urgency = db.Column(
        db.String(30),
        nullable=True
    )

    estimated_budget = db.Column(
        db.String(50),
        nullable=True
    )

    ai_summary = db.Column(
        db.Text,
        nullable=True
    )

    ai_analysis = db.Column(
        db.JSON,
        nullable=True
    )

    tags = db.Column(
        db.JSON,
        default=list
    )

    # ------------------------------------------------------------------------
    # METADATA
    # ------------------------------------------------------------------------

    ip_address = db.Column(
        db.String(45),
        nullable=True
    )

    user_agent = db.Column(
        db.String(500),
        nullable=True
    )

    source = db.Column(
        db.String(100),
        default="website"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    deleted_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # ------------------------------------------------------------------------
    # RELACIONAMENTOS
    # ------------------------------------------------------------------------

    conversations = relationship(
        "Conversation",
        back_populates="lead",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    interactions = relationship(
        "Interaction",
        back_populates="lead",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    def __repr__(self):
        return (
            f"<Lead {self.nome} "
            f"[{self.status}] "
            f"Score:{self.lead_score}>"
        )


# ============================================================================
# CONVERSATION MEMORY
# ============================================================================

class Conversation(db.Model):
    __tablename__ = "conversation"

    id = db.Column(db.Integer, primary_key=True)

    lead_id = db.Column(
        db.Integer,
        db.ForeignKey("lead.id"),
        nullable=False,
        index=True
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    intent = db.Column(
        db.String(50),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    lead = relationship(
        "Lead",
        back_populates="conversations"
    )

    def __repr__(self):
        return f"<Conversation Lead:{self.lead_id} Role:{self.role}>"


# ============================================================================
# INTERACTIONS / TIMELINE
# ============================================================================

class Interaction(db.Model):
    __tablename__ = "interaction"

    id = db.Column(db.Integer, primary_key=True)

    lead_id = db.Column(
        db.Integer,
        db.ForeignKey("lead.id"),
        nullable=False,
        index=True
    )

    event_type = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    extra_data = db.Column(        # <--- nome alterado
        db.JSON,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    lead = relationship(
        "Lead",
        back_populates="interactions"
    )

    def __repr__(self):
        return (
            f"<Interaction "
            f"{self.event_type} "
            f"Lead:{self.lead_id}>"
        )

# ============================================================================
# SERVICE
# ============================================================================

class Service(db.Model):
    __tablename__ = "service"

    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(
        db.String(150),
        nullable=False,
        index=True
    )

    slug = db.Column(
        db.String(180),
        unique=True,
        nullable=True,
        index=True
    )

    categoria = db.Column(
        db.String(80),
        nullable=True,
        index=True
    )

    descricao = db.Column(
        db.Text,
        nullable=False
    )

    ativo = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        index=True
    )

    featured = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<Service {self.titulo}>"


# ============================================================================
# PRODUCT
# ============================================================================

class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(150),
        nullable=False,
        index=True
    )

    slug = db.Column(
        db.String(180),
        unique=True,
        nullable=True,
        index=True
    )

    categoria = db.Column(
        db.String(80),
        nullable=True,
        index=True
    )

    sku = db.Column(
        db.String(80),
        nullable=True,
        unique=True
    )

    preco = db.Column(
        Numeric(10, 2),
        nullable=False
    )

    descricao = db.Column(
        db.Text,
        nullable=False
    )

    estoque = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    ativo = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        index=True
    )

    featured = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    imagem_url = db.Column(
        db.String(500),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    @property
    def display_price(self):
        return f"R$ {Decimal(self.preco):.2f}"

    def __repr__(self):
        return (
            f"<Product {self.nome} "
            f"R${Decimal(self.preco):.2f}>"
        )