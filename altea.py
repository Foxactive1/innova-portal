from app import create_app
from app.database import db

app = create_app()

with app.app_context():
    db.session.execute("ALTER TABLE lead ADD COLUMN analise TEXT")
    db.session.commit()