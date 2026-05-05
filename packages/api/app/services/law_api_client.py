"""국가법령정보센터 Open API 클라이언트"""

from __future__ import annotations

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Any

from app.config import Settings


class LawAPIClient:
    """국가법령정보센터 API — 법령 검색 + 조문 조회"""

    BASE_URL = "http://www.law.go.kr/DRF"

    def __init__(self) -> None:
        self._key: str = ""

    def initialize(self, settings: Settings) -> None:
        self._key = settings.LAW_API_KEY

    @property
    def is_ready(self) -> bool:
        return bool(self._key)

    def _request(self, service: str, params: dict) -> ET.Element | None:
        """API 요청 → XML 파싱"""
        if not self._key:
            return None

        params["OC"] = self._key
        params["type"] = "XML"
        query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        url = f"{self.BASE_URL}/{service}.do?{query}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=15)
            return ET.fromstring(resp.read().decode("utf-8"))
        except Exception:
            return None

    def search_law(self, query: str, page: int = 1, display: int = 10) -> list[dict[str, Any]]:
        """법령 검색 (키워드)"""
        root = self._request("lawSearch", {
            "target": "law",
            "query": query,
            "display": str(display),
            "page": str(page),
        })
        if root is None:
            return []

        results = []
        for item in root.findall(".//law"):
            law_id = item.findtext("법령일련번호", "")
            results.append({
                "law_id": law_id,
                "law_name": item.findtext("법령명한글", ""),
                "law_type": item.findtext("법령구분", ""),  # 법률, 시행령, 시행규칙
                "department": item.findtext("소관부처", ""),
                "promulgation_date": item.findtext("공포일자", ""),
                "enforcement_date": item.findtext("시행일자", ""),
            })
        return results

    def get_law_detail(self, law_id: str) -> dict[str, Any] | None:
        """법령 상세 조회 (조문 포함)"""
        root = self._request("lawService", {
            "target": "law",
            "MST": law_id,
        })
        if root is None:
            return None

        # 기본 정보
        info = root.find(".//기본정보")
        result: dict[str, Any] = {
            "law_id": law_id,
            "law_name": info.findtext("법령명_한글", "") if info is not None else "",
            "articles": [],
        }

        # 조문
        for article in root.findall(".//조문단위"):
            article_no = article.findtext("조문번호", "")
            article_title = article.findtext("조문제목", "")
            article_content = article.findtext("조문내용", "")

            # 항
            paragraphs = []
            for para in article.findall(".//항"):
                para_no = para.findtext("항번호", "")
                para_content = para.findtext("항내용", "")
                paragraphs.append({"no": para_no, "content": para_content or ""})

            result["articles"].append({
                "article_no": f"제{article_no}조" if article_no else "",
                "title": article_title or "",
                "content": article_content or "",
                "paragraphs": paragraphs,
            })

        return result

    def search_articles(self, query: str, law_name: str | None = None) -> list[dict[str, Any]]:
        """조문 검색"""
        params: dict = {
            "target": "jo",
            "query": query,
            "display": "20",
        }
        if law_name:
            params["law"] = law_name

        root = self._request("lawSearch", params)
        if root is None:
            return []

        results = []
        for item in root.findall(".//jo"):
            results.append({
                "law_name": item.findtext("법령명한글", ""),
                "article_no": item.findtext("조문번호", ""),
                "article_title": item.findtext("조문제목", ""),
                "article_content": item.findtext("조문내용", "")[:500],
            })
        return results


# 싱글톤
law_api_client = LawAPIClient()
