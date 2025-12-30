from app.core.config import Settings


def test_settings_builds_database_uri_from_env(monkeypatch):
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "password")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("GOOGLE_API_KEY", "dummy")

    settings = Settings()
    assert (
        settings.SQLALCHEMY_DATABASE_URI
        == "postgresql+asyncpg://postgres:password@localhost:5432/test_db"
    )
