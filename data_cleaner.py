# data_cleaner.py
import time
from pymongo import MongoClient

def clean_data():
    # Replace <your_atlas_connection_string> with your actual MongoDB Atlas connection string.
    client = MongoClient("")#replace with the actual mongoDB connection string
    db = client["stock_database"]
    collection = db["stock_prices"]

    # Define a query to remove documents where any key is null.
    query = {
        "$or": [
            {"current_price": None},
            {"symbol": None},
            {"timestamp": None}
        ]
    }
    result = collection.delete_many(query)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Cleaned {result.deleted_count} documents with null values.")

if __name__ == "__main__":
    while True:
        clean_data()
        time.sleep(300)  # Sleep for 5 minutes (300 seconds)
