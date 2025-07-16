import os
from supabase.client import create_client
from dotenv import load_dotenv

from .embeddings import get_embedding

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)  # type: ignore


def save_club_distances(entries):
    supabase.table("club_distances")\
        .upsert(entries, on_conflict="user_id,club")\
        .execute()

def save_shot(entry):
    if entry.get("cause") == "Mis-hit":
        return
    # build a flat dict matching your shots table
    db_row = {
        "user_id":           entry["user_id"],
        "scenario_text":     entry["scenario_text"],
        "distance":          entry["distance"],
        "lie":               entry["lie"],
        "ball_pos":          entry["ball_pos"],
        "wind_dir":          entry["wind"]["direction"],
        "wind_speed":        entry["wind"]["speed"],
        "elevation":         entry["elevation"],
        "effective_dist":    entry["effective_dist"],
        "recommended_club":  entry["recommended_club"],
        "carried":           entry["carried"],
        "error":             entry["error"],
        "result":            entry["result"],
        "cause":             entry.get("cause"),
        "embedding":         get_embedding(entry["scenario_text"])
    }
    supabase.table("shots").insert(db_row).execute()

def get_similar_shots(scenario_text: str, k: int = 3) -> list[dict]:
    # 1) embed the scenario
    emb = get_embedding(scenario_text)

    # 2) call the SQL function via RPC
    resp = (
      supabase
      .rpc("match_shots", {"query_embedding": emb, "match_count": k})
      .execute()
    )
    return resp.data or []


