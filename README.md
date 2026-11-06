# Disc Bag Advisor · Fieldwork

A responsive disc golf recommendation app using an OpenAI agent and real MCP tools. Search by one disc, multiple references, or a flight category; filter brands; sort by match, local popularity, speed, or name; inspect manufacturer imagery; save a bag in your browser.

## Run

Requires Python 3.11+ (tested with 3.12). From this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:8010**. On this Windows installation, DiscBag includes its own portable Python 3.12 runtime and packages under `.runtime/`. Launch with `./start.cmd` or the VS Code **Start Disc Bag Advisor** task. F5 uses this local runtime and requires the Python debugger extension. `start.ps1` is also available. Both launchers prefer a local `.venv` if present, otherwise use only this folder's `.runtime`. No sibling project folder is used.

The portable runtime is an independent copy of Python's base files with freshly installed packages; its configuration and imports point only inside DiscBag. It is ignored by Git, so a fresh GitHub checkout should follow the virtual-environment setup above. When using `.venv`, select its Python interpreter in VS Code. To install optional browser test and debugger dependencies, run `python -m pip install -r requirements-dev.txt` with your selected local interpreter. Browser tests use installed Edge and the Playwright package from that interpreter.

## OpenAI configuration

Copy `.env.example` to `.env` and set `OPENAI_API_KEY` in this folder, or set it in the server environment. The default `OPENAI_MODEL` is `gpt-5-mini`; choose another compatible function-calling model if needed. Set `DISC_AGENT_ENABLED=false` to use only catalog tools. Configuration is read for each search. No Ollama service or local model is used.

