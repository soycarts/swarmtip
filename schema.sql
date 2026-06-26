-- ============================================================
-- swarmtip: ClickHouse schema (build step 1)
-- Data flow: standings + fixtures  ->  grounded sources + odds
--            ->  qualification_signals (Prometheux / fallback)
--            ->  value_signals (the product output -> cited.md)
-- ============================================================

-- Current group-stage standings. One row per team, latest wins.
CREATE TABLE IF NOT EXISTS standings (
    group_id     String,
    team         String,
    played       UInt8,
    points       UInt8,
    goal_diff    Int16,
    goals_for    UInt16,
    goals_against UInt16,
    position     UInt8,                 -- current rank within the group
    updated_at   DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (group_id, team);

-- Remaining fixtures to analyse.
CREATE TABLE IF NOT EXISTS fixtures (
    fixture_id   String,                -- e.g. 'G_NZL_BEL'
    group_id     String,
    home_team    String,
    away_team    String,
    kickoff      DateTime,
    status       String DEFAULT 'scheduled',  -- scheduled | live | finished
    updated_at   DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY fixture_id;

-- Grounding evidence from Tavily. Append-only (your raw_events instinct).
-- Every claim the engine makes should trace back to a row here.
CREATE TABLE IF NOT EXISTS sources (
    fixture_id   String,
    query        String,
    url          String,
    title        String,
    snippet      String,
    fetched_at   DateTime DEFAULT now()
) ENGINE = MergeTree
ORDER BY (fixture_id, fetched_at);

-- Market odds per fixture. Append-only so you can watch the line move.
CREATE TABLE IF NOT EXISTS odds (
    fixture_id   String,
    bookmaker    String,
    home_odds    Float32,
    draw_odds    Float32,
    away_odds    Float32,
    fetched_at   DateTime DEFAULT now()
) ENGINE = MergeTree
ORDER BY (fixture_id, fetched_at);

-- Qualification reasoning, per team per fixture.
-- Written by Prometheux (preferred) or the Python fallback in pipeline.py.
CREATE TABLE IF NOT EXISTS qualification_signals (
    fixture_id     String,
    team           String,
    draw_points    UInt8,     -- projected points for this team if the match is drawn
    draw_sufficient UInt8,    -- 1 if a draw likely secures qualification
    path           String,    -- 'top2' | 'best_third' | 'none'
    reasoning      String,    -- human-readable derivation / lineage summary
    source         String DEFAULT 'fallback',  -- 'prometheux' | 'fallback'
    derived_at     DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(derived_at)
ORDER BY (fixture_id, team);

-- Final value signal per fixture. This is what you sell over x402
-- and render to cited.md.
CREATE TABLE IF NOT EXISTS value_signals (
    fixture_id       String,
    match_class      String,   -- 'mutual_draw' | 'one_sided' | 'both_must_win'
    model_draw_prob  Float32,  -- engine's estimate
    market_draw_prob Float32,  -- de-vigged 1/draw_odds
    edge             Float32,  -- model_draw_prob - market_draw_prob
    recommendation   String,   -- 'BET_DRAW' | 'NO_EDGE' | 'AVOID'
    brief_url        String,   -- cited.md link
    created_at       DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(created_at)
ORDER BY fixture_id;