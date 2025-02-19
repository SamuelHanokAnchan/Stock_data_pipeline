import json
import datetime
from kafka import KafkaConsumer
from pymongo import MongoClient
from google.cloud import storage

consumer = KafkaConsumer(
    'stock-prices',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

atlas_client = MongoClient("mongodb+srv://Francis:Bfe04@cluster0.0na1f.mongodb.net")
db = atlas_client['stock_database']      
collection = db['stock_prices']          

gcs_client = storage.Client.from_service_account_json('srh-project-bdd-2061d9042f25.json')
bucket_name = 'stockdata_backup'     
bucket = gcs_client.bucket(bucket_name)

print("Consumer is listening for messages...")

for message in consumer:
    data = message.value
    print("Received message:", data)

    # ----- Store in MongoDB Atlas -----
    try:
        result = collection.insert_one(data)
        print("Data inserted into MongoDB Atlas. Inserted id:", result.inserted_id)
    except Exception as e:
        print("Error inserting into MongoDB Atlas:", e)

    # ----- Backup to Google Cloud Storage -----
    try:
        
        backup_data = data.copy()
        backup_data.pop('_id', None)
        
        timestamp = datetime.datetime.utcnow().isoformat()
        blob_name = f'stock_backup/{timestamp}.json'
        blob = bucket.blob(blob_name)
        
        blob.upload_from_string(json.dumps(backup_data), content_type='application/json')
        print("Data backed up to GCS with blob name:", blob_name)
    except Exception as e:
        print("Error uploading to GCS:", e)
