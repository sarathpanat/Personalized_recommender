import csv
import os
import random
import json
import requests

# Ollama configuration
_OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_URL = f"{_OLLAMA_BASE}/api/generate"
MODEL_NAME = "phi3"

topics = ["Kubernetes", "Machine Learning", "Docker"]
difficulty_levels = ["Beginner", "Intermediate", "Advanced"]
formats = ["video", "article", "blog"]
tags_pool = ["kubernetes", "ml", "deployment", "docker", "ai", "python", "architecture"]


def generate_llm_content(topic, difficulty, fmt):
    prompt = f"""
You are an expert technical content creator.

Generate:
1. A professional educational title
2. A short explanatory description (2-3 sentences)

Topic: {topic}
Difficulty: {difficulty}
Format: {fmt}

Rules:
- Beginner = simple and foundational
- Intermediate = practical and applied
- Advanced = deep technical and production-level
- Return ONLY valid JSON in this format:

{{
  "title": "...",
  "description": "..."
}}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        result = response.json()
        content = result.get("response", "").strip()

        # 🔥 Robust JSON extraction
        start = content.find("{")
        end = content.rfind("}") + 1
        json_string = content[start:end]

        parsed = json.loads(json_string)

        return parsed.get("title"), parsed.get("description")

    except Exception as e:
        print("❌ Parsing error:", e)
        print("Raw output:", content if 'content' in locals() else "No content")
        return None, None


def generate_dataset(num_rows=250):
    data = []
    current_id = 1

    while len(data) < num_rows:
        topic = random.choice(topics)
        difficulty = random.choice(difficulty_levels)
        fmt = random.choice(formats)

        title, description = generate_llm_content(topic, difficulty, fmt)

        if not title or not description:
            print("⚠️ Skipping row due to parsing issue")
            continue

        duration = random.choice([15, 30, 45, 60, 90, 120])
        num_tags = random.randint(2, 4)
        tags = random.sample(tags_pool, num_tags)

        url = f"https://example.com/tutorials/{topic.lower().replace(' ', '-')}/{current_id}"

        row = {
            "id": current_id,
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "duration_minutes": duration,
            "tags": json.dumps(tags),
            "format": fmt,
            "url": url
        }

        print(f"✅ Generated: {title}")

        data.append(row)
        current_id += 1

    return data


def main():
    data = generate_dataset(250)

    keys = [
        "id",
        "title",
        "description",
        "difficulty",
        "duration_minutes",
        "tags",
        "format",
        "url"
    ]

    with open("data/sample_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

    print("🎉 Successfully generated dataset using phi3")


if __name__ == "__main__":
    main()