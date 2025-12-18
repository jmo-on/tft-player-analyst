CREATE DATABASE IF NOT EXISTS tftdb;
USE tftdb;

CREATE TABLE IF NOT EXISTS players (
  puuid VARCHAR(90) PRIMARY KEY,
  game_name VARCHAR(64),
  tag_line VARCHAR(16),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS matches (
  match_id VARCHAR(32) PRIMARY KEY,
  game_datetime BIGINT,
  game_length FLOAT,
  tft_set_number INT,
  tft_game_type VARCHAR(32),
  queue_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS participants (
  match_id VARCHAR(32) NOT NULL,
  puuid VARCHAR(90) NOT NULL,
  placement INT,
  level INT,
  last_round INT,
  players_eliminated INT,
  total_damage_to_players INT,
  PRIMARY KEY (match_id, puuid),
  FOREIGN KEY (match_id) REFERENCES matches(match_id),
  FOREIGN KEY (puuid) REFERENCES players(puuid)
);

CREATE TABLE IF NOT EXISTS participant_traits (
  match_id VARCHAR(32) NOT NULL,
  puuid VARCHAR(90) NOT NULL,
  trait_name VARCHAR(64) NOT NULL,
  tier_current INT,
  num_units INT,
  style INT,
  PRIMARY KEY (match_id, puuid, trait_name),
  FOREIGN KEY (match_id, puuid) REFERENCES participants(match_id, puuid)
);

CREATE TABLE IF NOT EXISTS participant_units (
  match_id VARCHAR(32) NOT NULL,
  puuid VARCHAR(90) NOT NULL,
  character_id VARCHAR(64) NOT NULL,
  tier INT,
  rarity INT,
  PRIMARY KEY (match_id, puuid, character_id),
  FOREIGN KEY (match_id, puuid) REFERENCES participants(match_id, puuid)
);

CREATE TABLE IF NOT EXISTS participant_augments (
  match_id VARCHAR(32) NOT NULL,
  puuid VARCHAR(90) NOT NULL,
  augment_id VARCHAR(96) NOT NULL,
  PRIMARY KEY (match_id, puuid, augment_id),
  FOREIGN KEY (match_id, puuid) REFERENCES participants(match_id, puuid)
);

CREATE INDEX idx_participants_puuid ON participants(puuid);
CREATE INDEX idx_traits_trait_name ON participant_traits(trait_name);
CREATE INDEX idx_units_character_id ON participant_units(character_id);
