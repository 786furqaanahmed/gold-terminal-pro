import os
import requests
import pandas as pd
import pandas_ta as ta
from flask import Flask, jsonify
from smartmoneyconcepts import smc

app = Flask(__name__)

TWELVE_DATA_KEY = os.getenv("TWELVE_DATA_KEY")

@app.route('/')
def home():
    return "Gold Terminal Pro: SMC Engine Active"

@app.route('/signal')
def get_smc_signal():
    try:
        # 1. Fetch High-Quality 1H Data
        url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=1h&outputsize=100&apikey={TWELVE_DATA_KEY}"
        res = requests.get(url).json()
        
        if "values" not in res:
            return jsonify({"status": "Error", "message": "API Limit or Key Issue"})

        # 2. Format Data for Smart Money Logic
        df = pd.DataFrame(res["values"])
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].apply(pd.to_numeric)
        df = df.iloc[::-1].reset_index(drop=True)

        # 3. Detect Break of Structure (BoS) & Order Blocks (OB)
        # We look for swing points to identify BoS
        swing_hl = smc.swing_highs_lows(df, swing_length=5)
        bos_data = smc.bos_choch(df, swing_hl)
        
        current_price = df["close"].iloc[-1]
        last_bos = bos_data.iloc[-1]
        
        # 4. Identify Zones (Supply/Demand Boxes)
        demand_zone = df["low"].tail(20).min()
        supply_zone = df["high"].tail(20).max()

        # 5. Trading Logic
        signal = "NEUTRAL"
        reasoning = "Price consolidating between major zones."
        
        if last_bos['BOS'] == 1:
            signal = "STRONG BUY"
            reasoning = f"Bullish BoS detected at ${last_bos['Level']:.2f}. Trend is UP."
        elif last_bos['BOS'] == -1:
            signal = "STRONG SELL"
            reasoning = f"Bearish BoS detected at ${last_bos['Level']:.2f}. Trend is DOWN."
        elif current_price <= demand_zone * 1.002:
            signal = "BUY"
            reasoning = "Price rejected Demand Zone. Looking for reversal."

        return jsonify({
            "live_price": f"${current_price:,.2f}",
            "market_structure": "BULLISH" if last_bos['BOS'] == 1 else "BEARISH",
            "signal": signal,
            "why": reasoning,
            "zones": {
                "buy_zone_demand": f"${demand_zone:,.2f}",
                "sell_zone_supply": f"${supply_zone:,.2f}"
            },
            "targets": {
                "TP": f"${supply_zone:,.2f}",
                "SL": f"${(demand_zone * 0.995):,.2f}"
            }
        })

    except Exception as e:
        return jsonify({"status": "Recalibrating", "error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
