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
import sys
import os

# Adiciona a pasta pai (raiz do projeto) ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Agora podemos importar a função create_app do pacote app
from app import create_app
from app.models import Service, Product
from app.database import db

SERVICES = [
    {"titulo": "Desenvolvimento Web", "descricao": "Criação de sistemas web modernos com Flask, Django e React."},
    {"titulo": "Inteligência Artificial", "descricao": "Automação de processos, chatbots inteligentes, análise preditiva."},
    {"titulo": "Consultoria em TI", "descricao": "Transformação digital estratégica e otimização de infraestrutura."},
    {"titulo": "Automação com WhatsApp", "descricao": "Chatbots e funis de vendas automatizados para WhatsApp."},
    {"titulo": "SaaS Personalizado", "descricao": "Plataformas white-label e sistemas multi-tenant escaláveis."}
]

PRODUCTS = [
    {"nome": "CRM Inteligente", "preco": 299.90, "descricao": "Gestão de clientes com IA integrada."},
    {"nome": "E-commerce SaaS", "preco": 499.00, "descricao": "Plataforma completa para vendas online."},
    {"nome": "WhatsApp Bot Pro", "preco": 199.90, "descricao": "Chatbot avançado para WhatsApp."}
]

def main():
    app = create_app()
    with app.app_context():
        for data in SERVICES:
            if not Service.query.filter_by(titulo=data["titulo"]).first():
                db.session.add(Service(**data))
                print(f"✅ Serviço: {data['titulo']}")
        for data in PRODUCTS:
            if not Product.query.filter_by(nome=data["nome"]).first():
                db.session.add(Product(**data))
                print(f"✅ Produto: {data['nome']}")
        db.session.commit()
        print("🎉 População concluída!")

if __name__ == "__main__":
    main()