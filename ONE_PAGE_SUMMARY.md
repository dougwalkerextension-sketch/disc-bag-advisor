# Disc Bag Advisor — one-page summary

**Purpose.** Fieldwork recommends possible additions to a disc golf bag from a named disc, multiple reference discs, or a category such as “understable fairway driver.” It supports strict brand preferences, flight-number comparisons, sort options, official source links, manufacturer imagery, and a browser-saved bag.

**Experience.** A responsive desktop/mobile UI offers sample searches, flight-number cards, manufacturer details, and add/remove bag actions. Sorting includes best match, speed, name, and popularity based on actual detail selections on this installation. Bagged discs are excluded from new recommendations.

**Refine a search.** Shift toward more overstable, more understable, faster, or slower discs relative to the leading result. Preferences remain active. Slower is hidden at speed 1 and Faster at speed 14. Empty shifts preserve current results. Refinements execute through MCP and appear in the run trace.

**MCP and framework.** Python/FastAPI serves the UI. A custom asyncio orchestrator uses the official MCP Python SDK and FastMCP over stdio. Local Ollama/Mistral selects search and rank tools and observes results. The host enforces preferences and candidate identity. Four model turns and explicit deadlines bound work. If the model fails, a clearly identified deterministic MCP workflow handles supported searches. AGENT_FRAMEWORK.md documents decisions, controls, retries, and the execution graph.

**Recovery.** Invalid input and unknown discs receive controlled errors. Tool/model outages produce recovery messages; read calls retry once, selection increments never retry. Manufacturer fetching uses fixed official URLs, an HTTPS allowlist, bounded redirects, timeout/size limits, one-day cache, and stale fallback. Missing/blocked images preserve recommendations and an official-page link. Browser image failures receive a recovery message; the saved bag persists.

**Records and checks.** WORK_LOG.md records implementation and investigations. Every application run writes a UUID-linked JSON record with its query, mode, results, trace, and timing; SQLite stores popularity and cached image URLs. Nine automated tests passed, including real MCP transport and failure paths. Headless Edge checks passed on desktop/mobile with bag persistence and no JavaScript errors. Live manufacturer verification covered Innova image success and Latitude 64 rate-limit recovery. Mistral also successfully selected search and rank through MCP.

**Scope and launch.** The starter catalog contains 24 discs from Innova, Latitude 64, MVP, Axiom, Discraft, Discmania, and Streamline. Flight data is curated seed data; recommendations are comparisons, not personal flight guarantees. Popularity is local, not global sales. Install requirements.txt and run python app.py, then visit http://127.0.0.1:8010. The original workspace also supports ./start.ps1. Ollama with mistral:7b enables model mode. This is a local single-user app; internet hosting needs a Python-capable deployment. Source destination: https://github.com/dougwalkerextension-sketch/disc-bag-advisor.

Brand preferences follow sorting in the sidebar. Five popular defaults use OTB’s 2025 retail sales ranking, with Show more revealing all seven catalog brands. Collapsed selections stay active.
