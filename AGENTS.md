# agents.md

How agents work on and within **swarmtip**. Cursor, Claude Code, and other AGENTS.md-aware
tools read this. Antigravity and Gemini tools read `gemini.md`, which points here. Full
system design is in `SPEC.md`.

There are two kinds of agent in this project:
- **Coding agents**: Antigravity, Cursor, Claude Code, and humans, building the codebase.
- **Runtime agents**: the swarm that runs the product (the roster in section 3).

Both log to the same canonical ledger, so one board shows everything happening.

## 1. The canonical task ledger (read this first)

The source of truth is the append-only ClickHouse table `task_events`. Current state is the
`tasks_current` view, and the live board is `swarm_board`. Because it is append-only, every
operation is an insert.

**Every actor logs three operations:**

| Operation | When | Event written |
|---|---|---|
| Start | you begin a task | `started` (or `created` for a brand-new task) |
| Close | you finish a task | `completed` (or `failed` / `cancelled`) |
| Assign | you hand a task to another actor | a new task `created` for them, `depends_on` the current task if sequential |

CLI (implemented in `core/tasks.py`):

```bash
python -m core.tasks start  --actor <name> --kind <coding|agent> --type <type> --title "..."
python -m core.tasks done   <task_id> --actor <name> [--result '<json>']
python -m core.tasks assign --to <name> --kind <coding|agent> --type <type> --title "..." [--after <task_id>]
python -m core.tasks list   [--open | --mine <name> | --board]
```

Programmatic API for the runtime swarm, same ledger:

```python
from core.tasks import create, claim, complete, spawn

tid = create(kind="agent", task_type="strategy", fixture_id=fx,
             depends_on=[ground_id, qualify_id])
claim(tid, actor="strategy")
complete(tid, actor="strategy",
         result={"draw_likelihood": 0.52, "play_for_draw": True})
spawn(parent=tid, kind="agent", task_type="price", fixture_id=fx)
```

Fields: `kind` is `coding` (dev work) or `agent` (runtime work). `task_type` is a short
label: for coding use `dev` / `fix` / `wire` / `infra`; for runtime use `ground` /
`qualify` / `strategy` / `price` / `publish`. `actor` is the tool or agent name. The full
row is in `db/schema.sql`.

Actors: `antigravity`, `cursor`, `claude-code`, `orchestrator`, `feed`, `context`,
`strategy`, `pricing`, `publisher`.

## 2. Coordination model

One asyncio process (`orchestrator.py`) is the **sole assigner** of runtime tasks. It reads
claimable tasks (status `created`, all `depends_on` completed) and hands each to an idle
agent. Agents append `claimed` then `completed` and spawn the next task. Because one process
assigns, no two agents contend for the same task and there is no claim race. ClickHouse
holds the ledger and the board, and the orchestrator handles assignment. If you later need
distributed concurrency, use Modal `Queue` and concurrency-limited functions; it is not
needed now.

Runtime DAG per score update:

```
score_update(match) -> assess(match)
  ├─ ground(match)    [context]
  └─ qualify(match)   [QualificationEngine, deterministic]
       -> strategy(match)  [strategy]
            -> price(match)     [pricing]
                 -> publish(match)  [publisher]   (only if edge >= EDGE_MIN)
```

## 3. Runtime roster

Each agent has a `soul.md` under `agents/<name>/` that is its system prompt. Model routing
is heterogeneous: Flash for most, a Pro tier for the StrategyAgent on a detected flip.

- **feed**: emits score updates (live poll or scripted sim), spawns `assess`. No model.
- **context**: claims `ground`, Tavily-pulls squad news and form, writes `sources`. Flash.
- **QualificationEngine**: claims `qualify`. Deterministic engine (Prometheux with a Python
  fallback). Writes `qualification_signals` with lineage. Wrapped as a tool, never an LLM.
- **strategy**: claims `strategy`, turns the qualification class plus context into a
  `draw_likelihood` and a `play_for_draw` flag. Flash, Pro on a flip. Spawns `price`.
- **pricing**: claims `price`, de-vigs the draw odds, computes edge, decides
  BET_DRAW / NO_EDGE / AVOID. Mostly deterministic. Spawns `publish` if `edge >= EDGE_MIN`.
- **publisher**: claims `publish`, writes the cited brief (Senso to cited.md), voices it
  (ElevenLabs), fills `value_signals.brief_url`. Flash.

## 4. Working rules (all agents, coding and runtime)

- Never let an LLM compute qualification math. Call `core/qualification.py`.
- No blocking approval gate. File a task to the board instead.
- Cite every external claim with a source URL.
- Keys and model strings live in `config.py`.
- Handlers are idempotent: a re-run must not double-write.
- Log start, close, and assign for every task (section 1). No silent work.

## 5. Repo map

See `SPEC.md` section 4. Key paths: `core/tasks.py` (ledger API and CLI),
`core/qualification.py` (deterministic engine), `orchestrator.py` (the asyncio loop),
`agents/<name>/soul.md` (agent identities), `db/schema.sql` and `db/views.sql` (the ledger
and board).