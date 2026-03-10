import os
import requests
import pandas as pd
import pandas_ta as ta
from flask import Flask, jsonify

app = Flask(__name__)

TWELVE_DATA_KEY = os.getenv("TWELVE_DATA_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_technical_analysis():
    # Fetching historical data for trend analysis
    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=1h&outputsize=50&apikey={TWELVE_DATA_KEY}"
    data = requests.get(url).json()
    
    if "values" not in data:
        return None

    df = pd.DataFrame(data["values"])
    df["close"] = pd.to_numeric(df["close"])
    df = df.iloc[::-1] # Reverse to chronological order

    # Indicators
    rsi = df.ta.rsi(length=14).iloc[-1]
    sma_20 = df.ta.sma(length=20).iloc[-1]
    current_price = df["close"].iloc[-1]
    
    # Simple Support/Resistance Logic
    support = df["close"].min()
    resistance = df["close"].max()

    # Trend Decision
    trend = "BULLISH" if current_price > sma_20 else "BEARISH"
    
    # Recommendation Logic
    reason = "Price is above 20MA with healthy RSI."
    if rsi > 70:
        signal = "SELL / TAKE PROFIT"
        reason = "Gold is Overbought (RSI > 70). High risk of drop."
    elif rsi < 30:
        signal = "STRONG BUY"
        reason = "Gold is Oversold (RSI < 30). Bounce expected."
    else:
        signal = "BUY" if trend == "BULLISH" else "SELL"
        reason = f"Following {trend} trend on 1H timeframe."

    return {
        "trend": trend,
        "rsi": round(rsi, 2),
        "support": f"${support:,.2f}",
        "resistance": f"${resistance:,.2f}",
        "signal": signal,
        "reasoning": reason
    }

@app.route('/signal')
def get_full_analysis():
    try:
        # Get Live Price
        p_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={TWELVE_DATA_KEY}").json()
        price = p_res.get('price', 'N/A')

        # Get Technicals
        ta_data = get_technical_analysis()

        return jsonify({
            "status": "LIVE",
            "price": f"${float(price):,.2f}",
            "analysis": ta_data,
            "instruction": f"ENTRY: {ta_data['signal']} | TP: {ta_data['resistance']} | SL: {ta_data['support']}"
        })
    except Exception as e:
        return jsonify({"error": "Analyzing Markets...", "details": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
