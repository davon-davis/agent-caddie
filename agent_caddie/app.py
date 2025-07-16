from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import openai
import os
from dotenv import load_dotenv

# Import your modules using absolute paths if app.py is at the project root
from .prompts import build_prompt
from .analytics import compute_effective_distance
from .db import save_club_distances, get_similar_shots, save_shot

app = FastAPI()

# Serve React at /
app.mount("/", StaticFiles(directory="frontend_dist", html=True), name="frontend")

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
# Enable CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173", "http://localhost:8000", "http://127.0.0.1:5173"],  # React dev server
    allow_origins=[API_BASE_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClubDistanceEntry(BaseModel):
    user_id: str
    club: str
    distance: float

class ShotDetails(BaseModel):
    user_id: str
    scenario_text: str
    distance: float
    lie: str
    ball_pos: str
    elevation: float
    wind_dir: str
    wind_speed: float

@app.get("/")
async def root():
    return {"message": "Hello World! V-Caddie API is running at http://localhost:8000/"}

@app.post("/api/caddie/update-yardages")
async def update_yardages(entries: List[ClubDistanceEntry]):
    """
    Record or update average carry distances for a user’s clubs.
    """
    try:
        save_club_distances([entry.dict() for entry in entries])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    return {"saved": len(entries)}

@app.post("/api/caddie/recommend")
async def recommend(details: ShotDetails):
    """
    Stream a club recommendation based on shot details and past performance.
    """
    # 1) Compute effective distance
    scn = details.model_dump()
    scn["effective_dist"] = compute_effective_distance(scn)

    # 2) Fetch similar past shots
    past = get_similar_shots(scn["scenario_text"])

    # 3) Build prompt and call OpenAI with streaming
    messages = build_prompt(scn, past)
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,  # type: ignore
            stream=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

    async def event_stream():
        for chunk in response:
            delta = chunk.choices[0].delta
            token = getattr(delta, "content", None)
            if token:
                yield token
            

    return StreamingResponse(event_stream(), media_type="text/plain; charset=utf-8")

@app.post("/api/caddie/record")
async def record_shot(details: ShotDetails):
    """
    Record the outcome of a shot after recommendation.
    """
    data = details.model_dump()
    try:
        save_shot(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    return JSONResponse({"success": True})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
