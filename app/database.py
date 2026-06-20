from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Usar SQLite para desarrollo sin necesidad de MySQL
SQLALCHEMY_DATABASE_URL = "sqlite:///./gestion_medicamentos.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necesario para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
