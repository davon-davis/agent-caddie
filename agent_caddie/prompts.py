from questionary import text, select

def ask_shot_details():
    d = float(text("Distance to pin (yards)?").ask())
    lie = select("What’s the lie?", choices=[
      "Fairway","Rough","Sand / Bunker","Tree line","Pine straw"
    ]).ask()
    ball_pos = select("Ball position?", choices=["Level","Above feet","Below feet"]).ask()
    elev = select("Elevation change?", choices=["Level","Downhill","Uphill"]).ask()
    wind_dir = select("Wind direction?", choices=[
      "Headwind","Tailwind","Left→Right","Right→Left","None"
    ]).ask()
    wind_sp = float(text("Wind speed (mph)?").ask())
    scenario = {
      "distance": d, "lie": lie, "ball_pos": ball_pos,
      "wind": {"direction": wind_dir, "speed": wind_sp},
      "elevation": elev
    }
    scenario["scenario_text"] = (
      f"{d}y, lie={lie}, ball_pos={ball_pos}, wind={wind_sp}mph {wind_dir}, elev={elev}"
    )
    return scenario

def build_prompt(scn, past_shots):
    intro = (
      f"Effective distance: {scn['effective_dist']} y "
      f"({scn['distance']} base + adjustments).\n\n"
      "Similar past shots:\n"
    )
    for p in past_shots:
        intro += (
          f"- You took {p['recommended_club']} and carried {p['carried']}y ({p['result']}).\n"
        )
    return [
      {"role":"system","content":"You’re a golf caddie balancing conditions and history."},
      {"role":"user","content": intro + "\nGiven this, what club would you suggest?"}
    ]
