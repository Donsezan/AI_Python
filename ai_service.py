from openai import OpenAI
import re

class AIService:    
    def __init__(self):
        pass

    def summarize_with_emojis(self, article_text, target_language='en'):
        target_language = target_language.lower()
        if target_language == 'en':
            target_language = 'English B2 level'
        elif target_language == 'es':
            target_language = 'Espanish' 
        elif target_language == 'ru':
            target_language = 'Russian'
        system_prompt = (
            "You are a helpful assistant. Summarize the following Spanish news article "
            f"in 2-3 sentences in {target_language} with a slightly sarcastic style. End the summary with 1-3 emojis that match the tone of the news."
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
        summary = response.choices[0].message.content
        final_summary = re.sub(r'<think>.*?</think>', '', summary, flags=re.DOTALL).strip()
        return final_summary

    def summarize_with_emojis_and_evaluate(self, article_text, target_language='en'):
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
        # Remove any <think> tags
        cleaned_response_text = re.sub(r'<think>.*?</think>', '', full_response_text, flags=re.DOTALL).strip()

        # Attempt to parse scores
        scores = {"expat_impact": 0, "malaga_relevance": 0, "feature_vs_politics": 0}
        scores_match = re.search(r"Scores:\s*E:(\d{1,2})\s*M:(\d{1,2})\s*P:(\d{1,2})", cleaned_response_text, re.IGNORECASE)
        
        summary_text = cleaned_response_text
        if scores_match:
            try:
                scores["expat_impact"] = int(scores_match.group(1))
                scores["malaga_relevance"] = int(scores_match.group(2))
                scores["feature_vs_politics"] = int(scores_match.group(3))
                # Remove score string from summary
                summary_text = re.sub(r"Scores:\s*E:\d{1,2}\s*M:\d{1,2}\s*P:\d{1,2}", "", cleaned_response_text, flags=re.IGNORECASE).strip()
            except ValueError:
                print(f"Warning: Could not parse scores from AI response: {scores_match.groups()}")
                # Keep summary_text as cleaned_response_text if scores can't be parsed, so we don't lose the text
        else:
            print(f"Warning: Scores pattern not found in AI response: '{cleaned_response_text}'")
        expat_impact = scores.get("expat_impact") or 0
        malaga_relevance = scores.get("malaga_relevance") or 0
        feature_vs_politics = scores.get("feature_vs_politics") or 0
        final_score = (expat_impact + malaga_relevance + feature_vs_politics) / len(scores)
        return summary_text, final_score   

    def evaluate_article(self, article_text):
        system_prompt = (
            "You are a helpful assistant. Evaluate the following Spanish news article "
            "on three dimensions: expat impact, Malaga capital relevance, and political vs. new feature. "
            "Provide scores on a scale of 1 to 10 for each dimension."
            "Use the format: Scores: E:X M:Y P:Z where X is 'expat impact', Y is 'Malaga capital relevance', and Z is 'political vs. new feature' (1 for internal politics, 10 for cool new stuff)."
            "Example: Scores: E:7 M:9 P:4"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": article_text}
        ]
        client =  OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        response = client.chat.completions.create(
            model="qwen3-4b",  
            messages=messages,
            temperature=0.8
        )
        full_response_text = response.choices[0].message.content
        # Remove any <think> tags
        cleaned_response_text = re.sub(r'<think>.*?</think>', '', full_response_text, flags=re.DOTALL).strip()
         # Attempt to parse scores
        scores = {"expat_impact": 0, "malaga_relevance": 0, "feature_vs_politics": 0}
        scores_match = re.search(r"Scores:\s*E:(\d{1,2})\s*M:(\d{1,2})\s*P:(\d{1,2})", cleaned_response_text, re.IGNORECASE)
        
        if scores_match:
            try:
                scores["expat_impact"] = int(scores_match.group(1))
                scores["malaga_relevance"] = int(scores_match.group(2))
                scores["feature_vs_politics"] = int(scores_match.group(3))
            except ValueError:
                print(f"Warning: Could not parse scores from AI response: {scores_match.groups()}")
                # Keep summary_text as cleaned_response_text if scores can't be parsed, so we don't lose the text
        else:
            print(f"Warning: Scores pattern not found in AI response: '{cleaned_response_text}'")
        expat_impact = scores.get("expat_impact") or 0
        malaga_relevance = scores.get("malaga_relevance") or 0
        feature_vs_politics = scores.get("feature_vs_politics") or 0
        final_score = (expat_impact + malaga_relevance + feature_vs_politics) / len(scores)
        return final_score