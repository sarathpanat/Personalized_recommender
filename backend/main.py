from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from backend.recommender import get_recommendations

app = FastAPI(title="Course Recommender API")


class UserProfile(BaseModel):
    name: str
    topic: str                              # mandatory
    difficulty: Optional[str] = None       # maps to difficulty column
    time_per_day_minutes: Optional[int] = None  # maps to duration_minutes column
    learning_style: Optional[str] = None   # maps to format column
    viewed_content_ids: List[int] = []


@app.post("/recommend")
def recommend(profile: UserProfile):
    return get_recommendations(profile.model_dump())
