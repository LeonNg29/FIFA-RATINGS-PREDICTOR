from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd
import redis
import json
from prometheus_client import Counter, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

# Load model once when server starts
with open('fifa_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Connect to Redis
cache = redis.Redis(host='redis', port=6379)

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
CACHE_HIT = Counter('cache_hits_total', 'Total cache hits')
CACHE_MISS = Counter('cache_misses_total', 'Total cache misses')

# Mount metrics endpoint
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    REQUEST_COUNT.inc()
    data = request.json

    cache_key = f"predict:{data['pace']}:{data['shooting']}:{data['passing']}:{data['dribbling']}:{data['defending']}:{data['physic']}"

    cached = cache.get(cache_key)
    if cached:
        print("Cache HIT")
        CACHE_HIT.inc()
        return jsonify({'rating': json.loads(cached), 'source': 'cache'})

    print("Cache MISS")
    CACHE_MISS.inc()

    player = pd.DataFrame([[
        data['pace'],
        data['shooting'],
        data['passing'],
        data['dribbling'],
        data['defending'],
        data['physic']
    ]], columns=['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic'])

    prediction = model.predict(player)
    rating = round(float(prediction[0]), 1)

    cache.set(cache_key, json.dumps(rating), ex=3600)

    return jsonify({'rating': rating, 'source': 'model'})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)