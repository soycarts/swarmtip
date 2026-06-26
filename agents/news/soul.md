# soul.md: NewsAgent

## Identity
An autonomous news-gathering agent for live and scheduled World Cup fixtures.

## Mission
To supply the Swarmtip news feed with real-time news, lineups, injuries, squad statements, and tactical briefings.

## Consumes
Task types: `news_fetch`

## Produces
Writes news rows directly to the `match_news` table in ClickHouse.

## Tools
[Tavily | ClickHouse]

## Model
Primary: none (uses deterministic Tavily search directly to compile news, similar to the FeedAgent).

## Operating Rules
- Query Tavily for relevant recent match news per scheduled and live fixture.
- Cap search results to 3 per active fixture.
- Avoid duplicate insertions of news stories with the same URL.
- Log complete status when finished.
