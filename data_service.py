import chromadb
from chromadb.config import Settings
import uuid
from datetime import datetime, timedelta


class DataService:
    def __init__(self, chroma_db_path, DISTANCE_THRESHOLD):
        self.distance_threshold = DISTANCE_THRESHOLD
        self.client = chromadb.PersistentClient(path=chroma_db_path, settings=Settings())
        self.collection = self.client.get_or_create_collection(name="malaga_news")


    def is_new_article(self, title):
        try:
            results = self.collection.query(query_texts=[title], n_results=1)
            distances = results.get('distances', [])
            if not distances or not distances[0]:
                return True
            distance = distances[0][0]
            if distance <= self.distance_threshold:
                return False
            return True
        except Exception as e:
            print(f"Error checking for new article: {e}")
            return True

    def save_article(self, title, date_time):
        try: 
            doc_id = str(uuid.uuid4())
            self.collection.add(
                ids=[doc_id],
                documents=[title],
                metadatas=[{"date": date_time.isoformat()}]
                )
            print(f"Article '{title}' added to the database with ID {doc_id}.")
        except Exception as e:
            print(f"Error adding article '{title}' to the database: {e}")

    
    def cleanup_old_articles(self, max_age_days=10):
        try:
            results = self.collection.get(include=["metadatas", "ids"])
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
                self.collection.delete(ids=ids_to_delete)
                self.client.persist()
                print(f"Deleted {len(ids_to_delete)} old articles from the database.")
            else:
                print("No old articles to delete.")
        except Exception as e:
            print(f"Error cleaning up old articles: {e}")
