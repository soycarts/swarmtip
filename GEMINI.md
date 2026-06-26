# gemini.md

Context for agentic tools (Antigravity, Gemini CLI) working on **swarmtip**.

swarmtip is an autonomous "playing for a draw" signal swarm for the 2026 World Cup.
Gemini Flash 3.5 agents read live standings, work out when teams are incentivised to play
for a draw, and price that against the market to flag value bets. Full design is in
`SPEC.md`. The runtime roster and the coordination contract are in `agents.md`.

## The one rule you must not break: log to the task ledger

Every actor that does work on this project logs it to the canonical ClickHouse ledger,
`task_events`. That includes you. This is what makes the autonomous project observable:
one live view of every dev task and every runtime task. Work that is not logged is
invisible to the rest of the swarm.

Three operations, every time:

1. **Starting** a piece of work: open a task.
2. **Finishing** it: close the task.
3. **Handing off**: assign a follow-up task to another actor.

Use the CLI (implemented in `core/tasks.py`):

```bash
# open a task, prints a TASK_ID
python -m core.tasks start --actor antigravity --kind coding --type dev \
  --title "implement core/tasks.py"

# close it when done
python -m core.tasks done <TASK_ID> --actor antigravity --result '{"note":"done"}'

# hand off: create a task for another actor, optionally after this one
python -m core.tasks assign --to claude-code --kind coding --type wire \
  --title "wire ElevenLabs in integrations/elevenlabs.py" --after <TASK_ID>

# see open work and the live board
python -m core.tasks list
```

Bootstrap, before `core/tasks.py` exists, insert directly:

```bash
clickhouse client --query "INSERT INTO task_events
  (task_id, event_type, kind, task_type, actor, title)
  VALUES ('bootstrap-tasks-py','started','coding','dev','antigravity','implement core/tasks.py')"
```

Your `--actor` is your tool name: `antigravity`, `cursor`, or `claude-code`. Runtime agents
use their own names (`feed`, `context`, `strategy`, `pricing`, `publisher`, `orchestrator`).

## How to find work

`python -m core.tasks list` shows open tasks. Read `tasks_current` and `swarm_board` in
ClickHouse for the live state. Pick up `coding` tasks; leave `agent` tasks to the runtime
swarm.

## Working rules

- The qualification engine (`core/qualification.py`) is deterministic. Never let an LLM
  compute standings or best-third math; it gets it wrong. Call the engine.
- No blocking human approval gate. If you need a human or another agent, file a task to the
  board and keep moving.
- Cite every external claim with a source URL.
- Keys and model strings live in `config.py`. Do not hardcode them.
- Task handlers are idempotent: re-running a claimed task must not double-write.

## Stack and layout

Python, ClickHouse (store, ledger, board), Tavily (grounding), Gemini Flash 3.5 (agents),
Prometheux (qualification reasoning), Senso (cited.md), ElevenLabs (voice), x402 (payment),
Modal (schedule). One asyncio orchestrator is the sole task assigner. Repo map is in
`agents.md` and `SPEC.md` section 4.