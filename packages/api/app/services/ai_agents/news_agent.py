"""뉴스 분석 Agent — 산업재해 뉴스 → 사고유형/유의점/법령근거 분석"""

from __future__ import annotations

import time
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from typing import Any

from app.services.ai_agents.base import BaseAgent

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

CACHE_TTL = 1800  # 30분


@dataclass
class NewsItem:
    title: str
    link: str
    pub_date: str
    source: str


class NewsAgent(BaseAgent):
    name = "news_agent"
    system_prompt = "당신은 한국 산업안전 전문가다. 산업재해 뉴스를 분석하여 사고 유형, 심각도, 예방 유의점, 관련 법령을 JSON 형식으로 반환한다."
    temperature = 0.3

    def __init__(self) -> None:
        super().__init__()
        self._cache: list[dict[str, Any]] = []
        self._cache_time: float = 0
        self._cache_key: str = ""

    def _fetch_rss(self, url: str) -> list[NewsItem]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            root = ET.fromstring(resp.read().decode("utf-8"))
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

    def _fetch_all(self, limit: int = 20) -> list[NewsItem]:
        all_items: list[NewsItem] = []
        seen: set[str] = set()
        for feed in NEWS_FEEDS:
            for item in self._fetch_rss(feed["url"]):
                key = item.title.strip()[:50]
                if key not in seen:
                    seen.add(key)
                    all_items.append(item)
        return all_items[:limit]

    def analyze(self, news_items: list[NewsItem]) -> list[dict[str, Any]]:
        """뉴스 목록을 GPT로 일괄 분석"""
        if not self.is_ready or not news_items:
            return [asdict(item) for item in news_items]

        titles_text = "\n".join(
            f"{i+1}. {item.title}" for i, item in enumerate(news_items)
        )

        prompt = f"""다음은 최근 산업재해/산업안전 관련 뉴스 제목들이다.
각 뉴스에 대해 JSON 배열로 분석 결과를 반환하라.

뉴스 제목:
{titles_text}

각 항목:
- "index": 뉴스 번호 (1부터)
- "incident_type": 사고 유형 (caught/fall/collision/electric/fire/suffocation/falling_object/chemical/other 중 하나, 판단 불가 시 null)
- "severity_hint": 추정 심각도 (death/serious/minor/near_miss 중 하나, 판단 불가 시 null)
- "summary": 1줄 요약 (50자 이내)
- "prevention_tips": 예방 유의점 2-3개 (짧은 문장 배열)
- "related_law": 관련 법령 1개 (예: "산업안전보건법 제38조", 판단 불가 시 null)

JSON 배열만 반환. 마크다운 코드블록 없이 순수 JSON만."""

        try:
            analyses = self._chat_json(prompt)
        except Exception:
            analyses = []

        analysis_map = {a.get("index", 0): a for a in analyses} if analyses else {}
        results = []
        for i, item in enumerate(news_items):
            a = analysis_map.get(i + 1, {})
            results.append({
                **asdict(item),
                "incident_type": a.get("incident_type"),
                "severity_hint": a.get("severity_hint"),
                "summary": a.get("summary"),
                "prevention_tips": a.get("prevention_tips"),
                "related_law": a.get("related_law"),
            })
        return results

    def get_news(self, limit: int = 15, use_ai: bool = True) -> list[dict[str, Any]]:
        """뉴스 수집 + 분석 (캐싱 적용)"""
        now = time.time()
        cache_key = f"{limit}_{use_ai}"

        if self._cache and (now - self._cache_time) < CACHE_TTL and self._cache_key == cache_key:
            return self._cache[:limit]

        items = self._fetch_all(limit=limit)

        if use_ai and self.is_ready:
            result = self.analyze(items)
        else:
            result = [asdict(item) for item in items]

        self._cache = result
        self._cache_time = now
        self._cache_key = cache_key
        return result
