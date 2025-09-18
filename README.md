# URL Shortener

This repository implements a simple URL shortener with observability (Prometheus + Grafana) and an Nginx reverse-proxy. It contains:

- API (Node.js / Express / MongoDB) — [server/server.js](server/server.js)  
  
- Frontend (Flask) — [client/app.py](client/app.py)  
  
- Reverse proxy (Nginx) — [nginx/default.conf](nginx/default.conf), [nginx/nginx.conf](nginx/nginx.conf), [nginx/Dockerfile](nginx/Dockerfile) and TLS certs in [nginx/certs/](nginx/certs/)
- Observability
  - Prometheus config: [prometheus/prometheus.yml](prometheus/prometheus.yml)
  - Grafana config: [grafana/grafana.ini](grafana/grafana.ini)
- Orchestration: [docker-compose.yaml](docker-compose.yaml)
- CI: GitHub Actions workflow: [.github/workflows/test.yml](.github/workflows/test.yml) and local pre-push hook: [pre-push](pre-push)

---

## High-level architecture

- The API exposes endpoints to create short URLs (POST /url) and to fetch redirect & analytics (GET /:shortId, GET /analytics/:shortId). See [server/server.js](server/server.js) and [`handleGenerateNewShortURL`](server/controllers/url.js).
- The Flask client renders the UI and calls the API to create short URLs and to retrieve analytics. See [client/app.py](client/app.py).
- Nginx serves as the public entrypoint (ports 80 and 443) and proxies:
  - / -> Flask client
  - /prometheus/ -> Prometheus
  - /grafana/ -> Grafana  
  See [nginx/default.conf](nginx/default.conf).
- Prometheus scrapes the Flask client for metrics at /metrics (configured in [prometheus/prometheus.yml](prometheus/prometheus.yml)).
- Grafana is configured for dashboards using [grafana/grafana.ini](grafana/grafana.ini).

---

## How it works (details)

1. Generation of short URL
   - Frontend sends POST to API at /url with JSON { "url": "<target>" } (see [client/.env](client/.env) variables: `API_POST_URL`).
   - Route handler: [server/routes/url.js](server/routes/url.js) mounts the controller.
   - Controller [`handleGenerateNewShortURL`](server/controllers/url.js):
     - Validates payload.
     - Generates a nanoid short id.
     - Saves a document to MongoDB using the Mongoose model [`URL`](server/models/url.js) with `visitHistory: []`.
     - Returns JSON { id: shortId }.

2. Redirection
   - When a visitor requests GET /:shortId on the API, [server/server.js](server/server.js) does:
     - findOneAndUpdate to push a visit record into visitHistory (timestamp).
     - returns JSON { redirectUrl, shortId } so the client (Flask) can 302-redirect.

3. Analytics
   - GET /analytics/:shortId returns the `visitHistory` array and a computed `visitCount`. Implemented in [server/server.js](server/server.js).

4. Metrics & monitoring
   - Flask client exposes Prometheus metrics via prometheus_flask_exporter; metrics include counters for creations, redirects, and failed redirects (see [client/app.py](client/app.py)).
   - Prometheus scrapes the client; Grafana provides dashboards.

---

## Environment variables

- server/.env — used by API when starting with nodemon (see [server/.env](server/.env)):
  - MONGO_URI (example): mongodb://kaap:kaap@mongodb/?directConnection=true
  - PORT (example): 8001

- client/.env — used by client to know where to call the API (see [client/.env](client/.env)):
  - API_GET_ANALYTICS=http://server:8001/analytics
  - API_GET_URL=http://server:8001/
  - API_POST_URL=http://server:8001/url

Notes:
- In Docker Compose the services communicate by service name (e.g. `server`, `mongodb`), which matches these values.
- Ensure `.env` files are present if you run containers locally and the container images rely on them.

---

## Run locally with Docker Compose (recommended)

1. From repo root, build and start everything:
   - Linux / macOS:
     - docker compose up --build
   - Windows (Docker Desktop):
     - docker compose up --build

2. Access services:
   - Nginx (public entrypoint): http://localhost (port 80) and https://localhost (443, self-signed)
     - Frontend is proxied at `/` by Nginx (see [nginx/default.conf](nginx/default.conf)).
   - Prometheus UI: http://localhost/prometheus/ (proxied)
   - Grafana UI: http://localhost/grafana/ (proxied)

3. Quick API examples (direct to API container, without Nginx):
   - Create short URL:
     - curl -X POST http://localhost:8001/url -H "Content-Type: application/json" -d '{"url":"https://example.com"}'
   - Redirect info:
     - curl http://localhost:8001/<shortId>
   - Analytics:
     - curl http://localhost:8001/analytics/<shortId>

Note: When using docker compose, the API container listens on 8001 internally. If you need to access API directly from host, you can add a ports mapping to docker-compose.yaml for the `server` service.

---

## Build images separately

- API:
  - cd server
  - docker build -t url-shortener-api:local .
- Client:
  - cd client
  - docker build -t url-shortener-client:local -f dockerfile .

---

## CI / Lint / Tests

- GitHub Actions workflow: [.github/workflows/test.yml](.github/workflows/test.yml) runs:
  - Node.js: npm install, npx eslint ., npx jest --passWithNoTests
  - Python (client): pip install -r requirements.txt, flake8, pytest
- pre-push hook: [pre-push](pre-push) builds/testing inside Docker for pre-push checks.

---

## Important files & symbols (quick links)

- API entrypoint: [server/server.js](server/server.js)  
- DB connector: [`connectDB`](server/connect.js) — [server/connect.js](server/connect.js)  
- URL controller: [`handleGenerateNewShortURL`](server/controllers/url.js) — [server/controllers/url.js](server/controllers/url.js)  
- Router: [`urlRoute`](server/routes/url.js) — [server/routes/url.js](server/routes/url.js)  
- Mongoose model: [`URL`](server/models/url.js) — [server/models/url.js](server/models/url.js)  
- Frontend app: [client/app.py](client/app.py) — functions: [`index`](client/app.py), [`go`](client/app.py), [`Analytics`](client/app.py)  
- Compose orchestration: [docker-compose.yaml](docker-compose.yaml)  
- Nginx config: [nginx/default.conf](nginx/default.conf)  
- Prometheus config: [prometheus/prometheus.yml](prometheus/prometheus.yml)  
- Grafana config: [grafana/grafana.ini](grafana/grafana.ini)  
- CI: [.github/workflows/test.yml](.github/workflows/test.yml)  
- Local pre-push: [pre-push](pre-push)

---

Use `docker compose up --build` to bring the full stack up