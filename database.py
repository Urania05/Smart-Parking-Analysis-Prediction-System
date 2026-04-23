from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Docker üzerindeki veri tabanımıza bağlanıyoruz
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin123@localhost:5432/akilli_otopark"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()