# Depi_Project

A small monorepo that demonstrates a simple URL shortener with:

- **Client (Flask)** – a minimal UI to submit a long URL and copy the generated short link.
- **Server (Node.js/Express + MongoDB)** – REST API that creates short IDs, redirects, and tracks visit history.
- **Database** – MongoDB instance (via Docker Compose) with a URL collection.

> This README was written after inspecting the repo structure (folders: `client/`, `server/`, `database/`, `docker-compose.yaml`). If anything below differs from your code, tweak paths/names to match.

---

## Table of Contents

- [Architecture](#architecture)
- [Monorepo Structure](#monorepo-structure)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Getting Started](#getting-started)

  - [Option A — Run with Docker Compose](#option-a--run-with-docker-compose)
  - [Option B — Run Locally (no Docker)](#option-b--run-locally-no-docker)

- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Data Model](#data-model)

---

## Architecture

![Architecture](/diagram-export-8-27-2025-6_14_39-PM.png)

- The **Flask client** calls the **Node API** to create short URLs, then redirects the user to the `shortId` link.
- The **API** handles: create short URL, redirect by `shortId`, and basic analytics (visit counts).
- **MongoDB** stores the mapping `{ shortId, redirectUrl, visitHistory[] }`.

---

## Monorepo Structure

```
Depi_Project/
├─ client/                 # Flask UI
│  ├─ app.py               # Flask entrypoint (example name)
│  ├─ templates/           # Jinja templates
│  └─ static/              # CSS/JS assets
│
├─ server/                 # Node.js/Express API
│  ├─ src/
│  │  ├─ index.js          # Express app bootstrap
│  │  ├─ routes/           # Routes (e.g., url.js)
│  │  └─ models/           # Mongoose models (e.g., URL.js)
│  ├─ package.json
│  └─ .env.example         # Example server envs (add if missing)
│
├─ database/               # DB init/seed scripts (optional)
│  └─ init.js              # Mongo init script (optional)
│
├─ docker-compose.yaml     # Orchestration for client, server, mongo
└─ .gitignore              # (typo in repo: .gitigonre)
```

> If names differ, adjust the references accordingly.

---

## Tech Stack

- **Client:** Python 3, Flask, Jinja, Requests
- **Server:** Node.js (18+), Express, Mongoose, NanoID/shortid (any ID lib), CORS
- **Database:** MongoDB
- **Infra/Dev:** Docker, Docker Compose

---

## Features

- Shorten a long URL into a compact `/:shortId`.
- Redirect to the original URL via `GET /:shortId`.
- Track clicks with `visitHistory` timestamps.
- Minimal web UI to submit a URL and copy the short link.
- Dockerized dev environment.

---

## Getting Started

### Prerequisites

- **Docker & Docker Compose** (for Option A), or
- **Node.js**, **Python 3.10+**, and **MongoDB** locally (for Option B).

### Option A — Run with Docker Compose

1. Copy env files (create them if missing):

- **Server** (`server/.env`):

```
PORT=8001
MONGO_URI=mongodb://kaap:kaap@mongodb/?directConnection=true

```

- **Client** (`client/.env` or config in `app.py`):

```
API_GET_URL=http://server:8001/
API_POST_URL=http://server:8001/url

```

2. From the repo root:

```bash
docker compose up --build
```

3. Open the app:

- UI: [http://localhost:80](http://localhost:80)
- API: [http://localhost:8001](http://localhost:8001)
- Mongo (container name `mongo`) listens on `27017` inside the network.

To stop:

```bash
docker compose down
```

### Option B — Run Locally (no Docker)

#### 1) Start MongoDB

- Ensure a local Mongo is running on `mongodb://localhost:27017` (or update `MONGO_URI`).

#### 2) Start the API server

```bash
cd server
npm install
# set envs in server/.env or export in shell
npm run dev        # or: node src/index.js
```

Expects envs:

```
PORT=8001
MONGO_URI=mongodb://localhost:27017/
CORS_ORIGIN=http://localhost:80
BASE_URL=http://localhost:8001
```

#### 3) Start the Flask client

```bash
cd client
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# set API_BASE_URL in client/.env or app.py
flask --app app run --host 0.0.0.0 --port 80
```

Open [http://localhost:80](http://localhost:80)

---

## Environment Variables

### Server (`server/.env`)

| Name          | Example                               | Description                                      |
| ------------- | ------------------------------------- | ------------------------------------------------ |
| `PORT`        | `8001`                                | Port for Express server                          |
| `MONGO_URI`   | `mongodb://kaap:kaap@mongodb/?directConnection=true` | MongoDB connection string                        |
| `CORS_ORIGIN` | `http://localhost:80`               | Allowed origin for Flask UI                      |
| `BASE_URL`    | `http://localhost:8001`               | Public base URL used when generating short links |

### Client (`client/.env`)

| Name           | Example              | Description                            |
| -------------- | -------------------- | -------------------------------------- |
| `API_BASE_URL` | `http://server:8001` | Internal URL for API requests (Docker) |


---

## API Reference

> Replace/augment below to match your actual routes.

### Create short URL

`POST /url`

```json
{
  "url": "https://example.com/very/long/path"
}
```

**201 Created**

```json
{
  "id": "abc123", // shortId
  "redirectUrl": "https://example.com/very/long/path",
}
```

### Redirect by shortId

`GET /:shortId`

- 302 redirect to the target URL.
- Side effect: pushes `{ timestamp: <now> }` into `visitHistory`.

### Analytics

`GET /analytics/:shortId`
**200 OK**

```json
{
  "totalClicks": 42,
  "visitHistory": [
    { "timestamp": 1723500000000 },
    { "timestamp": 1723600000000 }
  ]
}
```

---

## Data Model

```js
// server/src/models/URL.js (example)
const URL = {
  shortId: String,
  redirectUrl: String,
  visitHistory: [{ timestamp: Number }],
};
```

- `shortId` – unique slug.
- `redirectUrl` – destination URL.
- `visitHistory` – list of click timestamps (epoch ms).
