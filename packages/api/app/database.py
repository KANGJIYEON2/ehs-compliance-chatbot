from sqlalchemy import create_engine, func, cast, String
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import Generator


class Base(DeclarativeBase):
    pass


engine = None
SessionLocal: sessionmaker | None = None
_is_sqlite: bool = True


def init_db(database_url: str) -> None:
    global engine, SessionLocal, _is_sqlite
    _is_sqlite = database_url.startswith("sqlite")
    connect_args = {}
    if _is_sqlite:
        connect_args = {"check_same_thread": False}
    engine = create_engine(database_url, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def year_month(column):
    """DB 엔진에 맞는 YYYY-MM 추출 (SQLite strftime / PostgreSQL to_char)"""
    if _is_sqlite:
        return func.strftime("%Y-%m", column)
    return func.to_char(column, "YYYY-MM")


def extract_year(column):
    """DB 엔진에 맞는 연도 추출"""
    if _is_sqlite:
        return func.strftime("%Y", column)
    return cast(func.extract("year", column), String)


def extract_month(column):
    """DB 엔진에 맞는 월 추출 (zero-padded)"""
    if _is_sqlite:
        return func.strftime("%m", column)
    return func.to_char(column, "MM")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
