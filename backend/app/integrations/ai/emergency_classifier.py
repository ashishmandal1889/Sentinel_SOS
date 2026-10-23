"""
Sentinel SOS - AI Emergency Classifier.

Classifies citizen's free-text emergency descriptions to suggest an emergency category
and extract key triage flags using Google Gemini (with rule-based fallback).
NOTE: Treat AI as decision support only. Never allow LLM output to replace human judgment.
"""

import json
from typing import Any, Dict, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.schemas.incident import EmergencyType


class EmergencyClassifier:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.api_key = settings.LLM_API_KEY

    async def classify_emergency_text(self, text: str) -> Dict[str, Any]:
        """Classifies text into suggested emergency category with confidence score."""
        if not text or not text.strip():
            return {
                "suggested_type": EmergencyType.GENERAL.value,
                "confidence": 0.5,
                "summary": "No description provided.",
                "is_urgent": False,
                "source": "fallback",
            }

        # If Gemini is enabled and API key is present, use Gemini API
        if self.provider == "gemini" and self.api_key:
            try:
                ai_result = await self._call_gemini(text)
                if ai_result:
                    return ai_result
            except Exception as e:
                logger.error(f"[GEMINI AI ERROR] Emergency classification failed: {e}. Falling back to heuristic.")

        # Fallback keyword-based heuristic
        return self._heuristic_fallback(text)

    async def _call_gemini(self, text: str) -> Optional[Dict[str, Any]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        prompt = (
            "You are an intelligent emergency triage assistant for the Sentinel SOS emergency response platform. "
            "Analyze the citizen's emergency report description below and classify it.\n"
            "Valid emergency types are strictly one of: MEDICAL, POLICE, FIRE, ACCIDENT, NATURAL_DISASTER, GENERAL.\n"
            "Return valid JSON ONLY with exactly these keys:\n"
            "{\n"
            '  "suggested_type": "<one of the valid types>",\n'
            '  "confidence": <float between 0.0 and 1.0>,\n'
            '  "summary": "<short 1-line objective summary>",\n'
            '  "is_urgent": <true or false>\n'
            "}\n\n"
            f"Citizen Emergency Report: \"\"\"{text}\"\"\""
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1,
            },
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)

        if resp.status_code == 200:
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            parsed = json.loads(raw_text.strip())
            parsed["source"] = f"gemini ({self.model})"
            logger.info(f"[GEMINI AI CLASSIFIED] Type: {parsed.get('suggested_type')} | Confidence: {parsed.get('confidence')}")
            return parsed
        else:
            logger.warning(f"[GEMINI AI HTTP ERROR] {resp.status_code}: {resp.text}")
            return None

    def _heuristic_fallback(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        if any(w in text_lower for w in ["heart", "breath", "bleed", "unconscious", "ambulance", "fall", "injury"]):
            return {
                "suggested_type": EmergencyType.MEDICAL.value,
                "confidence": 0.95,
                "summary": "Potential acute medical crisis identified from description.",
                "is_urgent": True,
                "source": "heuristic",
            }
        elif any(w in text_lower for w in ["fire", "smoke", "burn", "explosion"]):
            return {
                "suggested_type": EmergencyType.FIRE.value,
                "confidence": 0.92,
                "summary": "Fire/smoke hazard detected.",
                "is_urgent": True,
                "source": "heuristic",
            }
        elif any(w in text_lower for w in ["robbery", "theft", "assault", "intruder", "stalker", "weapon"]):
            return {
                "suggested_type": EmergencyType.POLICE.value,
                "confidence": 0.90,
                "summary": "Police or physical security intervention indicated.",
                "is_urgent": True,
                "source": "heuristic",
            }

        return {
            "suggested_type": EmergencyType.GENERAL.value,
            "confidence": 0.6,
            "summary": "General emergency assistance requested.",
            "is_urgent": False,
            "source": "heuristic",
        }


emergency_classifier = EmergencyClassifier()
