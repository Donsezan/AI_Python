import re
import json

def parse_summary_with_emojis(response_text):
    """
    Cleans the summary text by removing any <think> tags.
    """
    return re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL).strip()

def parse_summary_with_emojis_and_evaluate(response_text):
    """
    Parses the response for a summary with evaluation, extracting the summary text and scores.
    """
    cleaned_response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL).strip()

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

def parse_evaluate_article(response_text):
    """
    Parses the JSON response from the article evaluation, calculating a total score.
    """
    cleaned_response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL).strip()
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
