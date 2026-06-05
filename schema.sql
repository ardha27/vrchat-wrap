-- VRChat Wrap — D1 leaderboard schema
-- Run: npx wrangler d1 execute vrcwrap-lb --file=schema.sql

CREATE TABLE IF NOT EXISTS leaderboard (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  username        TEXT    NOT NULL,
  username_lower  TEXT    NOT NULL,
  hours           REAL    NOT NULL DEFAULT 0,
  worlds          INTEGER NOT NULL DEFAULT 0,
  people_met      INTEGER NOT NULL DEFAULT 0,
  friends_added   INTEGER NOT NULL DEFAULT 0,
  solo_pct        INTEGER NOT NULL DEFAULT 0,
  one_time_people INTEGER NOT NULL DEFAULT 0,
  unfriended      INTEGER NOT NULL DEFAULT 0,
  empty_hours     REAL    NOT NULL DEFAULT 0,
  role_code       TEXT    DEFAULT '',
  role_name       TEXT    DEFAULT '',
  submitted_at    TEXT    NOT NULL DEFAULT (datetime('now')),
  UNIQUE(username_lower)
);

CREATE INDEX IF NOT EXISTS idx_hours           ON leaderboard(hours DESC);
CREATE INDEX IF NOT EXISTS idx_worlds          ON leaderboard(worlds DESC);
CREATE INDEX IF NOT EXISTS idx_people_met      ON leaderboard(people_met DESC);
CREATE INDEX IF NOT EXISTS idx_friends_added   ON leaderboard(friends_added DESC);
CREATE INDEX IF NOT EXISTS idx_solo_pct        ON leaderboard(solo_pct DESC);
CREATE INDEX IF NOT EXISTS idx_one_time_people ON leaderboard(one_time_people DESC);
CREATE INDEX IF NOT EXISTS idx_unfriended      ON leaderboard(unfriended DESC);
CREATE INDEX IF NOT EXISTS idx_empty_hours     ON leaderboard(empty_hours DESC);
