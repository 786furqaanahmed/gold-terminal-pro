import os
import requests
import pandas as pd
import pandas_ta as ta
from flask import Flask, jsonify

app = Flask(__name__)

TWELVE_DATA_KEY = os.getenv("TWELVE_DATA_KEY")

@app.route('/')
def home():
    return "Gold Terminal Pro: Logic Online"

@app.route('/signal')
def get_analysis():
    try:
        # 1. Fetch Price & History
        url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=1h&outputsize=50&apikey={TWELVE_DATA_KEY}"
        res = requests.get(url).json()
        
        if "values" not in res:
            return jsonify({"status": "Waiting for Data", "msg": "Twelve Data is still syncing."})

        # 2. Convert to DataFrame for Analysis
        df = pd.DataFrame(res["values"])
        df["close"] = pd.to_numeric(df["close"])
        df = df.iloc[::-1] # Newest at the bottom

        # 3. Technical Analysis (TA)
        rsi = df.ta.rsi(length=14).iloc[-1]
        sma_20 = df.ta.sma(length=20).iloc[-1]
        current_price = df["close"].iloc[-1]
        
        # Support/Resistance Zones
        support = df["close"].min()
        resistance = df["close"].max()

        # Logic Brain
        if rsi > 70:
            signal, reason = "SELL", "Overbought (RSI > 70)"
        elif rsi < 30:
            signal, reason = "BUY", "Oversold (RSI < 30)"
        else:
            signal = "BUY" if current_price > sma_20 else "SELL"
            reason = "Trending with Moving Average"

        return jsonify({
            "price": f"${current_price:,.2f}",
            "trend": "UP" if current_price > sma_20 else "DOWN",
            "rsi": round(rsi, 2),
            "zones": {"support": f"${support:,.2f}", "resistance": f"${resistance:,.2f}"},
            "recommendation": signal,
            "logic": reason
        })

    except Exception as e:
        return jsonify({"error": "System Rebooting", "details": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
