import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "tu-secret-key-por-defecto")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tu-jwt-secret-por-defecto")

    # Si existe DATABASE_URL la usa (Render la provee), si no, usa postgres local o sqlite
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or \
        f"postgresql://{os.getenv('DB_USER', 'postgres')}:" \
        f"{os.getenv('DB_PASSWORD', '')}@" \
        f"{os.getenv('DB_HOST', 'localhost')}:" \
        f"{os.getenv('DB_PORT', '5432')}/" \
        f"{os.getenv('DB_NAME', 'medicitas')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False