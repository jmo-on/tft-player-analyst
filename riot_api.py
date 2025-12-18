import os
import time
import requests

class RiotAPI:
    def __init__(self):
        self.api_key = os.getenv("RIOT_API_KEY")
        self.region = os.getenv("RIOT_REGION")

    def _get(self, url, params=None):
        headers = {"X-Riot-Token": self.api_key}
        while True:
            r = requests.get(url, headers=headers, params=params, timeout=10)
            if r.status_code == 429:
                time.sleep(2)
                continue
            r.raise_for_status()
            return r.json()

    # 1) Riot ID -> Account (gives puuid)
    def get_account_by_riot_id(self, game_name, tag_line):
        url = f"https://{self.region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        return self._get(url)

    # 2) puuid -> match ids (TFT match history is regional routing) :contentReference[oaicite:9]{index=9}
    def get_match_ids_by_puuid(self, puuid, count=20):
        url = f"https://{self.region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids"
        return self._get(url, params={"count": count})

    # 3) match id -> match detail
    def get_match_detail(self, match_id):
        url = f"https://{self.region}.api.riotgames.com/tft/match/v1/matches/{match_id}"
        return self._get(url)
