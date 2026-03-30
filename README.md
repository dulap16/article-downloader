# Article Downloader

Recursively download web articles and all their linked pages as clean, readable HTML files. Paste a URL, choose how deep to follow links, and get a ZIP of neatly formatted articles you can read offline.

## The Problem

You're reading a great article — a TLDR summary, a Wikipedia page, a blog post — and it links to five other interesting articles. Each of those links to five more. If you save just the original page, you lose all that depth. **Article Downloader** grabs the whole tree so you can read everything offline, at your own pace.

## How It Works

1. **Paste a URL** into the web interface.
2. **Choose a depth** (0–5). Depth 0 downloads only the page itself. Depth 1 also downloads every page it links to. Depth 2 goes one level further, and so on.
3. **Toggle "same domain only"** to stay on one site or follow links everywhere.
4. **Click Download Articles** — the crawler runs in the background.
5. When it finishes, **download a ZIP** of clean HTML files you can open in any browser.

The crawler uses [readability](https://github.com/mozilla/readability) (the same algorithm behind Firefox Reader View) to strip ads, navigation, and clutter, leaving just the article text, images, and links.

## Tech Stack

| Layer      | Technology                              |
|------------|-----------------------------------------|
| Backend    | Python 3.12, FastAPI, httpx, BeautifulSoup, readability-lxml |
| Frontend   | React 18, vanilla CSS (dark theme)      |
| Packaging  | Docker, Docker Compose                  |
| CI/CD      | GitHub Actions                          |
| Deployment | Railway, VPS (docker-compose), GHCR     |

## Quick Start

### Option 1: Docker Compose (recommended)

```bash
git clone https://github.com/dulap16/article-downloader.git
cd article-downloader
docker compose up --build
```

Open [http://localhost](http://localhost) in your browser.

### Option 2: Run locally without Docker

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm start
```

The React dev server starts at [http://localhost:3000](http://localhost:3000) and proxies API requests to port 8000.

## API Reference

| Method   | Endpoint                    | Description                          |
|----------|-----------------------------|--------------------------------------|
| `POST`   | `/api/crawl`                | Start a new crawl job                |
| `GET`    | `/api/jobs`                 | List all jobs                        |
| `GET`    | `/api/jobs/{id}`            | Get job status and page list         |
| `GET`    | `/api/jobs/{id}/download`   | Download crawled pages as ZIP        |
| `DELETE` | `/api/jobs/{id}`            | Delete a job and its files           |
| `GET`    | `/api/health`               | Health check                         |

### Start a crawl

```bash
curl -X POST http://localhost:8000/api/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article", "depth": 2, "same_domain_only": true}'
```

## Configuration

Copy `.env.example` to `.env` and adjust:

| Variable                  | Default                 | Description                        |
|---------------------------|-------------------------|------------------------------------|
| `DOWNLOAD_DIR`            | `./downloads`           | Where crawled files are stored     |
| `ALLOWED_ORIGINS`         | `http://localhost:3000`  | CORS allowed origins (comma-separated) |
| `MAX_CONCURRENT_REQUESTS` | `5`                     | Max parallel HTTP requests         |
| `REQUEST_TIMEOUT`         | `30`                    | Per-request timeout in seconds     |
| `REACT_APP_API_URL`       | `/api`                  | API base URL for the frontend      |

## Project Structure

```
article-downloader/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── crawler.py        # Recursive crawl engine
│   │   ├── models.py         # Pydantic schemas
│   │   └── routes.py         # API endpoints
│   ├── tests/
│   │   ├── test_api.py       # API integration tests
│   │   └── test_crawler.py   # Crawler unit tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CrawlForm.js  # URL input & depth selector
│   │   │   ├── JobCard.js    # Individual job display
│   │   │   └── JobList.js    # Job list container
│   │   ├── api.js            # API client
│   │   ├── App.js            # Root component
│   │   └── App.css           # Styles (dark theme)
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── .github/workflows/
│   ├── ci.yml                # Lint, test, build on push/PR
│   └── deploy.yml            # Build & push images on tag
├── docker-compose.yml        # Local development
├── docker-compose.prod.yml   # Production with GHCR images
├── railway.toml              # Railway deployment config
└── .env.example
```

## Deployment

### Railway

1. Fork this repo.
2. Connect it to [Railway](https://railway.app).
3. Railway auto-detects `railway.toml` and deploys the backend.
4. Set environment variables in the Railway dashboard.

### VPS with Docker

```bash
# Pull pre-built images and start
docker compose -f docker-compose.prod.yml up -d
```

### GitHub Container Registry

Tagged releases (e.g., `v1.0.0`) automatically build and push images to GHCR via the deploy workflow.

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest -v --cov=app
```

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes with descriptive messages.
4. Push and open a pull request against `main`.

## License

MIT
