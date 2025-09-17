from ai_provider import AIProvider
from ai.openai_service import OpenAIService
from ai.gemini_service import GeminiService

class AIService:
    @staticmethod
    def get_service(provider: AIProvider, **kwargs):
        if provider == AIProvider.OPENAI:
            return OpenAIService()
        elif provider == AIProvider.GEMINI:
            gemini_api_key = kwargs.get("gemini_api_key")
            if not gemini_api_key:
                raise ValueError("Gemini API key is required for the Gemini provider")
            return GeminiService(api_key=gemini_api_key)
        else:
            raise ValueError("Unsupported AI provider")