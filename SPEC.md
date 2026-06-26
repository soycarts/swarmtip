# swarmtip

An autonomous "playing for a draw" signal swarm. Gemini Flash 3.5 agents watch the
World Cup in real time, work out when teams are incentivised to play for a draw,
estimate the resulting draw probability, and compare it to the live betting market to
flag value bets. World Cup is the demo vertical. The product is generic: verified,
auditable signals from messy real-time information.

The swarm coordinates through a ClickHouse **task ledger**, not a hardcoded loop. Each
agent has a **soul.md** that declares its identity, tools, model, and handoff rules.
There is no blocking approval gate; the swarm posts work and flags to the board for
async human pickup.

---

## 1. Problem and value

Naive models and casual markets price a match on team strength and underweight
**incentive**: when a draw qualifies both teams, both shut up shop and the true draw
probability rises above the priced number. The 2026 format (top 2 of each group plus the
8 best third-placed teams of 12) creates these situations constantly, and they shift
**in-play** as scores elsewhere change the math. The engine detects that incentive,
grounds every input in real sources, and emits a signal only when the reasoning is
auditable. A downstream betting or trading agent pays per signal over an agent payment
rail. The edge is strongest in-play: when a goal elsewhere makes a draw mutually
sufficient, the live draw price lags, and an engine that recomputes the qualification
math instantly can beat the slow line.

## 2. The edge thesis

Classify each match: **mutual_draw** (a draw qualifies both, draw probability elevated,
bet candidate), **one_sided** (one content, one must chase, mild elevation),
**both_must_win** (neither qualifies on a draw, probability suppressed, avoid). Two
regimes: **static** (pre-match, from standings, judge Egypt v Iran now) and **dynamic**
(in-play, recompute on every score update and detect when a team's optimal strategy
**flips** to playing for a draw). The flip is the headline.

## 3. Goals and non-goals

**Goals**: autonomous loop with no approval gate acting on real-time data; correct
qualification reasoning across all 12 groups; in-play flip detection; value signal
(model vs market draw probability with edge); auditable cited brief plus a voiced
briefing; pay-per-signal over x402; a close-to-live swarm board.

**Non-goals**: beating a sharp closing line in production (frame as model vs *this* book,
target soft lines); full FIFA tiebreaker set and live liquidity modelling (future work);
any UI beyond the demo surface.

## 4. Repo structure

```
swarmtip/
├── SPEC.md
├── README.md
├── requirements.txt
├── .env.example
├── config.py                 # model strings, keys, thresholds (EDGE_MIN, etc.)
├── agents.md                 # roster + coordination contract (the team handbook)
├── agents/
│   ├── feed/        soul.md  agent.py
│   ├── context/     soul.md  agent.py
│   ├── strategy/    soul.md  agent.py
│   ├── pricing/     soul.md  agent.py
│   └── publisher/   soul.md  agent.py
├── core/
│   ├── db.py                 # ClickHouse client + queries
│   ├── tasks.py              # ledger API: create / claim / complete / spawn
│   ├── qualification.py      # deterministic engine: Prometheux client + fallback
│   └── prometheux/           # ontology rules
├── db/
│   ├── schema.sql            # domain tables + coordination tables (section 9)
│   └── views.sql             # tasks_current, swarm_board, signal views
├── feeds/
│   ├── live.py               # real score + odds poller
│   ├── sim.py                # scripted feed (same event shape as live)
│   └── timelines/group_g.json
├── integrations/
│   ├── tavily.py  gemini.py  senso.py  elevenlabs.py
│   └── x402_app.py           # FastAPI gated signal endpoint
├── orchestrator.py           # one asyncio process: feed -> spawn tasks -> run agents
├── modal_app.py              # Modal deploy + schedule
└── webapp/                   # AI Studio demo surface: live board, brief, audio
```

`core/qualification.py` is the deterministic engine from the starter `pipeline.py`. The
functions in `pipeline.py` (`ground_fixture`, `derive_qualification`,
`estimate_draw_prob`, `compute_value`) become the **task handlers** the agents run.

## 5. Agent identity: soul.md

Every agent loads its `soul.md` at startup as its system prompt and config. Identity is
declarative and editable, which keeps roles legible and lets Senso ingest the souls as
the swarm's ground truth. Template:

