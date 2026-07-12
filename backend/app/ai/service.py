import json
from abc import ABC, abstractmethod
from google import genai
from pydantic import BaseModel
from app.config import settings
from app.ai.schemas import PreVisitSummary, PostVisitSummary

class AIProvider(ABC):
    @abstractmethod
    async def generate_pre_visit_summary(self, symptoms: str) -> PreVisitSummary:
        """Generate a pre-visit clinical summary based on symptoms."""
        pass

    @abstractmethod
    async def generate_post_visit_summary(self, notes: str) -> PostVisitSummary:
        """Generate a post-visit patient-friendly summary based on doctor notes."""
        pass

class GeminiProvider(AIProvider):
    def __init__(self):
        # We are using synchronous client for now as Celery tasks run synchronously in threads
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

    async def generate_pre_visit_summary(self, symptoms: str) -> PreVisitSummary:
        prompt = f"""
        You are a clinical AI assistant. Analyze the following patient symptoms and provide a pre-visit summary for the doctor.
        Symptoms: {symptoms}
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PreVisitSummary,
                temperature=0.2
            ),
        )
        return PreVisitSummary.model_validate_json(response.text)

    async def generate_post_visit_summary(self, notes: str) -> PostVisitSummary:
        prompt = f"""
        You are a helpful medical assistant. Translate the following doctor's clinical notes into a friendly, easy-to-understand summary for the patient.
        Doctor Notes: {notes}
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PostVisitSummary,
                temperature=0.2
            ),
        )
        return PostVisitSummary.model_validate_json(response.text)

class AIService:
    """Abstraction layer - business logic calls this, not the provider directly."""
    def __init__(self, provider: AIProvider | None = None):
        self.provider = provider or GeminiProvider()
        
    async def get_pre_visit_summary(self, symptoms: str) -> PreVisitSummary:
        return await self.provider.generate_pre_visit_summary(symptoms)
        
    async def get_post_visit_summary(self, notes: str) -> PostVisitSummary:
        return await self.provider.generate_post_visit_summary(notes)
