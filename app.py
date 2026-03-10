import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Gold Terminal Pro: Backend System Online"

@app.route('/signal')
def signal():
    # We will add the high-level news/market logic here next
    return jsonify({"message": "System Ready. Waiting for API Keys."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