```markdown
# soul.md: <AgentName>

## Identity
One line: who this agent is and its single mandate.

## Mission
The one job it owns and does well.

## Consumes
Task types it claims. Events and tables it reads.

## Produces
Tables and artifacts it writes. Task types it spawns on completion.

## Tools
Allowed tools only: [Tavily | Gemini | QualificationEngine | Senso | ElevenLabs | ClickHouse].

## Model
Primary: gemini-3.5-flash. Escalate to <pro-tier> when: <condition>.

## Operating rules
- Cite every external claim with a source URL.
- Never compute qualification math; call the QualificationEngine tool.
- No blocking gate. File a 'coding' task to the board on a capability gap.
- Idempotent: re-running a claimed task must not double-write.

## Handoff / done
Done when: <criteria>. On done, spawn: <next task type(s)>.
```

Per-agent souls (model routing is heterogeneous, zapflex-style):

- **FeedAgent**: emits `ScoreUpdate{match_id, minute, score, other_match_scores}`. Live
  polls a score source, sim reads a timeline. No model (mechanical). On a new update,
  spawns `assess(match)`.
- **ContextAgent**: claims `ground`. Tavily-pulls squad news, manager quotes, form.
  Writes `sources`. Flash. Cite everything.
- **StrategyAgent**: claims `strategy`. Input: the qualification classification plus
  grounded context plus recent score events. Output: `draw_likelihood`, a
  `play_for_draw` flag, a one-line rationale. **Flash, escalate to a Pro tier** when a
  flip is detected (the high-value reasoning). Spawns `price`.
- **PricingAgent**: claims `price`. De-vig the latest draw odds, compute edge, decide
  `BET_DRAW` / `NO_EDGE` / `AVOID`. Mostly deterministic, Flash for the rationale only.
  Spawns `publish` when `edge >= EDGE_MIN`.
- **PublisherAgent**: claims `publish`. Renders the cited brief (Senso to cited.md),
  triggers an ElevenLabs clip, writes `value_signals.brief_url`. Flash.

`agents.md` holds the roster, the task protocol below, the task-type DAG, the
coordination model, and the no-gate rule.

## 6. Swarm coordination via the task ledger

The orchestrator turns a `ScoreUpdate` into a root task and drives the chain. The DAG per
update:

```
score_update(match)
  └─ assess(match)                      [kind=agent, root]
       ├─ ground(match)        -> ContextAgent
       └─ qualify(match)       -> QualificationEngine (deterministic)
            (when ground + qualify complete)
            └─ strategy(match) -> StrategyAgent
                 └─ price(match) -> PricingAgent
                      └─ publish(match) -> PublisherAgent   (only if edge >= EDGE_MIN)
```

Protocol: a task is `created` with `depends_on`. The orchestrator hands a claimable task
(created, all dependencies completed) to an idle agent. The agent runs the handler, writes
the result, appends `completed`, and spawns the next task. Every transition is one append
to `task_events`.

Implementation, locked: **one orchestrator process running asyncio**. It is the sole
assigner, so no two agents ever contend for the same task and there is no claim race.
In-memory state does the claiming, which is atomic inside a single process, and every
transition mirrors to `task_events` for the board and the audit trail. ClickHouse is the
observability layer, the orchestrator holds coordination, and you need no extra datastore.

If you later want distributed concurrency, reach for Modal: its `Queue` and `Dict`
primitives and concurrency-limited functions handle distribution while ClickHouse stays
the ledger. You do not need it for this build.

The ledger holds two kinds of work in one place. `agent` tasks are the runtime swarm work
above. `coding` tasks are build and capability-gap work, filed by a human or by an agent
that hits a wall. One board shows both lanes, which is the single operational view for the
swarm and replaces the blocking approval gate.

## 7. System overview

```
  live / sim ─▶ FeedAgent ─▶ spawn assess(match) ─▶ ┌─────────────┐
   score feed                                       │ task ledger │ (ClickHouse)
                                                     └──────┬──────┘
   ContextAgent ─claims ground─────────────────────────────┤
   QualificationEngine ─claims qualify─ (Prometheux/fallback)┤
   StrategyAgent ─claims strategy─ (Flash, Pro on flip) ─────┤
   PricingAgent ─claims price─ (edge vs market) ─────────────┤
   PublisherAgent ─claims publish─ Senso→cited.md, ElevenLabs ┘

   swarm_board view ─▶ webapp (live)   One asyncio orchestrator, run on a Modal schedule.
```

