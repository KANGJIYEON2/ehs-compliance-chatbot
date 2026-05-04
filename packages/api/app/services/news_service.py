"""산업재해 뉴스 피드 ��비스: RSS 수집 + GPT 분석"""

from __future__ import annotations

import json
import time
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from typing import Any

from openai import OpenAI

from app.config import Settings

# Google News RSS — 산업재해/산업안전 키워드
NEWS_FEEDS = [
    {
        "url": "https://news.google.com/rss/search?q=%EC%82%B0%EC%97%85%EC%9E%AC%ED%95%B4&hl=ko&gl=KR&ceid=KR:ko",
        "keyword": "산업재해",
    },
    {
        "url": "https://news.google.com/rss/search?q=%EC%82%B0%EC%97%85%EC%95%88%EC%A0%84+%EC%82%AC%EA%B3%A0&hl=ko&gl=KR&ceid=KR:ko",
        "keyword": "산업안전 사고",
    },
]

CACHE_TTL = 1800  # 30분 캐시


@dataclass
class NewsItem:
    title: str
    link: str
    pub_date: str
    source: str


@dataclass
class AnalyzedNews:
    title: str
    link: str
    pub_date: str
    source: str
    incident_type: str | None = None
    severity_hint: str | None = None
    summary: str | None = None
    prevention_tips: list[str] | None = None
    related_law: str | None = None


class NewsService:
    def __init__(self) -> None:
        self._client: OpenAI | None = None
        self._cache: dict[str, Any] = {}
        self._cache_time: float = 0

    def initialize(self, settings: Settings) -> None:
        if settings.OPENAI_API_KEY:
            self._client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=settings.OPENAI_TIMEOUT,
            )

    def _fetch_rss(self, url: str) -> list[NewsItem]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            xml_bytes = resp.read()
            root = ET.fromstring(xml_bytes.decode("utf-8"))

            items = []
            for item in root.findall(".//item"):
                title_el = item.find("title")
                link_el = item.find("link")
                pub_el = item.find("pubDate")
                source_el = item.find("source")

                if title_el is None or link_el is None:
                    continue

                items.append(NewsItem(
                    title=title_el.text or "",
                    link=link_el.text or "",
                    pub_date=pub_el.text if pub_el is not None else "",
                    source=source_el.text if source_el is not None else "",
                ))
            return items
        except Exception:
            return []

    def _fetch_all_news(self, limit: int = 20) -> list[NewsItem]:
        all_items: list[NewsItem] = []
        seen_titles: set[str] = set()

        for feed in NEWS_FEEDS:
            items = self._fetch_rss(feed["url"])
            for item in items:
                # 제목 기반 중복 제거
                key = item.title.strip()[:50]
                if key not in seen_titles:
                    seen_titles.add(key)
                    all_items.append(item)

        return all_items[:limit]

    def _analyze_batch(self, news_items: list[NewsItem]) -> list[AnalyzedNews]:
        if not self._client or not news_items:
            return [
                AnalyzedNews(**asdict(item))
                for item in news_items
            ]

        titles_text = "\n".join(
            f"{i+1}. {item.title}" for i, item in enumerate(news_items)
        )

        prompt = f"""다음은 최근 산업재해/산업안전 관련 뉴스 제���들이다.
각 뉴스에 대해 JSON 배열로 분석 결과를 반환하라.

뉴스 제목:
{titles_text}

각 항목에 대해:
- "index": 뉴스 번호 (1��터)
- "incident_type": 사고 유형 (caught/fall/collision/electric/fire/suffocation/falling_object/chemical/other 중 하나, 판단 불가 시 null)
- "severity_hint": 추정 심각도 (death/serious/minor/near_miss 중 하나, 판단 불가 시 null)
- "summary": 1줄 요약 (50자 이내)
- "prevention_tips": 예방 유의점 2-3개 (짧은 문장 배열)
- "related_law": 관련 법령 1개 (예: "산업안전보건법 제38조", 판단 불가 시 null)

JSON 배열만 반���하라. 마크다운 코드블록 없이 순수 JSON만."""

        try:
            resp = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 한국 산업안전 전문���다. JSON 형식으로만 답하라."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            raw = resp.choices[0].message.content.strip()
            # JSON 파싱 (```json ... ``` 래핑 제거)
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
            analyses = json.loads(raw)
        except Exception:
            analyses = []

        results: list[AnalyzedNews] = []
        analysis_map = {a.get("index", 0): a for a in analyses} if analyses else {}

        for i, item in enumerate(news_items):
            a = analysis_map.get(i + 1, {})
            results.append(AnalyzedNews(
                title=item.title,
                link=item.link,
                pub_date=item.pub_date,
                source=item.source,
                incident_type=a.get("incident_type"),
                severity_hint=a.get("severity_hint"),
                summary=a.get("summary"),
                prevention_tips=a.get("prevention_tips"),
                related_law=a.get("related_law"),
            ))

        return results

    def get_news(self, limit: int = 15, analyze: bool = True) -> list[dict[str, Any]]:
        now = time.time()
        cache_key = f"news_{limit}_{analyze}"

        if cache_key in self._cache and (now - self._cache_time) < CACHE_TTL:
            return self._cache[cache_key]

        items = self._fetch_all_news(limit=limit)

        if analyze and self._client:
            analyzed = self._analyze_batch(items)
        else:
            analyzed = [AnalyzedNews(**asdict(item)) for item in items]

        result = [asdict(a) for a in analyzed]
        self._cache[cache_key] = result
        self._cache_time = now
        return result


# 싱글톤
news_service = NewsService()
