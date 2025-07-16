from questionary import text, select

LIE_ADJ = {
  "Above feet": +5, "Below feet": -5,
  "Rough": +8, "Sand / Bunker": +12
}

def wind_adj(dir, sp):
    base = sp * 0.5
    return base if dir=="Headwind" else -base if dir=="Tailwind" else 0

def compute_effective_distance(scn):
    return (
      scn["distance"]
      + LIE_ADJ.get(scn["lie"], 0)
      + wind_adj(scn["wind_dir"], scn["wind_speed"])
    )

def record_shot_result(scn):
    carried = float(text("How many yards did it carry?").ask())
    error = carried - scn["distance"]
    if abs(error) <= 5: res="perfect"
    elif error<0:     res="too short"
    else:             res="too long"
    cause = None
    if res!="perfect":
        cause = select("What went wrong?", choices=[
          "Mis-hit","Club selection","Wind mis-judge","Other"
        ]).ask()
    return {"carried":carried,"error":error,"result":res,"cause":cause}
