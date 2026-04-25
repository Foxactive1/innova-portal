from app import create_app
from app.seed import seed_demo_data


def main():
    app = create_app()
    with app.app_context():
        created = seed_demo_data()
        print(
            "Seed concluido. "
            f"Servicos criados: {created['services']}, "
            f"produtos criados: {created['products']}."
        )


if __name__ == "__main__":
    main()
