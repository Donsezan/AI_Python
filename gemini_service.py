import google.generativeai as genai
from base_ai_service import BaseAIService
import ai_prompts
import response_parser

class GeminiService(BaseAIService):
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def summarize_with_emojis(self, article_text, target_language='en'):
        prompt = ai_prompts.get_summarize_with_emojis_prompt(target_language)
        full_prompt = f"{prompt}\n\n{article_text}"

        response = self.model.generate_content(full_prompt)
        summary = response.text
        return response_parser.parse_summary_with_emojis(summary)

    def summarize_with_emojis_and_evaluate(self, article_text, target_language='en'):
        prompt = ai_prompts.get_summarize_with_emojis_and_evaluate_prompt(target_language)
        full_prompt = f"{prompt}\n\n{article_text}"

        response = self.model.generate_content(full_prompt)
        full_response_text = response.text
        return response_parser.parse_summary_with_emojis_and_evaluate(full_response_text)

    def evaluate_article(self, article_text):
        prompt = ai_prompts.get_evaluate_article_prompt()
        full_prompt = (
            f"{prompt} Provide a JSON response with the following schema: "
            '{"expat_impact": int, "event_weight": int, "politics": int, "timeliness": int, "practical_utility": int}.'
            f"\n\n{article_text}"
        )

        response = self.model.generate_content(full_prompt)
        return response_parser.parse_evaluate_article(response.text)
