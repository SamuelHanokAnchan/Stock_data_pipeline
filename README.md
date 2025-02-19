# Real-Time Stock Data Pipeline

## Overview
This project is a real-time stock data processing pipeline that integrates Kafka, GCP, MongoDB, and Machine Learning to ingest, store, clean, and analyze stock price data. The system predicts future stock trends using Linear Regression and assesses risk via ARIMA models. A Flask-based web application visualizes everything interactively.

## Features
- Live stock data ingestion from Yahoo Finance API
- Kafka Producer-Consumer model for streaming data processing
- MongoDB Atlas for structured data storage
- Google Cloud Storage (GCS) S3 bucket as a backup
- Automated data cleaning every 5 minutes
- Stock price prediction using Linear Regression
- Risk analysis with ARIMA models
- Flask-based web dashboard for visualization
- Dockerized and orchestrated with Docker Compose

## Architecture
1. **Data Ingestion**: Fetch live stock prices using `yfinance` and push to Kafka.
2. **Storage**: Store data in MongoDB Atlas and back up in GCP S3 bucket.
3. **Data Cleaning**: Runs every 5 minutes to remove inconsistencies.
4. **Machine Learning**: Applies Linear Regression and ARIMA models.
5. **Web Application**: Flask-based dashboard to visualize trends and predictions.
6. **Containerization**: Uses Docker and Docker Compose for deployment.

## Installation & Setup
1. **Clone the Repository**
   ```bash
   git clone https://github.com/SamuelHanokAnchan/Stock_data_pipeline.git
   cd Stock_data_pipeline
   ```
2. **Set Up Kafka**
   - Ensure you have Apache Kafka installed and running.
3. **Run the Containers**
   ```bash
   docker-compose up --build
   ```
4. **Access the Web Application**
   - Open `http://localhost:5000` in your browser.

## Security Notice
The JSON key file for GCP has been deleted from the repository for security reasons. To use GCP storage, generate a new key from your GCP console and place it in the appropriate directory.

## Future Enhancements
- Upgrade machine learning models (LSTM, Transformers for better accuracy)
- Migrate to a serverless architecture (AWS Lambda or GCP Functions)
- Enable real-time alerts and notifications (WebSockets, push notifications)
- Scale with Spark Streaming for high-volume processing

## Contribution
Feel free to open issues, create pull requests, and suggest improvements.

**GitHub Repository:** [Stock Data Pipeline](https://github.com/SamuelHanokAnchan/Stock_data_pipeline/)