OpenAI chooses tools through the [Responses API function-calling loop](https://developers.openai.com/api/docs/guides/function-calling). The server calls only `https://api.openai.com/v1/responses`, uses `store: false`, and keeps function results plus encrypted reasoning items in memory between calls. Queries and catalog observations are sent to OpenAI. The API key stays server-side, is not returned to the browser, and `.env` is ignored by Git. Never paste keys into the UI or commit them. API usage is billed to the configured OpenAI account.

Missing keys, authentication failures, quotas, network issues, malformed tool calls, and timeouts return clearly labeled catalog fallback results; there is no local LLM fallback. Directional shifts continue to use deterministic MCP tools directly. The trace reports `openai-model`, `bounded-fallback`, `bounded-workflow` (explicitly disabled), or `bounded-shift`.


## Use and catalog scope

- `Similar to Leopard3` compares flight numbers and excludes the reference disc.
- `Similar to River and Crave` averages distance from up to three named references.
- `understable fairway driver`, `stable midrange`, `overstable distance driver`, or `putter` filter by flight category.
- Selected brands are strict filters. Leave unchecked to include all brands.
- Sorting appears above brand preferences. The default brand list shows Innova, Axiom, Discraft, Discmania, and MVP, based on [The DiscList's published manufacturer ranking](https://thedisclist.com/brands/) dated October 16, 2026, which combines retail availability and market signals rather than measuring sales. **Show more** reveals every remaining catalog brand. No brand is checked by default. Collapsing the list retains filters and reports hidden selections on the button. Available brands come from the catalog API and are validated against the same catalog registry.
- After a search, use **More overstable**, **More understable**, **Faster**, or **Slower** to shift from the leading displayed result. The reference name, speed, and turn + fade appear beside the controls. Each click searches the catalog through MCP, preserves current brand/sort/bag preferences, and requires strictly higher/lower speed or stability. Speed shifts may cross disc categories. Slower is hidden at speed 1; Faster is hidden at speed 14. Empty shifts retain the current results. Changing sort preserves the latest shift; submitting a search starts fresh.
- Open a result for manufacturer imagery and add it to your bag. Bagged discs are excluded from subsequent searches; **My bag** allows removal.

The starter catalog has **37 discs across 20 manufacturers**. Flight numbers are source-linked curated seed data, not a complete or continuously refreshed database. Similarity uses weighted flight-number distance. Stability categories use turn + fade: understable < 0; stable >= 0 and < 2; overstable >= 2. This application heuristic is not a universal manufacturer standard. Weight, plastic, wear, power, and release affect actual flight.

Popularity means **detail-card selections on this installation**, stored in SQLite. It is not global sales. Fresh installations start at zero; ties use match score then name. Adding to a bag does not itself increment popularity.

## MCP and agent framework

The official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) supplies ClientSession, stdio transport, and FastMCP. A custom asyncio orchestrator manages an OpenAI Responses function-calling loop and dispatches those calls to real MCP tools. It does not use LangGraph or the separate FastMCP v2 package. See [AGENT_FRAMEWORK.md](AGENT_FRAMEWORK.md) for the execution graph and controls.

External MCP hosts can launch the same tools using their actual Python executable and absolute path:

```json
{"mcpServers":{"disc-bag-tools":{"command":"C:/path/to/.venv/Scripts/python.exe","args":["C:/path/to/disc-bag-advisor/tools_server.py"]}}}
```

Tools are `search_discs`, `rank_discs`, `manufacturer_image`, and `record_selection`. Recommendation and detail endpoints create real MCP sessions; they do not shortcut to in-process domain calls. `/api/catalog` is a read-only UI bootstrap.

## Recovery and records

Invalid input receives 422, unknown discs 404, and tool outages a friendly 503. Browser requests time out after 70 seconds; model planning after 40 seconds; the workflow after 65 seconds. Read tools retry once, selection increments never retry. Failed searches retain previous visible results and saved bags.

Manufacturer requests use fixed HTTPS source URLs, a hostname allowlist, bounded redirects, two MB page limits, eight-second network timeouts, one-day image URL caching, and stale-cache fallback. Missing metadata, rate limits, hotlink restrictions, and browser image failures show recovery messages with an official-page link. Metadata can occasionally identify a promotional image; review imagery when expanding the catalog.

`runtime/` stores SQLite popularity/image-cache data and one JSON file per agent run, including the original query, preferences, results, mode, run ID, statuses, and timings. Bag contents stay in this browser. Logs can contain search text; stop the app and delete `runtime/` to reset history/cache/popularity. Runtime data, screenshots, environments, and credentials are excluded from source publication.

The server binds to localhost with host/origin checks. This is a single-user app. Internet hosting requires a Python-capable service plus deployment-specific authentication, limits, and persistence. The Python/stdio backend cannot run on static GitHub Pages or directly in Sites' Cloudflare Worker runtime. No hosted deployment is claimed.

## Checks and handoff

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tests/check_model.py
```

The first command runs offline checks including real MCP transport. The second verifies live OpenAI tool calling (uses the configured API key and incurs API usage). `tests/browser_check.py`, `tests/browser_shift_check.py`, and `tests/browser_sidebar_check.py` use installed Edge and locally installed Playwright; no external project paths are added. See [WORK_LOG.md](WORK_LOG.md) and [ONE_PAGE_SUMMARY.md](ONE_PAGE_SUMMARY.md).

## Standalone verification

Run `.runtime/python.exe tests/check_standalone.py` (or the Python in your local `.venv`). This checks interpreter/import paths, runs real MCP search/ranking, and verifies MCP uses this interpreter, with no sibling project dependency. The base app works without OpenAI connectivity through its bounded fallback; OpenAI planning requires an API key and internet access. Manufacturer imagery also requires internet access.

## Manufacturer coverage

The filter includes all 20 brands on the supplied [DiscList page](https://thedisclist.com/brands/), with at least one actual source-linked disc per brand. Five defaults are shown initially; **Show more (15)** reveals the rest. The sidebar states the total manufacturer count. This is a dated, curated coverage/ranking snapshot, not a live ranking feed or a claim to list every manufacturer worldwide. Some brands have only one seed disc, so a specific category or similarity search may still return no matches for them.

Innova, Axiom, Discraft, Discmania, MVP, Latitude 64, Kastaplast, RPM, Dynamic Discs, Westside, Clash Discs, Streamline, Thought Space Athletics, Infinite Discs, Mint Discs, Prodigy, Divergent Discs, Doomsday Discs, Gateway, and Elevation are included. Short DiscList labels such as Thought Space, Infinite, Mint, Clash, Divergent, and Doomsday use their fuller brand names in the app.

Flight ratings link to manufacturer product pages. The expanded records include current source-specific ratings: Clash Soda is 7/5/-2/2, Divergent Kraken is 8/5/-1/2, Prodigy F5 is 8/6/-2/1, and the selected Elevation glO-G Koi run is 3/4/-2/0. Plastics/runs and published ratings can differ from older retailer listings. Manufacturer imagery remains best effort with the existing source-link and cache fallback.

## DiscFinder MCP on View disc

**View disc** now opens manufacturer details and independently requests stock from Golf With Discs DiscFinder at `https://finder.golfwithdiscs.com/mcp`. The backend uses the official MCP SDK's Streamable HTTP transport, initializes the remote server, lists its tools, verifies `find_retailer_stock`, and calls that tool with the selected catalog disc slug. A live connection to `golfwithdiscs-finder` version 1.1.0 and successful Leopard3 stock lookup were verified on November 6, 2026. No API key or login was required for those public calls.

The dialog shows source-returned retailer links, prices, country, plastic, weight, colors, and affiliate disclosures when supplied. Choose a country to request fresh localized results; the default is US. Countries/currencies reflect the server response. A country preference localizes results and currency; international retailers can still appear. Prices exclude shipping/checkout charges, and converted amounts may be estimates. Results may contain imperfect product matches, so confirm the linked product and stock with the retailer. No purchase is performed by the app.

`discfinder.json` declares the fixed endpoint, tool, default country, and offer limit (10). Each lookup has a 25-second overall deadline, uses no OpenAI credentials, and writes an independent UUID audit record including the source, tool, country, timestamp, offers, and trace. Offers are not cached as live stock. Not-found and no-offer results are distinct from service outages. Missing-tool, transport, and remote failures produce an unavailable state. Stock errors show a retry message; they never use web searches, general model knowledge, or another stock service. Manufacturer photos and bag controls remain usable independently.

The remote stock interface is independent of the local recommendation catalog. This change does not make the initial recommendation search use DiscFinder; it routes the requested **View disc** stock lookup to DiscFinder. The returned data is rendered as text and validated HTTPS links, not executed as HTML or instructions.

### Codex connection

The server was also registered in this user's Codex configuration using the supported command:

```powershell
codex mcp add golfwithdiscs-discfinder --url https://finder.golfwithdiscs.com/mcp
codex mcp get golfwithdiscs-discfinder --json
```

The installed Codex VS Code extension reads that MCP configuration. Start a new Codex session or reload the VS Code window to load newly registered tools into the native assistant tool list if needed. DiscBag's direct MCP client is already connected and does not depend on Codex reloading or its configuration. The user-level Codex config is local and is not published in this repository.

Verify directly with this app's local interpreter:

```powershell
./.runtime/python.exe tests/check_discfinder.py
./.runtime/python.exe tests/browser_discfinder_check.py
```

The first performs a live tool discovery and stock call; the second checks the actual View disc flow, country switching, and no-substitute outage handling. Neither uses a normal web search or a language model for stock.
