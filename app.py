import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, redirect, url_for
from db import get_conn
from ingest import refresh_player

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/player/<game_name>/<tag_line>")
def player(game_name, tag_line):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # find puuid (if already ingested)
    cur.execute("SELECT puuid FROM players WHERE game_name=%s AND tag_line=%s", (game_name, tag_line))
    row = cur.fetchone()
    puuid = row["puuid"] if row else None

    matches = []
    if puuid:
        cur.execute("""
          SELECT m.match_id, m.game_datetime, p.placement, p.level
          FROM participants p
          JOIN matches m ON m.match_id = p.match_id
          WHERE p.puuid=%s
          ORDER BY m.game_datetime DESC
          LIMIT 20
        """, (puuid,))
        matches = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("player.html", game_name=game_name, tag_line=tag_line, puuid=puuid, matches=matches)

@app.post("/refresh/<game_name>/<tag_line>")
def refresh(game_name, tag_line):
    refresh_player(game_name, tag_line, count=20)
    return redirect(url_for("player", game_name=game_name, tag_line=tag_line))

@app.get("/match/<match_id>")
def match(match_id):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM matches WHERE match_id=%s", (match_id,))
    m = cur.fetchone()

    cur.execute("""
      SELECT puuid, placement, level, last_round, total_damage_to_players
      FROM participants WHERE match_id=%s
      ORDER BY placement ASC
    """, (match_id,))
    ps = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("match.html", match=m, participants=ps)

@app.get("/analytics")
def analytics():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # Example: traits with best average placement (lower is better)
    cur.execute("""
      SELECT trait_name, COUNT(*) as n, AVG(p.placement) as avg_place
      FROM participant_traits t
      JOIN participants p
        ON p.match_id=t.match_id AND p.puuid=t.puuid
      GROUP BY trait_name
      HAVING n >= 50
      ORDER BY avg_place ASC
      LIMIT 20
    """)
    traits = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("analytics.html", traits=traits)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
