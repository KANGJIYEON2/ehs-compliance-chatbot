"""법령 근거 Agent — 사고/상황 → 관련 법조문 검색 + 요약"""

from __future__ import annotations

from typing import Any

from app.services.ai_agents.base import BaseAgent


class LawAgent(BaseAgent):
    name = "law_agent"
    system_prompt = (
        "당신은 대한민국 EHS(환경·안전·보건) 법령 전문가다. "
        "산업안전보건법, 중대재해처벌법, 산업안전보건기준에 관한 규칙 등에 정통하다. "
        "사고나 상황에 대해 관련 법적 근거를 정확히 찾아 요약한다. "
        "반드시 법령명과 조문 번호를 명시하라."
    )
    temperature = 0.2

    def find_legal_basis(
        self,
        incident_type: str,
        description: str,
        rag_context: str | None = None,
    ) -> dict[str, Any]:
        """사고 정보 → 관련 법령 근거 검색"""
        if not self.is_ready:
            return {"error": "AI agent not initialized"}

        context_block = ""
        if rag_context:
            context_block = f"\n\n[RAG 검색 결과 (참고 근거)]\n{rag_context}"

        prompt = f"""다음 산업재해에 대한 법적 근거를 찾아라.

사고 유형: {incident_type}
상황: {description}
{context_block}

다음 JSON 형식으로 반환:
{{
  "primary_laws": [
    {{"law": "법령명", "article": "조문 번호", "summary": "핵심 내용 요약", "relevance": "이 사고와의 관련성"}}
  ],
  "employer_obligations": ["사업주 의무 1", "사업주 의무 2"],
  "penalties": "위반 시 처벌 내용 요약",
  "compliance_checklist": ["컴플라이언스 점검 항목 1", "점검 항목 2"]
}}

JSON만 반환."""

        try:
            return self._chat_json(prompt)
        except Exception as e:
            return {"error": str(e)}

    def summarize_regulation(self, law_name: str, article: str) -> str:
        """특정 법조문 요약"""
        if not self.is_ready:
            return "AI agent not initialized"

        prompt = f"{law_name} {article}의 핵심 내용을 3줄 이내로 요약하라. 현장 적용 관점에서."
        return self._chat(prompt)
