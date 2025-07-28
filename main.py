from dotenv import load_dotenv
import schedule
import time
import os
from datetime import datetime

from fetching_data import FetchingData
from ai_service import AIService
from telegram_service import TelegramService
from data_service import DataService
from ai_provider import AIProvider

# Configuration
load_dotenv()
HEADERS = {"User-Agent": "Mozilla/5.0"}
CHROMA_DB_PATH = "./chroma_db_persistence"
SIMILARITY_THRESHOLD = 0.85
DISTANCE_THRESHOLD = 1 - SIMILARITY_THRESHOLD
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
NEWS_URL = os.getenv('NEWS_URL')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Toggle between AI providers: AIProvider.OPENAI or AIProvider.GEMINI
current_ai_provider = AIProvider.GEMINI

# Initialize services
data_service = DataService(chroma_db_path=CHROMA_DB_PATH, DISTANCE_THRESHOLD=DISTANCE_THRESHOLD)
fetch_serice = FetchingData(NEWS_URL, HEADERS)
telegram_service = TelegramService(BOT_TOKEN, CHAT_ID)
ai_service = AIService(provider=current_ai_provider, gemini_api_key=GEMINI_API_KEY)

def job():
    """
    This function fetches new articles, evaluates them, and posts them to Telegram if they meet the criteria.
    """
    print("Fetching latest articles...")
    new_articles = fetch_serice.fetch_latest_articles()
    print(f"Found {len(new_articles)} new articles.")
    for title, href in new_articles:
        print(f"Processing article: {title}")
        if not data_service.is_new_article(title):
            print(f"Article '{title}' already processed, skipping.")
            continue

        print("Fetching and summarizing article...")
        result = fetch_serice.fetch_and_summarize(title, href)
        if not result:
            print("Failed to fetch and summarize article.")
            continue

        main_content, images, date_time = result
        if not main_content or not date_time:
            print("Article content or date/time is missing.")
            continue

        print("Saving article...")
        data_service.save_article(title, date_time)

        print("Evaluating article...")
        article_score = ai_service.evaluate_article(title)
        if not article_score:
            print(f"Failed to evaluate article '{title}'. Skipping.")
            continue

        print(f"Article score: {article_score}")
        if article_score < 6:
            print(f"Article '{title}' with score '{article_score}' does not meet the evaluation criteria. Skipping.")
            continue

        print("Summarizing with emojis...")
        evaluated_content = ai_service.summarize_with_emojis(main_content, target_language='en')

        print("Posting to Telegram...")
        result_of_post = telegram_service.post_to_telegram(f"<b>{title}</b>\n\n{evaluated_content}", images, href)
        if not result_of_post:
            print(f"Failed to post article '{title}' to Telegram.")
            continue
    print("Job finished.")

def dry_run():
    """
    This function is for testing purposes. It fetches and evaluates articles without posting to Telegram.
    """
    new_articles = fetch_serice.fetch_latest_articles()
    for title, href in new_articles:
        print(f"Title: {title}, Link: {href}")

        result = fetch_serice.fetch_and_summarize(title, href)
        if not result:
            continue

        main_content, images, date_time = result
        if not main_content or not date_time:
            continue

        article_score = ai_service.evaluate_article(title)
        if not article_score:
            print(f"Failed to evaluate article '{title}'. Skipping.")
            continue

        if article_score < 5:
            print(f"Article '{title}' with score '{article_score}' does not meet the evaluation criteria. Skipping.")
            continue

        evaluated_content = ai_service.summarize_with_emojis(main_content, target_language='en')
        print(f"Evaluated Content: {evaluated_content}")

# Main execution
if __name__ == "__main__":
    # dry_run()  # Uncomment to test without posting
    job()  # Run once immediately

    # Schedule regular jobs
    # schedule.every(10).minutes.do(job)
    # schedule.every().day.at("00:00").do(data_service.cleanup_old_articles, max_age_days=10)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    #     print(f"All done for {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")