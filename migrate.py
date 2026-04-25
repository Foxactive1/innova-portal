from sqlalchemy import inspect, text

from app import create_app
from app.database import db


def ensure_legacy_columns():
    inspector = inspect(db.engine)
    table_names = set(inspector.get_table_names())
    if "lead" not in table_names:
        print("Tabela lead ainda nao existe. Nada a migrar.")
        return

    columns = {column["name"] for column in inspector.get_columns("lead")}
    if "analise" in columns:
        print("Coluna analise ja existe.")
        return

    with db.engine.begin() as connection:
        connection.execute(text("ALTER TABLE lead ADD COLUMN analise VARCHAR(300)"))

    print("Coluna analise criada com sucesso.")


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Schema verificado.")
        ensure_legacy_columns()


if __name__ == "__main__":
    main()
