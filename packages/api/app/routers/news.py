"""산업재해 뉴스 피드 라우터 (NewsAgent 기반)"""

from fastapi import APIRouter, Query


router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("")
def get_news(
    limit: int = Query(15, ge=1, le=50),
    analyze: bool = Query(True, description="AI 분석 포함 여부"),
):
    from app.main import news_agent
    return news_agent.get_news(limit=limit, use_ai=analyze)
