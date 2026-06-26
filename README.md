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

One asyncio orchestrator is the sole task assigner, so there is no claim race and no extra
datastore is needed. ClickHouse holds the append-only task ledger and the live board.
Deploy the orchestrator on a Modal schedule so it pulls genuinely current data during the
4:30 demo. No approval gate, the loop runs end to end and posts work to the board.

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