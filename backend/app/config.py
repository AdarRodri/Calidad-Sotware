import os
from dotenv import load_dotenv

load_dotenv()


def _database_uri():
    """Usa DATABASE_URL (base de datos en la nube). Si no existe, arma la URL local con DB_*."""
    url = os.getenv("DATABASE_URL")
    if url:
        # Algunos proveedores entregan "postgres://"; SQLAlchemy necesita "postgresql://".
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    return (
        f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', '')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'medicitas')}"
    )


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "tu-secret-key-por-defecto")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tu-jwt-secret-por-defecto")

    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Las bases de datos en la nube cierran conexiones inactivas: se verifican antes de usarlas.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
