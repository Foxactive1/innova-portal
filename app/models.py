from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin

from .database import db


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


class Lead(db.Model):
    __tablename__ = "lead"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), index=True, nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow, index=True, nullable=False)
    analise = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f"<Lead {self.nome} - {self.email}>"


class Service(db.Model):
    __tablename__ = "service"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Service {self.titulo}>"


class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=False)

    @property
    def display_price(self):
        return f"R$ {self.preco:.2f}"

    def __repr__(self):
        return f"<Product {self.nome} R${self.preco:.2f}>"
