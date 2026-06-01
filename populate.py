"""
Script apenas para popular dados de demonstração (sem recriar tabelas).
Uso: python populate.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.seed import seed_demo_data


def main():
    app = create_app()
    with app.app_context():
        created = seed_demo_data()
        print(
            "✅ Seed concluído. "
            f"Serviços criados: {created['services']}, "
            f"Produtos criados: {created['products']}."
        )


if __name__ == "__main__":
    main()