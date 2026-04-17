#---------------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      DIONE CASTRO ALVES
#
# Created:     16/04/2026
# Copyright:   (c) DIONE CASTRO ALVES 2026
# Licence:     <your licence>
#---------------------------------------------------------------------------------------

#!/usr/bin/env python3
"""
Script para popular o banco de dados com serviços e produtos iniciais da InNovaIdeia.
Executar: python populate_db.py
"""

import sys
import os

# Adiciona o diretório atual ao path para importar a aplicação
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from database import db
from models import Service, Product

# Importa a função create_app ou cria um app manualmente
try:
    from __init__ import create_app
    app = create_app()
except ImportError:
    # Fallback: cria app básico caso __init__ não esteja configurado
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

# Dados iniciais para serviços
SERVICES = [
    {
        "titulo": "Desenvolvimento Web",
        "descricao": "Criação de sistemas web modernos com Flask, Django e React. Sites institucionais, e-commerces e aplicações sob medida."
    },
    {
        "titulo": "Inteligência Artificial",
        "descricao": "Automação de processos, chatbots inteligentes, análise preditiva e soluções com machine learning para o seu negócio."
    },
    {
        "titulo": "Consultoria em TI",
        "descricao": "Transformação digital estratégica, otimização de infraestrutura e adoção de boas práticas de desenvolvimento."
    },
    {
        "titulo": "Automação com WhatsApp",
        "descricao": "Criação de chatbots e funis de vendas automatizados para WhatsApp Business API."
    },
    {
        "titulo": "SaaS Personalizado",
        "descricao": "Plataformas white-label, assinaturas e sistemas multi-tenant escaláveis."
    }
]

# Dados iniciais para produtos (opcional)
PRODUCTS = [
    {
        "nome": "CRM Inteligente",
        "preco": 299.90,
        "descricao": "Gestão de clientes com IA integrada, automação de follow-ups e relatórios preditivos."
    },
    {
        "nome": "E-commerce SaaS",
        "preco": 499.00,
        "descricao": "Plataforma completa para vendas online, com pagamentos, catálogo e integrações."
    },
    {
        "nome": "WhatsApp Bot Pro",
        "preco": 199.90,
        "descricao": "Chatbot avançado para WhatsApp, com envio de mídia, menus interativos e API."
    }
]

def populate_services():
    """Adiciona serviços se não existirem."""
    print("📦 Verificando serviços...")
    for data in SERVICES:
        existing = Service.query.filter_by(titulo=data["titulo"]).first()
        if not existing:
            service = Service(titulo=data["titulo"], descricao=data["descricao"])
            db.session.add(service)
            print(f"  ✅ Adicionado serviço: {data['titulo']}")
        else:
            print(f"  ⏭️  Serviço já existe: {data['titulo']}")
    db.session.commit()

def populate_products():
    """Adiciona produtos se não existirem."""
    print("\n📦 Verificando produtos...")
    for data in PRODUCTS:
        existing = Product.query.filter_by(nome=data["nome"]).first()
        if not existing:
            product = Product(
                nome=data["nome"],
                preco=data["preco"],
                descricao=data["descricao"]
            )
            db.session.add(product)
            print(f"  ✅ Adicionado produto: {data['nome']} (R$ {data['preco']})")
        else:
            print(f"  ⏭️  Produto já existe: {data['nome']}")
    db.session.commit()

def main():
    with app.app_context():
        print("🚀 Iniciando população do banco de dados...\n")
        populate_services()
        populate_products()
        print("\n✨ População concluída com sucesso!")

if __name__ == "__main__":
    main()