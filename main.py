from bs4 import BeautifulSoup
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
import schedule
import time
import requests
import re
import os
import chromadb
from chromadb.config import Settings
import uuid
from datetime import timedelta

HEADERS = {"User-Agent": "Mozilla/5.0"}
CHROMA_DB_PATH = "./chroma_db_persistence"
SIMILARITY_THRESHOLD = 0.85  
DISTANCE_THRESHOLD = 1 - SIMILARITY_THRESHOLD  

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
NEWS_URL = os.getenv('NEWS_URL')

client = chromadb.PersistentClient(path=CHROMA_DB_PATH, settings=Settings())
collection = client.get_or_create_collection(name="malaga_news")

def fetch_latest_articles():
    try:
        resp = requests.get(NEWS_URL, headers=HEADERS)
        resp.raise_for_status()  # ensure successful response
        soup = BeautifulSoup(resp.text, "html.parser")
        # Example: find all article links in the main list (may need to adjust selector)
        articles = []
        for link in soup.select("a[href*='/malaga/']"):  # find anchors in Málaga section
            href = link.get('href')
            title = link.get_text(strip=True)
            if href and title:
                articles.append((title, href))
        articles.reverse()  # Reverse to get the latest articles first
        return articles
    except requests.RequestException as e:
        print(f"Error fetching articles: {e}")
        return []

def is_new_article(title):
    try:
        results = collection.query(query_texts=[title], n_results=1)
        distances = results.get('distances', [])
        if not distances or not distances[0]:
            return True
        distance = distances[0][0]
        if distance <= DISTANCE_THRESHOLD:
            return False
        return True
    except Exception as e:
        print(f"Error checking for new article: {e}")
        return True

def summarize_with_emojis(article_text):
    system_prompt = (
        "You are a helpful assistant. Summarize the following Spanish news article "
        "in 2-3 sentences in English with a slightly sarcastic style. End the summary with 1-3 emojis that match the tone of the news."
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

def post_to_telegram(message_text, images, href):
    message_text = message_text + f"\n\n{href}"
    if images:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup"
        mediaGroup = [
            {'type': 'photo',
            'media': images[0],
            'caption': message_text,
            'parse_mode': 'HTML'}
        ]
        if len(images) > 1:
            for image in images[1:9]:
                mediaGroup.append({'type': 'photo', 'media': image})
        payload = {
            "chat_id": CHAT_ID,
            "media": mediaGroup
        }
        resp = requests.post(url, json=payload)
        print(f"Telegram response: {resp.json()}")
        return True
    else:
        # If no images, send as a text message
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": message_text}

        resp = requests.get(url, params=params)
        print(f"Telegram response: {resp.json()}")
        print(f"Failed to send message: {e}")
        return False

def fetch_and_summarize(title, href):
    if(title == "Málaga"):
            return
        # Suppose we detect this is new (not seen before)
    resp = requests.get(href, headers=HEADERS)

    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract the title of the article
    title = soup.find('h1').get_text(strip=True)  # Assuming the title is in an <h1> tag
    # Extract the date of the article
    date_time_obj =  soup.find('p', class_='timestamp-atom') # Assuming the title is in an <h1> tag    
    # Convert to datetime object

    month_mapping = {
    'enero': '01',
    'febrero': '02',
    'marzo': '03',
    'abril': '04',
    'mayo': '05',
    'junio': '06',
    'julio': '07',
    'agosto': '08',
    'septiembre': '09',
    'octubre': '10',
    'noviembre': '11',
    'diciembre': '12'
}
    date_string = date_time_obj.text.strip().split('\n')[0]
    # Replace the Spanish month name with its corresponding number
    for month_name, month_number in month_mapping.items():
        if month_name in date_string:
            date_string = date_string.replace(month_name, month_number)
            break  # Exit the loop once the month is found and replaced

    date_time = datetime.strptime(date_string, '%d de %m %Y - %H:%M')
    # Extract the main content of the article
    content = []
    for paragraph in soup.find_all('p'):
        content.append(paragraph.get_text(strip=True))

    # Extract image URLs from <source> tags
    main_colleft= soup.find('main', id ='content-body')
    source_images = [
        source['srcset'] for source in main_colleft.find_all('source')
        if not source.find_parent(class_='media-atom') 
        ]

    # Extract image URL from <img> tag
    img_tag = soup.find('img')
    img_url = img_tag['src'] if img_tag else None

    # Combine all image URLs
    all_images = source_images + [img_url] if img_url else source_images

    max_resolution = 0

    for url in all_images:
        match = re.search(r'_(\d+)w_', url) # type: ignore
        if match:
            resolution = int(match.group(1))
            if resolution > max_resolution:
                max_resolution = resolution

    # Step 2: Filter URLs with the maximum resolution and .jpg extension
    unique_urls = set(all_images) 
    filtered_urls = [url for url in unique_urls if url.endswith('.jpg') and f'_{max_resolution}w_' in url] # type: ignore
    # Join the content paragraphs into a single string
    return '\n'.join(content), filtered_urls, date_time

def job():
    load_dotenv()
    # Fetch, summarize, and post logic here
    new_articles = fetch_latest_articles()
    for title, href in new_articles:
        result = fetch_and_summarize(title, href)
        if not result:
            continue
        main_content, images, date_time = result
        if not main_content or not date_time:
            continue
        if not is_new_article(title):
            print(f"Article '{title}' already processed, skipping.")
            continue
        summary = summarize_with_emojis(main_content)
        result_of_post = post_to_telegram(f"<b>{title}</b>\n\n{summary}", images, href)
        if not result_of_post:
            print(f"Failed to post article '{title}' to Telegram.")
            continue
        try: 
            doc_id = str(uuid.uuid4())
            collection.add(
                ids=[doc_id],
                documents=[title],
                metadatas=[{"date": date_time.isoformat()}]
            )
            print(f"Article '{title}' added to the database with ID {doc_id}.")
        except Exception as e:
            print(f"Error adding article '{title}' to the database: {e}")
    print(f"All done for {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def cleanup_old_articles(max_age_days=10):
    try:
        results = collection.get(include=["metadatas", "ids"])
        if not results or "metadatas" not in results or "ids" not in results:
            print("No articles found in the database.")
            return
        ids_to_delete = []
        now = datetime.now()
        cutoff = now - timedelta(days=max_age_days)
        for doc_id, metadata in zip(results['ids'], results['metadatas']):
            timestamp_str = metadata.get("date")
            if not timestamp_str:
                continue
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp < cutoff:
                    ids_to_delete.append(doc_id)
            except ValueError:
                continue
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            client.persist()
            print(f"Deleted {len(ids_to_delete)} old articles from the database.")
        else:
            print("No old articles to delete.")
    except Exception as e:
        print(f"Error cleaning up old articles: {e}")

job()  # Run once immediately
schedule.every(10).minutes.do(job)
schedule.every().day.at("00:00").do(cleanup_old_articles, max_age_days=10)  
while True:
    schedule.run_pending()
    time.sleep(1)
