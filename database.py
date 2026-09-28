from typing import Generator
from sqlmodel import Session, SQLModel, create_engine

DATABASE_FILE_NAME = "lost_and_found.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE_NAME}"

# create SQLite database engine with check_same_thread=False for multithreaded FastAPI requests
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)


def create_db_and_tables() -> None:
    """Create all tables defined in SQLModel metadata on application startup."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency to provide a database session per request."""
    with Session(engine) as session:
        yield session
