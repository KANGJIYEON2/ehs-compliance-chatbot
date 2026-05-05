"""국가법령정보센터 API 라우터 — 동적 법령 검색/조회"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.user import User
from app.dependencies import get_current_user
from app.services.law_api_client import law_api_client

router = APIRouter(prefix="/api/law", tags=["law-api"])


@router.get("/search")
def search_law(
    q: str = Query(..., min_length=1, description="검색 키워드"),
    page: int = Query(1, ge=1),
    user: User = Depends(get_current_user),
):
    """법령 검색 (키워드)"""
    if not law_api_client.is_ready:
        raise HTTPException(status_code=503, detail="법령 API가 설정되지 않았습니다")
    return law_api_client.search_law(q, page=page)


@router.get("/detail/{law_id}")
def get_law_detail(
    law_id: str,
    user: User = Depends(get_current_user),
):
    """법령 상세 (조문 포함)"""
    if not law_api_client.is_ready:
        raise HTTPException(status_code=503, detail="법령 API가 설정되지 않았습니다")
    result = law_api_client.get_law_detail(law_id)
    if not result:
        raise HTTPException(status_code=404, detail="법령을 찾을 수 없습니다")
    return result


@router.get("/articles")
def search_articles(
    q: str = Query(..., min_length=1),
    law_name: str | None = None,
    user: User = Depends(get_current_user),
):
    """조문 검색"""
    if not law_api_client.is_ready:
        raise HTTPException(status_code=503, detail="법령 API가 설정되지 않았습니다")
    return law_api_client.search_articles(q, law_name=law_name)
