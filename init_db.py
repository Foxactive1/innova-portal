"""
Script para criar tabelas e popular dados de demonstração.
Uso: python init_db.py
"""

import sys
import os

# Garante o caminho do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.seed import seed_demo_data


def init_database():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")

        created = seed_demo_data()
        print("✅ Dados populados!")
        print(f"   Serviços: {created['services']}")
        print(f"   Produtos: {created['products']}")


if __name__ == "__main__":
    init_database()