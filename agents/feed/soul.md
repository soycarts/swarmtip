# soul.md: FeedAgent

## Identity
The pacemaker of the swarm. It reads score updates and odds changes, driving the autonomous loop.

## Mission
To ingest live or simulated match timelines and trigger the swarm's analysis loop by spawning `assess` tasks.

## Consumes
Live API feeds or simulated timeline JSONs (`group_g.json`).

## Produces
Rows in the `odds` table. Root `assess` tasks in the `task_events` ledger.

## Tools
ClickHouse, `core.tasks`. No LLM.

## Model
None. Mechanical.

## Operating rules
- Never run qualification math.
- Update odds in ClickHouse.

## Handoff / done
Done when the timeline ends or the process is stopped. On each event, spawn: `assess`.
