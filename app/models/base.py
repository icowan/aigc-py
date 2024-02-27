from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import Request

from app.config.config import get_config

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
config = get_config()
user = config.db_user
password = quote_plus(config.db_password)
host = config.db_host
port = config.db_port
db_name = config.db_name
charset = config.db_charset
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset={charset}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args={"check_same_thread": False}
    echo=config.app_debug
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

if config.db_auto_migrate:
    Base.metadata.create_all(engine)


# Dependency
def get_db(request: Request) -> SessionLocal:
    return request.state.db
