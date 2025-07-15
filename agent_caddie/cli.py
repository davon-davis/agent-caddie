import click
import openai
from questionary import text, select
from tabulate import tabulate

from .prompts import ask_shot_details, build_prompt
from .analytics import compute_effective_distance, record_shot_result
from .db import save_shot, get_similar_shots, save_club_distances

@click.group()
def cli():
    """V-Caddie CLI."""
    pass

@cli.command()
@click.option("--user-id", required=True, help="Your unique user ID")
def update(user_id):
    """Record or update your average carry distance for each club."""
    clubs = [
        "Driver", "3-Wood", "5-Wood",
        "3-Iron", "4-Iron", "5-Iron", "6-Iron",
        "7-Iron", "8-Iron", "9-Iron",
        "Pitching Wedge", "Sand Wedge",
        "48°", "50°", "52°", "54°", "56°", "58°", "60°"
    ]

    entries = []
    click.echo("\nEnter your average carry distance for each club.")
    click.echo("Press Enter to skip any club you don’t have.\n")

    for club in clubs:
        ans = text(f"{club}:").ask()
        if not ans or not ans.strip():
            click.echo(f"  • Skipping {club}")
            continue

        try:
            dist = float(ans)
        except ValueError:
            click.echo(f"  ⚠ '{ans}' isn’t a number; skipping {club}.")
            continue

        entries.append({
            "user_id": user_id,
            "club": club,
            "distance": dist
        })

    if entries:
        save_club_distances(entries)
        click.echo("\n✅ Your club distances have been saved:")
        table = [(e["club"], e["distance"]) for e in entries]
        click.echo(tabulate(table, headers=["Club", "Avg Carry (yd)"], tablefmt="github"))
    else:
        click.echo("\n⚠ No distances entered; nothing was saved.")

@cli.command()
@click.option("--user-id", required=True, help="Your unique user ID")
def shot(user_id):
    """Get a club recommendation for your next shot."""
    # 1. Gather shot details
    scn = ask_shot_details()
    scn["effective_dist"] = compute_effective_distance(scn)

    # 2. Retrieve similar past shots
    past = get_similar_shots(scn["scenario_text"])

    # 3. Build and send prompt
    prompt = build_prompt(scn, past)
    resp = openai.chat.completions.create(  # ✅ new v1 style
        model="gpt-3.5-turbo",
        messages=prompt,  # type: ignore
        stream=True
    )

    # 4. Show recommendation
    club = resp.choices[0].message.content.strip() if resp.choices and resp.choices[0].message.content else "No recommendation"
    click.echo(f"\n→ I’d take your {club}\n")

    # 5. Record outcome and save
    outcome = record_shot_result(scn)
    save_shot({
        **scn,
        **outcome,
        "user_id": user_id,
        "recommended_club": club
    })
    click.echo("🏌️  Shot logged. Good luck on the next one!")
