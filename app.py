import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

TWELVE_DATA_KEY = os.getenv("TWELVE_DATA_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

@app.route('/')
def home():
    return "Gold Terminal Pro: Engine Online"

@app.route('/signal')
def get_analysis():
    try:
        # 1. FIXED PRICE FETCH (Using 'price' endpoint for speed)
        price_url = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={TWELVE_DATA_KEY}"
        p_res = requests.get(price_url).json()
        current_price = p_res.get('price', 'N/A')

        # 2. TARGETED NEWS (Focusing strictly on Gold & Central Banks)
        news_url = f"https://newsapi.org/v2/everything?q=%22gold+price%22+OR+%22XAU%22+OR+%22federal+reserve%22&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
        n_res = requests.get(news_url).json()
        articles = n_res.get('articles', [])
        
        headlines = [a['title'] for a in articles[:3]]
        
        # 3. ADVANCED SENTIMENT
        bullish_words = ["inflation", "crisis", "war", "cut", "weak", "buy", "demand"]
        full_text = " ".join(headlines).lower()
        
        sentiment = "NEUTRAL"
        if any(word in full_text for word in bullish_words):
            sentiment = "BULLISH (Potential Upside)"
        elif "hike" in full_text or "stronger dollar" in full_text:
            sentiment = "BEARISH (Potential Downside)"

        return jsonify({
            "market": "XAU/USD (Gold)",
            "price": f"${float(current_price):,.2f}" if current_price != 'N/A' else "Market Closed/API Error",
            "news_sentiment": sentiment,
            "top_headlines": headlines if headlines else ["No high-impact news in last hour"],
            "recommendation": "Strong Buy" if sentiment == "BULLISH (Potential Upside)" else "Wait for Setup"
        })

    except Exception as e:
        return jsonify({"error": "Calibration error", "msg": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
