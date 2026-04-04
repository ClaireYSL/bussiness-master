from shared.config import get_settings


def main() -> None:
    settings = get_settings()
    print(f"worker started: {settings.app_name}")


if __name__ == "__main__":
    main()

