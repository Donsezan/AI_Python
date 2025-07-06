import schedule
import time
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import lmstudio as lms


NEWS_URL = "https://www.malagahoy.es/malaga/"
headers = {"User-Agent": "Mozilla/5.0"}

def fetch_latest_articles():
    try:
        resp = requests.get(NEWS_URL, headers=headers)
        resp.raise_for_status()  # ensure successful response
        soup = BeautifulSoup(resp.text, "html.parser")
        # Example: find all article links in the main list (may need to adjust selector)
        articles = []
        for link in soup.select("a[href*='/malaga/']"):  # find anchors in Málaga section
            href = link.get('href')
            title = link.get_text(strip=True)
            if href and title:
                articles.append((title, href))
        return articles
    except requests.RequestException as e:
        print(f"Error fetching articles: {e}")
        return []


# Configure the OpenAI-compatible client to use local LM Studio server
client =  OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def summarize_with_emojis(article_text):
    system_prompt = (
        "You are a helpful assistant. Summarize the following Spanish news article "
        "in 2-3 sentences in English. End the summary with 1-3 emojis that match the tone of the news."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": article_text}
    ]
    
    response = client.chat.completions.create(
        model="qwen3-4b",  
        messages=messages,
        temperature=0.7
    )
    summary = response.choices[0].message.content
    return summary



BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def post_to_telegram(message_text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message_text}
    try:
        resp = requests.get(url, params=params)
        print(f"Telegram response: {resp.json()}")
    except requests.RequestException as e:
        print(f"Failed to send message: {e}")



def job():
    # Fetch, summarize, and post logic here
    new_articles = fetch_latest_articles()
    for title, href in new_articles:
        if(title == "Málaga"):
            continue
        # Suppose we detect this is new (not seen before)
        resp = requests.get(href, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")


        # Extract the title of the article
        title = soup.find('h1').get_text(strip=True)  # Assuming the title is in an <h1> tag

        # Extract the date of the article
        date = soup.find('time').get_text(strip=True)  # Assuming the date is in a <time> tag

        # Extract the main content of the article
        content = []
        for paragraph in soup.find_all('p'):
            content.append(paragraph.get_text(strip=True))

        # Join the content paragraphs into a single string
        main_content = '\n'.join(content)


        article_text = soup.find("div", {"class": "article-text"}).get_text()
        summary = summarize_with_emojis(article_text)
        post_to_telegram(f"{title}\n\n{summary}")

job()  # Run once immediately
schedule.every(10).minutes.do(job)
while True:
    schedule.run_pending()
    time.sleep(1)