## 8. Qualification engine

Given live standings and scores, per team: `draw_points` = current + 1; `secures_top2`
(projected points hold a top-two place); `secures_best_third` (projected third-place
standing ranks top 8 across all 12 groups, compared on points, then goal difference, then
goals scored); `draw_sufficient` = either; then `match_class`. Step 3 is what makes
Prometheux load-bearing: a ranking over derived facts from all 12 groups, recomputed on
each score event, and an LLM gets it wrong. The Python fallback uses a coarse
points-and-GD heuristic so the system runs before Prometheux is wired. Prometheux replaces
it with the full rules and exposes lineage, which is what makes the brief auditable.

## 9. Data model (ClickHouse)

Domain tables are in the starter `schema.sql`: `standings`, `fixtures`, `sources`
(append-only grounding), `odds` (append-only, line moves), `qualification_signals` (engine
output with lineage), `value_signals` (the product output). Add the coordination layer:

```sql
-- Append-only source of truth for all task transitions, both lanes.
CREATE TABLE IF NOT EXISTS task_events (
    event_id    UUID DEFAULT generateUUIDv4(),
    task_id     String,
    ts          DateTime64(3) DEFAULT now64(3),
    event_type  Enum8('created'=1,'claimed'=2,'started'=3,'progress'=4,
                      'completed'=5,'failed'=6,'blocked'=7,'cancelled'=8),
    kind        Enum8('coding'=1,'agent'=2),
    task_type   String,                 -- ground|qualify|strategy|price|publish|dev
    actor       String,                 -- agent name or human handle
    fixture_id  String DEFAULT '',
    depends_on  Array(String) DEFAULT [],
    parent_task String DEFAULT '',
    title       String DEFAULT '',
    payload     String DEFAULT '{}',    -- JSON
    result      String DEFAULT '{}'     -- JSON
) ENGINE = MergeTree
ORDER BY (task_id, ts);

-- Agent liveness, for the board.
CREATE TABLE IF NOT EXISTS heartbeats (
    agent  String,
    ts     DateTime64(3) DEFAULT now64(3),
    status String,                       -- idle | working | <task_id>
    note   String DEFAULT ''
) ENGINE = MergeTree
ORDER BY (agent, ts);
```

```sql
-- views.sql

-- Current state of every task: latest event wins. The close-to-live board.
CREATE VIEW IF NOT EXISTS tasks_current AS
SELECT task_id,
       argMax(kind, ts)       AS kind,
       argMax(task_type, ts)  AS task_type,
       argMax(event_type, ts) AS status,
       argMax(actor, ts)      AS assigned_to,
       argMax(fixture_id, ts) AS fixture_id,
       argMax(depends_on, ts) AS depends_on,
       argMax(title, ts)      AS title,
       argMax(result, ts)     AS result,
       min(ts)                AS created_at,
       max(ts)                AS updated_at
FROM task_events
GROUP BY task_id;

-- Demo board: live moves and who is doing what.
CREATE VIEW IF NOT EXISTS swarm_board AS
SELECT status, kind, task_type, assigned_to, fixture_id, title, updated_at
FROM tasks_current
ORDER BY updated_at DESC;

CREATE VIEW IF NOT EXISTS agent_status AS
SELECT agent, argMax(status, ts) AS status, max(ts) AS last_seen
FROM heartbeats GROUP BY agent;
```

Claimable tasks (`status = 'created'` with all `depends_on` completed) are computed in
`core/tasks.py`, in process, since ClickHouse correlated subqueries are limited.
`tasks_current` is a plain view for hackathon scale; for higher volume make it a
ReplacingMergeTree or a materialized view keyed on `task_id`.

## 10. Run modes

**Live**: FeedAgent polls real scores and odds on a Modal schedule (every 60 to 90 seconds
in-play) and drives the loop autonomously. **Simulation**: FeedAgent reads a scripted
`timelines/group_g.json` of score events and odds snapshots, replaying a final matchday
faster than real time, running the exact same agent code, so the demo is a faithful
preview. Timeline shape:

