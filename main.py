from dotenv import load_dotenv
import schedule
import time
import os
from datetime import datetime

from fetching_data import FetchingData
from ai_service import AIService
from telegram_service import TelegramService
from data_service import DataService

HEADERS = {"User-Agent": "Mozilla/5.0"}
CHROMA_DB_PATH = "./chroma_db_persistence"
SIMILARITY_THRESHOLD = 0.85  
DISTANCE_THRESHOLD = 1 - SIMILARITY_THRESHOLD  

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
NEWS_URL = os.getenv('NEWS_URL')
data_service = DataService(chroma_db_path=CHROMA_DB_PATH, DISTANCE_THRESHOLD=DISTANCE_THRESHOLD)
fetch_serice = FetchingData(NEWS_URL, HEADERS)
telegram_service = TelegramService(BOT_TOKEN, CHAT_ID)
ai_service = AIService()

def job():
    load_dotenv()
    # Fetch, summarize, and post logic here
    new_articles = fetch_serice.fetch_latest_articles()
    for title, href in new_articles:
        # 1. Check if the article is new
        if not data_service.is_new_article(title):
            print(f"Article '{title}' already processed, skipping.")
            continue
        # 3. Fetch the article content and images  
        result = fetch_serice.fetch_and_summarize(title, href)
        if not result:
            continue
        main_content, images, date_time = result
        if not main_content or not date_time:
            continue
        # save
        data_service.save_article(title, date_time)
       
        article_score = ai_service.evaluate_article(title)
        if not article_score:
            print(f"Failed to evaluate article '{title}'. Skipping.")
            continue
        if article_score < 6:
            print(f"Article '{title}' with score '{article_score}' does not meet the evaluation criteria. Skipping.")
            continue

        # 3.1 Evaluate post (should we post it or not)   
        evaluated_content = ai_service.summarize_with_emojis(main_content, target_language='en')
       
        result_of_post = telegram_service.post_to_telegram(f"<b>{title}</b>\n\n{evaluated_content}", images, href)
        if not result_of_post:
            print(f"Failed to post article '{title}' to Telegram.")
            continue


# Main execution
job()  # Run once immediately

schedule.every(10).minutes.do(job)
schedule.every().day.at("00:00").do(data_service.cleanup_old_articles, max_age_days=10)  
while True:
    schedule.run_pending()
    time.sleep(1)  
    print(f"All done for {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")