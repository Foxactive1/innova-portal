from __future__ import annotations

from .database import db
from .models import Product, Service

SERVICES = [
    {
        "titulo": "Desenvolvimento Web",
        "descricao": (
            "Criacao de sistemas web modernos, portais institucionais e aplicacoes "
            "sob medida com foco em performance, seguranca e escala."
        ),
    },
    {
        "titulo": "Inteligencia Artificial",
        "descricao": (
            "Automacao de processos, copilotos de atendimento e fluxos inteligentes "
            "para acelerar operacoes e vendas."
        ),
    },
    {
        "titulo": "Consultoria em TI",
        "descricao": (
            "Diagnostico tecnico, redesenho de arquitetura e boas praticas para "
            "elevar maturidade digital e reduzir risco operacional."
        ),
    },
    {
        "titulo": "Automacao com WhatsApp",
        "descricao": (
            "Bots, funis e jornadas conversacionais integradas ao WhatsApp Business "
            "para captação, suporte e conversao."
        ),
    },
    {
        "titulo": "SaaS Personalizado",
        "descricao": (
            "Plataformas escalaveis e modelos white-label desenhados para operacao "
            "de assinatura, multi-tenant e crescimento previsivel."
        ),
    },
]

PRODUCTS = [
    {
        "nome": "CRM Inteligente",
        "preco": 299.90,
        "descricao": "Gestao comercial com IA, follow-up automatico e visao unificada do funil.",
    },
    {
        "nome": "E-commerce SaaS",
        "preco": 499.00,
        "descricao": "Loja online pronta para vender com pagamentos, catalogo e integracoes.",
    },
    {
        "nome": "WhatsApp Bot Pro",
        "preco": 199.90,
        "descricao": "Atendimento automatizado com menus, mensagens contextuais e integracao via API.",
    },
]


def seed_demo_data():
    created = {"services": 0, "products": 0}

    for payload in SERVICES:
        existing = Service.query.filter_by(titulo=payload["titulo"]).first()
        if not existing:
            db.session.add(Service(**payload))
            created["services"] += 1

    for payload in PRODUCTS:
        existing = Product.query.filter_by(nome=payload["nome"]).first()
        if not existing:
            db.session.add(Product(**payload))
            created["products"] += 1

    db.session.commit()
    return created
