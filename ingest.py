from dotenv import load_dotenv

from db import get_conn
from riot_api import RiotAPI

load_dotenv()

def upsert_player(conn, puuid, game_name, tag_line):
    q = """
    INSERT INTO players (puuid, game_name, tag_line)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE
      game_name = COALESCE(VALUES(game_name), game_name),
      tag_line  = COALESCE(VALUES(tag_line), tag_line)
    """
    cur = conn.cursor()
    cur.execute(q, (puuid, game_name, tag_line))
    cur.close()


def insert_match(conn, m):
    info = m["info"]
    q = """
    INSERT IGNORE INTO matches
      (match_id, game_datetime, game_length, tft_set_number, tft_game_type, queue_id)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur = conn.cursor()
    cur.execute(q, (
        m["metadata"]["match_id"],
        info.get("game_datetime"),
        info.get("game_length"),
        info.get("tft_set_number"),
        info.get("tft_game_type"),
        info.get("queue_id"),
    ))
    cur.close()

def insert_participant_bundle(conn, match_id, p):
    # participants
    q1 = """
    INSERT IGNORE INTO participants
      (match_id, puuid, placement, level, last_round, players_eliminated, total_damage_to_players)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cur = conn.cursor()
    cur.execute(q1, (
        match_id, p["puuid"], p.get("placement"), p.get("level"), p.get("last_round"),
        p.get("players_eliminated"), p.get("total_damage_to_players")
    ))

    # traits
    q2 = """
    INSERT IGNORE INTO participant_traits
      (match_id, puuid, trait_name, tier_current, num_units, style)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    for t in p.get("traits", []):
        cur.execute(q2, (
            match_id, p["puuid"], t.get("name"), t.get("tier_current"),
            t.get("num_units"), t.get("style")
        ))

    # units
    q3 = """
    INSERT IGNORE INTO participant_units
      (match_id, puuid, character_id, tier, rarity)
    VALUES (%s, %s, %s, %s, %s)
    """
    for u in p.get("units", []):
        cur.execute(q3, (
            match_id, p["puuid"], u.get("character_id"),
            u.get("tier"), u.get("rarity")
        ))

    # augments
    q4 = """
    INSERT IGNORE INTO participant_augments
      (match_id, puuid, augment_id)
    VALUES (%s, %s, %s)
    """
    for a in p.get("augments", []):
        cur.execute(q4, (match_id, p["puuid"], a))

    cur.close()

def refresh_player(game_name, tag_line, count=20):
    api = RiotAPI()
    conn = get_conn()

    acct = api.get_account_by_riot_id(game_name, tag_line)
    puuid = acct["puuid"]

    upsert_player(conn, puuid, acct.get("gameName"), acct.get("tagLine"))

    match_ids = api.get_match_ids_by_puuid(puuid, count=count)

    for mid in match_ids:
        m = api.get_match_detail(mid)
        insert_match(conn, m)
        match_id = m["metadata"]["match_id"]

        for p in m["info"]["participants"]:
            # store all participants so you can run cross-player analytics
            upsert_player(conn, p["puuid"], None, None)
            insert_participant_bundle(conn, match_id, p)

    conn.close()
    return puuid, len(match_ids)

if __name__ == "__main__":
    # Your Riot ID from the prompt:
    puuid, n = refresh_player("jinong", "jm7", count=20)
    print("done:", puuid, "matches:", n)
