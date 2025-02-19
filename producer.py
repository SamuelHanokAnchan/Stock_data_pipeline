import time
import json
import yfinance as yf
from kafka import KafkaProducer
from datetime import datetime

TOP_STOCKS = ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA", "META", "NVDA", "JPM", "V", "WMT"]

KAFKA_TOPIC = "stock-prices"

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

def fetch_stock_data(symbol):
    
    try:
        stock = yf.Ticker(symbol)
        
        intraday_data = stock.history(period="1d", interval="1m")
        if not intraday_data.empty:
            latest_record = intraday_data.iloc[-1]
            latest_timestamp = intraday_data.index[-1].strftime('%Y-%m-%d %H:%M:%S')
            current_price = float(latest_record["Close"])
        else:
            latest_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            current_price = None
        
        daily_data = stock.history(period="3d", interval="1d")
        historical_prices = {}
        today_str = datetime.now().strftime('%Y-%m-%d')
        for date, row in zip(daily_data.index.strftime('%Y-%m-%d').tolist(), daily_data.itertuples()):# type: ignore
            if date != today_str:
                historical_prices[date] = float(getattr(row, "Close", row.Close)) # type: ignore
        
        sorted_dates = sorted(historical_prices.keys())
        if len(sorted_dates) > 2:
            selected_dates = sorted_dates[-2:]
            historical_prices = {date: historical_prices[date] for date in selected_dates}
        
        message = {
            "symbol": symbol,
            "timestamp": latest_timestamp,
            "current_price": current_price,
            "historical_prices": historical_prices
        }
        return message
    except Exception as e:
        print(f"Error fetching stock data for {symbol}: {e}")
        return None

if __name__ == "__main__":
    while True:
        for symbol in TOP_STOCKS:
            stock_data = fetch_stock_data(symbol)
            if stock_data:
                try:
                    producer.send(KAFKA_TOPIC, stock_data)
                    print(f"Sent to Kafka: {stock_data}\n")
                except Exception as e:
                    print(f"Error sending data to Kafka for {symbol}: {e}")
        time.sleep(60)
