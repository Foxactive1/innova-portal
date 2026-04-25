#---------------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      DIONE CASTRO ALVES
#
# Created:     25/04/2026
# Copyright:   (c) DIONE CASTRO ALVES 2026
# Licence:     <your licence>
#---------------------------------------------------------------------------------------
# C:\innovaprojects\innova_portal\init_db.py

from app import create_app
from app.database import db
from app.seed import seed_demo_data

def init_database():
    app = create_app()
    with app.app_context():
        # Criar tabelas
        db.create_all()
        print("✅ Tabelas criadas!")

        # Popular dados
        created = seed_demo_data()
        print(f"✅ Dados populados!")
        print(f"   Serviços: {created['services']}")
        print(f"   Produtos: {created['products']}")

if __name__ == "__main__":
    init_database()
