import google.generativeai as genai
from base_ai_service import BaseAIService
import ai_prompts
import response_parser

class GeminiService(BaseAIService):
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

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
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "article_evaluation",
                "schema": {
                    "type": "object",
                    "properties": {
                        "expat_impact": {"type": "integer", "minimum": 1, "maximum": 10, "description": "How relevant or impactful the news is for expatriates (1-10)"},
                        "event_weight": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Significance or uniqueness of the event (1-10)"},
                        "politics": {"type": "integer", "minimum": 0, "maximum": 10, "description": "Non-political/innovation score (0=political, 10=non-political/innovative)"},
                        "timeliness": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Time-sensitivity or urgency (1-10)"},
                        "practical_utility": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Usefulness for reader's daily life (1-10)"}
                    },
                    "required": ["expat_impact", "event_weight", "politics", "timeliness", "practical_utility"],
                    "additionalProperties": False
                }
            }
        }
        full_prompt = (
                    f"{prompt} Provide a JSON response with the following schema: {response_format}"
                    
                    f"\n\n{article_text}"
                )
        response = self.model.generate_content(
            full_prompt,
            generation_config={
                "response_mime_type": "application/json"
            }
        )

        print(response.text)
        return response_parser.parse_evaluate_article(response.text)