```json
{ "match_id": "G_EGY_IRN",
  "events": [
    {"t": 0,  "score": "0-0", "other": {"G_NZL_BEL": "0-0"}, "draw_odds": 3.10},
    {"t": 22, "score": "0-0", "other": {"G_NZL_BEL": "1-0"}, "draw_odds": 3.05},
    {"t": 38, "score": "0-0", "other": {"G_NZL_BEL": "1-0"}, "draw_odds": 2.95} ] }
```

## 11. Demo (3 minutes)

**Beat 1, judge it now (static).** Run on today's Group G. Egypt v Iran: Egypt safe and
content with a point, Iran must chase, class `one_sided`, modest draw lean. NZ v Belgium:
both must win, class `both_must_win`, `AVOID` the draw. The counter-example proves the
engine reasons about incentive. (Alex Paulsen on screen.)

**Beat 2, the flip (dynamic, simulated).** Replay the scripted matchday with the
**swarm_board live** on screen. 22': NZ 1-0 Belgium, the board lights up as agents claim
`ground` and `qualify`, Iran's third-place draw path opens. 38': Egypt safe, Iran now has a
live third-place case, StrategyAgent fires **PLAY FOR A DRAW**, draw probability jumps
(illustrative 0.32 to 0.52). PricingAgent: in-play draw odds still imply ~0.34, the line
lags, edge +0.18, signal **BET_DRAW**. Verify the exact qualification numbers against the
live state on the day; probabilities here are illustrative.

**Beat 3, the product.** The cited brief on cited.md (claim, lineage, sources), the
ElevenLabs clip, and a buyer agent paying for the signal over x402.

## 12. Sponsor integrations

| Tool | Role | Fallback | Prize |
|---|---|---|---|
| ClickHouse | Store, task ledger, live board | build first | $1k cash + credits |
| Tavily | Grounding, sources behind cited.md | near-mandatory | credits |
| Gemini (DeepMind) | Agent model, heterogeneous routing | n/a | your credits |
| Prometheux | Qualification engine + lineage | Python heuristic | £45k credits + £1.5k, 3 categories |
| Senso | Publish cited.md, ingest soul.md/agents.md as ground truth | local cited.md | 2k credits |
| ElevenLabs | Voiced brief | skip | your credits |
| x402 / CDP | Pay-per-signal endpoint | log the signal | satisfies "monetize" |
| Modal | Scheduled loop, future concurrency | local cron | autonomy axis |

Get the Prometheux mentor for 20 minutes for the ClickHouse connection snippet and a rule
deriving `draw_points` and `draw_sufficient`. Confirm the cited.md publish flow with Senso.
Confirm the x402 facilitator (CDP free tier, Base testnet).

## 13. Build phases (time-boxed)

1. `schema.sql` plus the coordination tables and views. Seed the final-round groups. Run
   the starter `pipeline.py` to confirm a strong mutual-draw fixture is in the demo window.
2. Agents over the fallback engine, wired as a **linear orchestrator first** (handlers call
   each other), static mode end to end.
3. Refactor to the task ledger, still one asyncio process, so the **swarm_board** shows
   live coordination. This is the Presentation win, lock it once the linear flow works.
4. Simulation harness and `group_g.json`.
5. Prometheux replaces the fallback (mentor).
6. cited.md via Senso, then ElevenLabs, then x402 last.
7. Modal schedule for live mode and the autonomy claim.

Cut without hesitation: any approval gate, UI beyond the board plus cited.md plus audio,
multi-group batching polish, the buy-side x402 call.

## 14. Acceptance criteria

- **Idea**: pitched as a generic verified-signal engine, football as the demo.
- **Technical**: qualification math correct (validate against a hand-worked group), live
  and sim share one code path, agents coordinate through the ledger.
- **Tool Use**: ClickHouse (store + ledger + board), Tavily, Gemini, Prometheux load-bearing.
- **Presentation**: three beats inside 3 minutes, the flip legible, the board live.
- **Autonomy**: the loop runs on a schedule against current data with no human in the path.

## 15. Notes for Google AI Studio

Build the agent handlers and the demo surface as the AI Studio app: a page that streams the
`swarm_board`, the qualification recompute, the strategy flip, the edge, the cited brief,
and the audio. Call ClickHouse, Prometheux, Senso, and the x402 endpoint as external
services. Keep the qualification engine deterministic and outside the LLM. Keep model
strings and keys in `config.py`.