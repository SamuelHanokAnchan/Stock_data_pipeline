# app.py
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import json
import datetime
from threading import Thread
from kafka import KafkaConsumer
from pymongo import MongoClient
from google.cloud import storage

from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

atlas_client = MongoClient("")#replace with mongoDB atlas cluster key
db = atlas_client['stock_database']
collection = db['stock_prices']

gcs_client = storage.Client.from_service_account_json('')#replace with actual google service key
bucket_name = 'stockdata_backup'
bucket = gcs_client.bucket(bucket_name)

consumer = KafkaConsumer(
    'stock-prices',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def kafka_listener():
    for message in consumer:
        data = message.value
        print("Received message:", data)
        
        try:
            result = collection.insert_one(data)
            print("Data inserted into MongoDB Atlas. Inserted id:", result.inserted_id)
        except Exception as e:
            print("Error inserting into MongoDB Atlas:", e)
        
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
        
        socketio.emit('new_message', data)

thread = Thread(target=kafka_listener)
thread.daemon = True
thread.start()

@app.route('/')
def index():
    initial_data = list(collection.find().sort('_id', -1).limit(20))
    for doc in initial_data:
        doc['_id'] = str(doc['_id'])
    return render_template('index.html', initial_data=initial_data)

@app.route('/predict/<symbol>')
def predict(symbol):
    cursor = collection.find({"symbol": symbol}).sort("timestamp", 1)
    data = list(cursor)
    if len(data) < 5:
        return jsonify({"error": "Not enough data to predict"}), 400
    
    df = pd.DataFrame(data)
    df = df[df["current_price"].notnull()].copy()
    df.reset_index(drop=True, inplace=True)
    if len(df) < 5:
        return jsonify({"error": "Not enough valid data to predict"}), 400

    X = np.array(df.index).reshape(-1, 1)
    y = np.array(df["current_price"])
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_index = np.array(range(len(df), len(df)+10)).reshape(-1, 1)
    predictions = model.predict(future_index)
    
    predictions_train = model.predict(X)
    residuals = y - predictions_train
    risk = float(np.std(residuals))
    
    result = {
        "symbol": symbol,
        "predictions": predictions.tolist(),
        "risk": risk
    }
    return jsonify(result)

if __name__ == '__main__':
    socketio.run(app, debug=True)

