import pandas as pd
import json
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Recommender loaded")

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sample_data.csv')
_OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_URL = f"{_OLLAMA_BASE}/api/generate"
OLLAMA_MODEL = "phi3"

# Load data and embed descriptions once at startup
df = pd.read_csv(DATA_PATH)
model = SentenceTransformer('all-MiniLM-L6-v2')
item_embeddings = model.encode(df['description'].tolist())
print(f"Ready: {len(df)} courses embedded.")


def get_recommendations(user_profile: dict) -> list:
    print("Recommender loaded", flush=True)

    topic = user_profile["topic"]
    viewed_ids = set(user_profile.get("viewed_content_ids", []))

    print(f"\n{'='*60}")
    print(f"[REQUEST] User: {user_profile['name']} | Topic: {topic}")
    print(f"[REQUEST] Filters → difficulty={user_profile.get('difficulty')}, "
          f"time={user_profile.get('time_per_day_minutes')}, "
          f"style={user_profile.get('learning_style')}")
    print(f"[REQUEST] Viewed IDs: {list(viewed_ids)}")

    # --- Step 1: Hard filter ---
    filtered = df[~df['id'].isin(viewed_ids)].copy()
    print(f"\n[FILTER] After removing viewed: {len(filtered)} courses")

    if user_profile.get("difficulty"):
        filtered = filtered[filtered['difficulty'] == user_profile["difficulty"]]
        print(f"[FILTER] After difficulty='{user_profile['difficulty']}': {len(filtered)} courses")

    if user_profile.get("learning_style"):
        filtered = filtered[filtered['format'] == user_profile["learning_style"]]
        print(f"[FILTER] After format='{user_profile['learning_style']}': {len(filtered)} courses")

    if user_profile.get("time_per_day_minutes"):
        filtered = filtered[filtered['duration_minutes'] <= user_profile["time_per_day_minutes"]]
        print(f"[FILTER] After duration<={user_profile['time_per_day_minutes']}min: {len(filtered)} courses")

    if filtered.empty:
        print("[FILTER] No courses left after filtering. Returning empty.")
        return []

    # --- Step 2: Cosine similarity on filtered rows ---
    user_emb = model.encode([topic])
    filtered_indices = filtered.index.tolist()
    filtered_embeddings = item_embeddings[filtered_indices]

    scores = cosine_similarity(user_emb, filtered_embeddings)[0]
    filtered = filtered.copy()
    filtered['score'] = scores

    top10 = filtered.sort_values('score', ascending=False).head(10).to_dict(orient='records')

    print(f"\n[COSINE] Top 10 candidates:")
    for c in top10:
        print(f"  id={c['id']} | score={c['score']:.4f} | {c['title']} ({c['difficulty']}, {c['duration_minutes']}m, {c['format']})")

    top_score = top10[0]['score'] if top10 else 0
    if top_score < 0.3:
        print(f"[WARN] Top cosine score {top_score:.4f} too low — no relevant courses in filtered pool")
        return []
    
    # --- Step 3: LLM re-ranking + explanation in one call ---
    candidate_ids = [c["id"] for c in top10]

    ranking_prompt = f"""You are a course recommender. The user wants to learn: '{topic}'.

Rank the TOP 3 most relevant courses from the list below and explain why each fits.
Return ONLY a JSON array of exactly 3 objects. No markdown, no extra text.

Courses:
{json.dumps([{"id": c["id"], "title": c["title"]} for c in top10], indent=2)}

Return format:
[{{"id": 5, "explanation": "one sentence why this fits"}}, ...]"""

    print(f"\n[LLM] Sending ranking + explanation request to {OLLAMA_MODEL}...")
    rank_resp = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": ranking_prompt, "stream": False},
        timeout=60
    )
    rank_resp.raise_for_status()

    raw_response = rank_resp.json()["response"]
    print(f"[LLM] Raw response: {raw_response}")

    # Strip markdown if phi3 wraps in backticks
    import re
    cleaned = re.search(r'\[.*?\]', raw_response, re.DOTALL)
    if not cleaned:
        print("[WARN] Could not parse LLM response, falling back to cosine order")
        ranked = [{"id": c["id"], "explanation": ""} for c in top10[:3]]
    else:
        ranked = json.loads(cleaned.group())

    # Filter hallucinated IDs
    ranked = [r for r in ranked if r["id"] in candidate_ids]
    if len(ranked) < 3:
        print("[WARN] Too few valid IDs from LLM, padding with cosine order")
        existing_ids = [r["id"] for r in ranked]
        for c in top10:
            if c["id"] not in existing_ids:
                ranked.append({"id": c["id"], "explanation": ""})
            if len(ranked) == 3:
                break

    # Attach full metadata
    result = []
    for rec in ranked[:3]:
        orig = next((c for c in top10 if c["id"] == rec["id"]), None)
        if orig:
            result.append({
                "id": orig["id"],
                "title": orig["title"],
                "url": orig["url"],
                "format": orig["format"],
                "duration_minutes": orig["duration_minutes"],
                "difficulty": orig["difficulty"],
                "tags": orig["tags"],
                "explanation": rec.get("explanation", "")
            })

    print(f"\n[RESULT] Returning {len(result)} recommendations:")
    for r in result:
        print(f"  id={r['id']} | {r['title']} | explanation={'✓' if r.get('explanation') else '✗ MISSING'}")
    print(f"{'='*60}\n")

    return result
