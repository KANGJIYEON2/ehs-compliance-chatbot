"""음성 보고 Agent — Whisper STT + GPT 구조화 파싱"""

from __future__ import annotations

import io
from typing import Any

from app.services.ai_agents.base import BaseAgent


class VoiceAgent(BaseAgent):
    name = "voice_agent"
    system_prompt = (
        "당신은 한국 산업현장 안전 전문가다. "
        "음성으로 보고된 현장 상황을 분석하여 사고 보고서 양식에 맞게 구조화한다."
    )
    temperature = 0.2

    def transcribe(self, audio_bytes: bytes, filename: str = "audio.webm") -> str:
        """Whisper API로 음성 → 텍스트"""
        if not self._client:
            raise RuntimeError("Voice agent not initialized")

        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        response = self._client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ko",
        )
        return response.text

    def parse_report(self, text: str, site_processes: list[str] | None = None) -> dict[str, Any]:
        """텍스트 → 구조화된 사고 보고 데이터"""
        if not self.is_ready:
            return {"error": "Agent not initialized"}

        context = ""
        if site_processes:
            context = f"\n현장 공정/장비 목록: {', '.join(site_processes)}"

        prompt = f"""다음은 현장 작업자가 음성으로 보고한 내용이다.{context}

보고 내용: "{text}"

이 내용을 사고 보고서 양식에 맞게 JSON으로 구조화하라:
{{
  "incident_type": "caught|fall|collision|electric|fire|suffocation|falling_object|chemical|other 중 하나",
  "severity": "death|serious|minor|near_miss 중 하나 (판단 불가 시 near_miss)",
  "description": "사고 설명 (원문 기반 정리)",
  "cause_estimate": "추정 원인 (없으면 null)",
  "location_hint": "위치 정보 (없으면 null)",
  "urgency": "high|medium|low"
}}

JSON만 반환."""

        try:
            return self._chat_json(prompt)
        except Exception as e:
            return {"error": str(e), "raw_text": text}
