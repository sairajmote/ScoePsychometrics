import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables. Locally uses .env; in Azure uses system env vars.
# We don't use override=True so system environment always takes precedence.
load_dotenv()

# Use os.environ here so the app crashes immediately if DATABASE_URL is missing
try:
    SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]
except KeyError:
    print("CRITICAL ERROR: DATABASE_URL environment variable is not set.")
    raise

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
