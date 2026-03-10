import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Fetching Keys from Render Environment
TWELVE_DATA_KEY = os.getenv("TWELVE_DATA_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

@app.route('/')
def home():
    return "Gold Terminal Pro: Engine Online"

@app.route('/signal')
def get_analysis():
    try:
        # 1. GET REAL-TIME PRICE DATA
        price_url = f"https://api.twelvedata.com/quote?symbol=XAU/USD&apikey={TWELVE_DATA_KEY}"
        p_res = requests.get(price_url).json()
        current_price = p_res.get('price', 'N/A')
        day_change = p_res.get('percent_change', '0')

        # 2. GET LIVE NEWS ANALYSIS
        news_url = f"https://newsapi.org/v2/everything?q=gold+market+XAU&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
        n_res = requests.get(news_url).json()
        articles = n_res.get('articles', [])
        
        # Pull the top 3 headlines
        headlines = [a['title'] for a in articles[:3]]
        
        # 3. SENTIMENT LOGIC (The "Brain")
        # Keywords that usually move Gold up
        bullish_words = ["inflation", "crisis", "war", "fed pivot", "rate cut", "weak dollar"]
        sentiment_score = "NEUTRAL"
        full_text = " ".join(headlines).lower()
        
        if any(word in full_text for word in bullish_words):
            sentiment_score = "BULLISH (News favoring Gold)"
        elif "rate hike" in full_text or "strong dollar" in full_text:
            sentiment_score = "BEARISH (Pressure on Gold)"

        return jsonify({
            "market": "XAU/USD (Gold)",
            "price": f"${current_price}",
            "change": f"{day_change}%",
            "news_sentiment": sentiment_score,
            "top_headlines": headlines,
            "recommendation": "Strong Buy" if "BULLISH" in sentiment_score else "Monitor Closely"
        })

    except Exception as e:
        return jsonify({"error": "System Calibration in Progress", "details": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
