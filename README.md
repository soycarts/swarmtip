# swarmtip

A swarm that finds underpriced **draws** at the 2026 World Cup. It reads live standings,
works out which teams qualify on a draw (so a draw is mutually convenient), grounds every
claim in real sources, and prices that against the market to flag value bets. NZ vs Belgium
is the built-in counter-example: both teams must win, so the engine says **avoid the draw**
there.

## What's here (build steps 1 and 2)

- `schema.sql`: ClickHouse tables. The spine of everything.
- `pipeline.py`: end-to-end skeleton, ground then qualify then analyse then value signal.
  Runs today with a Python fallback for the qualification logic.

## Run order

1. `clickhouse client < schema.sql` (or paste into the Cloud console).
2. Seed `standings` and `fixtures` (Tavily, a stats page, or hand-enter the final-round
   groups to start, it is only ~12 groups).
3. Seed `odds` with a draw price per fixture from any public odds page.
4. `pip install clickhouse-connect tavily-python google-genai`
5. Export `CLICKHOUSE_*`, `TAVILY_API_KEY`, `GEMINI_API_KEY`.
6. `python pipeline.py` for ranked fixtures by draw edge.

## Implemented Prometheux Logic Measures

Our logic-based, deterministic qualification engine implements the following four core declarative ontology measures (defined in `core/prometheux/ontology.dlog` and executed in `core/qualification.py`):

1. **Draw Points Projection (`projected_points(T, F, P)`)**
   - **Logic**: `standings(T, CurrentP), P = CurrentP + 1`
   - **Description**: Calculates the team's tournament points if the match under analysis ends in a draw.

2. **Guaranteed Top-2 Finish (`secures_top2(T, F)`)**
   - **Logic**: `projected_points(T, F, P), group_scenario_min_position(T, F, Pos), Pos <= 2`
   - **Description**: Evaluates all $3^N$ scenario permutations of sibling fixtures to guarantee the team finishes in the top 2 places of their group stage.

3. **Best-Third Qualification (`secures_best_third(T, F)`)**
   - **Logic**: `group_scenario_min_position(T, F, 3), (P >= 4 || (P == 3, goal_difference(T, GD), GD >= 0))`
   - **Description**: Verifies if a 3rd-place finish guarantees progression, requiring either $\ge 4$ points, or exactly 3 points with a non-negative goal difference.

4. **Draw Sufficiency (`draw_sufficient(T, F)`)**
   - **Logic**: `secures_top2(T, F) || secures_best_third(T, F)`
   - **Description**: Aggregates rules to flag if a draw is mathematically sufficient for World Cup round-of-32 qualification.

## Where each sponsor tool plugs in

- **ClickHouse**: store, the task ledger, the live board. Already the spine.
- **Tavily**: `ground_fixture()`. Grounding plus the source rows behind `cited.md`.
- **Gemini (DeepMind)**: `estimate_draw_prob()`. Flash for the swarm, route only this
  analysis step to a Pro tier if it needs more reasoning.
- **Prometheux**: replaces `derive_qualification()`. Real cross-group top-2 plus best-third
  reasoning over the `standings` table, with lineage written to `qualification_signals`.
  This is the prize move. Get the mentor for 20 min: ask for the ClickHouse connection
  snippet and a minimal rule that derives `draw_points` and `draw_sufficient`.
- **Senso**: `write_cited_md()`. Publish the brief through the Senso CLI so `cited.md` is
  satisfied properly and you bank Best Use of Senso. Confirm the publish flow on site.
- **ElevenLabs**: voice the final ranked brief. Run after `cited.md` is written.
- **x402**: one FastAPI endpoint that serves the `value_signals` brief, gated by the CDP
  facilitator. Do it last.

## Coordination and autonomy

One asyncio orchestrator is the sole task assigner, so there is no claim race and no extra datastore is needed. ClickHouse holds the append-only task ledger and the live board.

The loop runs end-to-end autonomously with **four core architectural pillars** implementing timezone-aware scheduling, external grounding, and data consistency:

### 1. NewsAgent (Hourly Match News Crawler)
- **Role**: `news_gatherer` (`NewsAgent`) claims `news_fetch` tasks triggered autonomously at the start of each hour.
- **Action**: Performs live, advanced Tavily searches for all scheduled and live matches to crawl squad previews, injury updates, and predicted lineups.
- **Consistency**: Applies an URL-based duplicate filter to discard already ingested stories before inserting into the `match_news` ClickHouse table.
- **Consumption**: The `StrategyAgent` prompt context queries both historical grounding `sources` and the newly updated `match_news` table to base draw evaluations on real-time news.

### 2. KickoffAgent (Dynamic Kickoff Verification)
- **Role**: `kickoff` (`KickoffAgent`) claims `research_kickoff` tasks.
- **Action**: Researches official World Cup 2026 fixture times on-demand using Tavily and uses Gemini to verify and extract official kickoff times into a strict `YYYY-MM-DD HH:MM:00` UTC format, updating the central database.

### 3. Timezone-Aware UTC Orchestration
- **Action**: Orchestrates all loop executions and state tracking using timezone-aware UTC timestamps (`datetime.now(timezone.utc)`).
- **Match Status Transitions**: Dynamically calculates and transitions matches from `scheduled` &rarr; `live` &rarr; `finished` depending on real UTC time versus verified kickoff.
- **In-Play Elapsed Minute Tracking**: Translates active in-play times into actual elapsed minutes and injects them into regular live assessments (e.g., `"minute": 66`), which are displayed in real-time.

### 4. ClickHouse ReplacingMergeTree & argMax Resolve
- **Action**: Maintains absolute consistency across append-only tables (like `fixtures`). Since entries can be updated with new statuses or kickoffs, the API resolves the latest state of each fixture on-demand using high-performance `argMax(field, updated_at)` aggregations grouped by `fixture_id`:
```sql
SELECT fixture_id,
       argMax(group_id, updated_at) AS group_id,
       argMax(home_team, updated_at) AS home_team,
       argMax(away_team, updated_at) AS away_team,
       argMax(kickoff, updated_at) AS kickoff,
       argMax(status, updated_at) AS status
FROM fixtures
GROUP BY fixture_id
```

No approval gate is needed: the loop runs end-to-end, writing state to the ClickHouse ledger and instantly updating the live dashboard.


## Build order (4 hours)

1. Schema plus the coordination tables and seed (you're here).
2. Confirm a strong mutual-draw fixture is in the demo window, run the spine and look at
   the ranking. If today's groups are thin, seed June 27 and 28 finishers too.
3. Agent loop on Gemini Flash, then refactor to the task ledger for the live board.
4. Prometheux over ClickHouse (mentor pairing).
5. `cited.md` via Senso.
6. ElevenLabs on the brief.
7. x402 endpoint.
8. Modal scheduled loop.

Cut without hesitation: any approval gate, UI beyond the board plus `cited.md` plus audio,
multi-group batching polish, the buy-side x402 call.