#---------------------------------------------------------------------------------------
# Name:        init
# Purpose:
#
# Author:      DIONE CASTRO ALVES
#
# Created:     16/04/2026
# Copyright:   (c) DIONE CASTRO ALVES 2026
# Licence:     <your licence>
#---------------------------------------------------------------------------------------

import os
from flask import Flask
from .database import db
from . import models  # <-- Importa todos os modelos ANTES do create_all
from .routes import main
from .auth import auth

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-prod')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()  # Agora as tabelas serão criadas corretamente

    return app