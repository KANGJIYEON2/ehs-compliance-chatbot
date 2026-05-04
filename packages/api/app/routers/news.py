"""산업재해 뉴스 피드 라우터"""

from fastapi import APIRouter, Query

from app.services.news_service import news_service

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("")
def get_news(
    limit: int = Query(15, ge=1, le=50),
    analyze: bool = Query(True, description="GPT 분석 포함 여부"),
):
    return news_service.get_news(limit=limit, analyze=analyze)
