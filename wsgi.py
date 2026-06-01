
from app import create_app
import sys
import os

# Garante que o diretório raiz do projeto (onde está a pasta 'app') seja reconhecido
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


app = create_app()
