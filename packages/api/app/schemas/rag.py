from typing import Any
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., description="질문 문장")
    topk: int = Field(5, ge=1, le=20, description="검색 상위 K")
    mode: str = Field("auto", description="auto | law | rule")
    ctx_chars: int = Field(6000, ge=1000, le=20000, description="컨텍스트 최대 길이")
    dbs: list[str] | None = Field(None, description="사용할 DB 폴더 목록")


class AskResponse(BaseModel):
    question: str
    answer: str
    mode: str
    hits: list[dict[str, Any]]
    used_dbs: list[str]


class ReloadRequest(BaseModel):
    dbs: list[str] | None = Field(None, description="로드할 DB 폴더 목록")


class HealthResponse(BaseModel):
    status: str
    dbs: list[dict[str, Any]]
