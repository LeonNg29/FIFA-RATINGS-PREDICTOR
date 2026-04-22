# FIFA Player Rating Predictor

A machine learning system that predicts FIFA 23 player overall ratings from player attributes, served via a production-grade infrastructure stack.

## Architecture

User → Flask API → Redis Cache → ML Model (Random Forest)
↓
Prometheus (metrics scraping)
↓
Grafana (dashboard visualisation)

## Tech Stack

- **Machine Learning**: scikit-learn Random Forest Regressor trained on 148,000+ FIFA 23 players
- **Backend**: Python Flask REST API
- **Caching**: Redis (cache hit/miss on repeated predictions)
- **Containerisation**: Docker + Docker Compose
- **Observability**: Prometheus metrics + Grafana dashboard
- **CI/CD**: GitHub Actions (dependency install, smoke test, Docker image build)

## Model Performance

- **Mean Absolute Error**: 0.09 rating points
- **R² Score**: 0.9979
- **Training data**: 148,068 FIFA 23 players
- **Features**: Pace, Shooting, Passing, Dribbling, Defending, Physicality

## Running Locally

**Prerequisites**: Docker, Docker Compose

1. Clone the repository
```bash
git clone https://github.com/LeonNg29/FIFA-RATINGS-PREDICTOR.git
cd FIFA-RATINGS-PREDICTOR
```

2. Add the model file (not included in repo due to size)
Place fifa_model.pkl in the project root

3. Start all services
```bash
docker compose up --build
```

4. Access the services
- **FIFA Predictor**: http://localhost:5001
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## API

**POST /predict**

Request:
```json
{
  "pace": 85,
  "shooting": 91,
  "passing": 91,
  "dribbling": 95,
  "defending": 34,
  "physic": 64
}
```

Response:
```json
{
  "rating": 91.0,
  "source": "model"
}
```

`source` will be `"cache"` if the result was served from Redis.

## Observability

Metrics exposed at `/metrics` and scraped by Prometheus every 5 seconds:

- `http_requests_total` — total prediction requests
- `cache_hits_total` — requests served from Redis cache
- `cache_misses_total` — requests that ran the ML model

Grafana dashboard visualises these metrics in real time.

## CI/CD

GitHub Actions pipeline triggers on every push to `main`:

1. Install dependencies
2. Smoke test — verify all imports succeed
3. Build Docker image