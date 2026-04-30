from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, ConfigDict
from typing import List

# =========================
# DATABASE CONFIG (FIXED)
# =========================

DATABASE_URL = "postgresql://nischit:Test12345@2024-a.postgres.database.azure.com:5432/postgres"

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# =========================
# DATABASE MODEL
# =========================

class QueryModel(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    query = Column(String, nullable=False)

# Create tables
Base.metadata.create_all(bind=engine)

# =========================
# PYDANTIC SCHEMA (FIXED)
# =========================

class Query(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    query: str

    model_config = ConfigDict(from_attributes=True)

# =========================
# FASTAPI APP
# =========================

app = FastAPI()

# =========================
# DB DEPENDENCY
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# HEALTH CHECK
# =========================

@app.get("/")
def health_check():
    return {"status": "ok"}

# =========================
# CREATE QUERY
# =========================

@app.post("/queries", response_model=Query)
def create_query(query: Query, db: Session = Depends(get_db)):
    db_query = QueryModel(**query.model_dump())
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query

# =========================
# GET ALL QUERIES
# =========================

@app.get("/queries", response_model=List[Query])
def get_queries(db: Session = Depends(get_db)):
    queries = db.query(QueryModel).all()
    if not queries:
        raise HTTPException(status_code=404, detail="No queries found")
    return queries