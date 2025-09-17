from openai import OpenAI
from base_ai_service import BaseAIService
import ai_prompts
import response_parser

class OpenAIService(BaseAIService):
    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    def _init_agent(self, messages, response_format={"type": "text"}, model="microsoft/phi-4-reasoning-plus"):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            response_format=response_format,
            temperature=0.7
        )
        return response

    def summarize_with_emojis(self, article_text, target_language='en'):
        system_prompt = ai_prompts.get_summarize_with_emojis_prompt(target_language)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": article_text}
        ]
        response = self._init_agent(messages)
        summary = response.choices[0].message.content
        return response_parser.parse_summary_with_emojis(summary)

    def summarize_with_emojis_and_evaluate(self, article_text, target_language='en'):
        system_prompt = ai_prompts.get_summarize_with_emojis_and_evaluate_prompt(target_language)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": article_text}
        ]

        response = self._init_agent(messages, model="qwen3-4b")
        full_response_text = response.choices[0].message.content
        return response_parser.parse_summary_with_emojis_and_evaluate(full_response_text)

    def evaluate_article(self, article_text):
        system_prompt = ai_prompts.get_evaluate_article_prompt()
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

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": article_text}
        ]
        response = self._init_agent(messages, response_format=response_format)
        full_response_text = response.choices[0].message.content
        return response_parser.parse_evaluate_article(full_response_text)
