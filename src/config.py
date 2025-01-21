import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/gestion_penas")
    DEBUG = True
