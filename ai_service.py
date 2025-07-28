from openai import OpenAI
import re
import json
from ai_provider import AIProvider
from gemini_service import GeminiService

class AIService:    
    def __init__(self, provider: AIProvider, gemini_api_key: str = None):
        self.provider = provider
        if self.provider == AIProvider.GEMINI:
            if not gemini_api_key:
                raise ValueError("Gemini API key is required for the Gemini provider")
            self.gemini_service = GeminiService(api_key=gemini_api_key)

    def summarize_with_emojis(self, article_text, target_language='en'):
        if self.provider == AIProvider.GEMINI:
            return self.gemini_service.summarize_with_emojis(article_text, target_language)

        target_language = target_language.lower()
        if target_language == 'en':
            target_language = 'English B2 level'
        elif target_language == 'es':
            target_language = 'Espanish' 
        elif target_language == 'ru':
            target_language = 'Russian'
        system_prompt = (
            "You are a helpful assistant. Summarize the following Spanish news article "
            f"in 2-3 sentences in {target_language} with a slightly sarcastic or humorous style where it appropriate. End the summary with 1-3 emojis that match the tone of the news."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": article_text}
        ]
        response = self.init_agent(messages)
        summary = response.choices[0].message.content
        final_summary = re.sub(r'<think>.*?</think>', '', summary, flags=re.DOTALL).strip()
        return final_summary

    def init_agent(self, messages, response_format = {"type": "text"}):
        if self.provider == AIProvider.GEMINI:
            # This method is specific to OpenAI, so we'll need to adapt it or bypass it for Gemini
            raise NotImplementedError("init_agent is not implemented for the Gemini provider")

        client =  OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        response = client.chat.completions.create(
            model="microsoft/phi-4-reasoning-plus",  
            messages=messages,
            response_format=response_format,
            temperature=0.7
        )
        
        return response

    def summarize_with_emojis_and_evaluate(self, article_text, target_language='en'):
        if self.provider == AIProvider.GEMINI:
            return self.gemini_service.summarize_with_emojis_and_evaluate(article_text, target_language)

        target_language = target_language.lower()
        if target_language == 'en':
            target_language = 'English'
        elif target_language == 'es':
            target_language = 'Epanish' 
        elif target_language == 'ru':
            target_language = 'Russian'
        system_prompt = (
        "You are a helpful assistant. Summarize the following Spanish news article "
            f"in 2-3 sentences in {target_language} with a slightly sarcastic style. End the summary with 1-3 emojis that match the tone of the news."
            "After the summary and emojis, provide an evaluation of the article on three dimensions, each on a scale of 1 to 10. "
            "Use the format: Scores: E:X M:Y P:Z where X is 'expat impact', Y is 'Malaga capital relevance', and Z is 'political vs. new feature' (1 for internal politics, 10 for cool new stuff)."
            "Example: Summary of the article... 🤔 Scores: E:7 M:9 P:4"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": article_text}
        ]
        client =  OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        response = client.chat.completions.create(
            model="qwen3-4b",  
            messages=messages,
            temperature=0.7
        )
        full_response_text = response.choices[0].message.content
        cleaned_response_text = re.sub(r'<think>.*?</think>', '', full_response_text, flags=re.DOTALL).strip()

        scores = {"expat_impact": 0, "malaga_relevance": 0, "feature_vs_politics": 0}
        scores_match = re.search(r"Scores:\s*E:(\d{1,2})\s*M:(\d{1,2})\s*P:(\d{1,2})", cleaned_response_text, re.IGNORECASE)
        
        summary_text = cleaned_response_text
        if scores_match:
            try:
                scores["expat_impact"] = int(scores_match.group(1))
                scores["malaga_relevance"] = int(scores_match.group(2))
                scores["feature_vs_politics"] = int(scores_match.group(3))
                summary_text = re.sub(r"Scores:\s*E:\d{1,2}\s*M:\d{1,2}\s*P:\d{1,2}", "", cleaned_response_text, flags=re.IGNORECASE).strip()
            except ValueError:
                print(f"Warning: Could not parse scores from AI response: {scores_match.groups()}")
        else:
            print(f"Warning: Scores pattern not found in AI response: '{cleaned_response_text}'")

        expat_impact = scores.get("expat_impact", 0)
        malaga_relevance = scores.get("malaga_relevance", 0)
        feature_vs_politics = scores.get("feature_vs_politics", 0)
        final_score = (expat_impact + malaga_relevance + feature_vs_politics) / len(scores) if scores else 0
        return summary_text, final_score   

    def evaluate_article(self, article_text):
        if self.provider == AIProvider.GEMINI:
            return self.gemini_service.evaluate_article(article_text)

        system_prompt = (
            "You are a news evaluation agent. Your role is to score local news stories based on how likely they are to interest a general audience, "
            "especially international readers and expats in Malaga. " )
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "article_evaluation",
                "schema": {
                    "type": "object",
                    "properties": {
                        "expat_impact": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "description": "How relevant or impactful the news is for expatriates (1-10)"
                        },
                        "event_weight": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "description": "Significance or uniqueness of the event (1-10)"
                        },
                        "politics": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 10,
                            "description": "Non-political/innovation score (0=political, 10=non-political/innovative)"
                        },
                        "timeliness": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "description": "Time-sensitivity or urgency (1-10)"
                        },
                        "practical_utility": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "description": "Usefulness for reader's daily life (1-10)"
                        }
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
        response = self.init_agent(messages, response_format=response_format)
        full_response_text = response.choices[0].message.content
        cleaned_response_text = re.sub(r'<think>.*?</think>', '', full_response_text, flags=re.DOTALL).strip()
        cleaned_response_text = re.sub(r'//.*', '', cleaned_response_text)

        if "json" in cleaned_response_text:
            cleaned_response_text = cleaned_response_text.strip('```json\n').strip('```').strip()

        try:
            json_object = json.loads(cleaned_response_text)
            expat_impact = json_object.get("expat_impact", 0)
            event_weight = json_object.get("event_weight", 0)
            politics_vs_innovation = json_object.get("politics", 0)
            timeliness = json_object.get("timeliness", 0)
            practical_utility = json_object.get("practical_utility", 0)

            scores = [expat_impact, event_weight, politics_vs_innovation, timeliness, practical_utility]
            non_zero_scores = [score for score in scores if score != 0]
            total_score = sum(non_zero_scores) / len(non_zero_scores) if non_zero_scores else 0
            return total_score
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from response: {cleaned_response_text}")
            return 0