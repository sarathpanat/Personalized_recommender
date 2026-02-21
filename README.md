# Personalized Course Recommender (Dockerized)

A full-stack course recommendation system using **FastAPI**, **Streamlit**, **Ollama (phi3)**, and **Sentence Transformers**. This project is fully containerized using Docker Compose.

## Features

- **Multi-user support**: Track viewed courses per user.
- **Semantic search**: Find courses similar to user queries.
- **LLM-powered explanations**: Generate personalized reasoning for recommendations.
- **Flexible filtering**: Filter by difficulty, time, and learning style.
- **Automatic data generation**: Generates `sample_data.csv` on first run.

## Prerequisites

- **Docker** and **Docker Compose** installed and running.

## Quick Start

1. **Clone the repository** (if not already done).

2. **Start the application**:
   ```bash
   docker compose up --build
   ```

3. **Access the application**:
   - **Frontend**: [http://localhost:8501](http://localhost:8501)
   - **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Stop the application**:
   ```bash
   docker compose down
   ```

## Recommendation Logic

1. **Generate embeddings** — Course descriptions are embedded using `all-MiniLM-L6-v2` (Sentence Transformers) at startup.
2. **Pre-filter** — Remove already-viewed courses; apply hard constraints.
3. **Semantic retrieval** — Embed the user's topic query and compute cosine similarity against all course embeddings → Top-K candidates.
4. **LLM re-ranking** — Send Top-K to Ollama `phi3`, which re-ranks by relevance and returns structured JSON with one-sentence explanations.
5. **Constraints respected** — Difficulty level, time per day, learning style, previously viewed content are all excluded before retrieval.

## How It Works

### 1. Ollama (LLM)
- Runs in a dedicated container (`ollama`).
- Automatically pulls and serves the `phi3` model on first startup.
- Provides embeddings and text generation for the recommendation engine.

### 2. Data Initialization
- The `data-init` container runs `llm_gen.py` **only if** `data/sample_data.csv` is missing.
- Generates 100+ course entries with realistic details.

### 3. FastAPI Backend
- Exposes `/recommend` endpoint.
- Uses **Sentence Transformers** for semantic similarity.
- Uses **Ollama** for generating personalized explanations.
- Persists user data in `profiles.json`.

### 4. Streamlit Frontend
- Simple 2-page UI:
  1. Enter your name (creates/loads profile).
  2. Enter topic + filters → get recommendations.
- Tracks viewed courses to improve future suggestions.

## Project Structure

```
Personalized_recommender/
├── backend/            # FastAPI application
├── frontend/           # Streamlit application
├── data/               # Generated course data
├── Dockerfile          # Build frontend + backend
├── docker-compose.yml  # Orchestrates all services
├── entrypoint.sh       # Auto-generates CSV on first run
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Environment Variables

The application uses the following environment variables (set automatically by Docker Compose):

- `OLLAMA_BASE_URL`: `http://ollama:11434`
- `BACKEND_URL`: `http://backend:8000`

## Troubleshooting

- **Ollama not starting**: Check `docker logs ollama`.
- **CSV not generating**: Ensure `data/` directory exists and has write permissions.
- **Port conflicts**: Change `ports` in `docker-compose.yml` if needed.
- **Reset data**: Run `docker compose down -v` to remove all volumes (including models and profiles).

