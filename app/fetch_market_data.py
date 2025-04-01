import yfinance as yf
import psycopg2
from config import DATABASE_URL
import time

def get_latest_price(symbol):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d", interval="1m")
    if data.empty:
        print(f"[WARN] No data found for {symbol}")
        return None, None
    latest_row = data.iloc[-1]
    timestamp = latest_row.name.to_pydatetime().replace(tzinfo=None)  # 确保是 datetime 类型
    close_price = float(latest_row['Close'])  # 确保是 float 类型
    return timestamp, close_price


def save_to_db(symbol, price, timestamp):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO market_data (symbol, current_price, timestamp)
        VALUES (%s, %s, %s)
        ON CONFLICT (symbol, timestamp) DO NOTHING;
    """, (symbol, price, timestamp))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[OK] {symbol} @ {timestamp} = ${price:.2f}")


def get_unique_symbols_from_positions():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT symbol FROM positions;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]


if __name__ == "__main__":
    while True:
        symbols = get_unique_symbols_from_positions()
        print(f"[INFO] Fetching {len(symbols)} symbols...")
        for symbol in symbols:
            ts, price = get_latest_price(symbol)
            if ts and price:
                save_to_db(symbol, price, ts)
        print("[INFO] Sleeping 60 seconds...\n")
        time.sleep(60)
