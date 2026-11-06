# Disc Bag Advisor · Fieldwork

A responsive disc golf recommendation app using a local model agent and real MCP tools. Search by one disc, multiple references, or a flight category; filter brands; sort by match, local popularity, speed, or name; inspect manufacturer imagery; save a bag in your browser.

## Run

Requires Python 3.11+ (tested with 3.12). From this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:8010**. The app now lives in `C:/Users/dougw/DiscBag`. `./start.ps1` uses a local virtual environment when present, otherwise the existing Python runtime at `../DGRag/.runtime/python.exe`. In this VS Code workspace, run the **Start Disc Bag Advisor** task, or run `../DGRag/.runtime/python.exe app.py` in the terminal. The included VS Code launch configuration also supports F5 with the Python debugger extension installed. This independent app does not read the Poe app's `.env`.

For model mode, install/start [Ollama](https://ollama.com/) and run `ollama pull mistral:7b`. The default is `mistral:7b`, configured with the `DISC_AGENT_MODEL` environment variable. The only model endpoint is `http://127.0.0.1:11434/api/chat`; no paid model or API key is needed. Set `DISC_AGENT_MODEL` to an empty string for the deterministic workflow. Model errors/timeouts automatically fall back; the UI trace identifies the actual mode.

## Use and catalog scope

- `Similar to Leopard3` compares flight numbers and excludes the reference disc.
- `Similar to River and Crave` averages distance from up to three named references.
- `understable fairway driver`, `stable midrange`, `overstable distance driver`, or `putter` filter by flight category.
- Selected brands are strict filters. Leave unchecked to include all brands.
- Sorting appears above brand preferences. The default brand list shows Discraft, Axiom, MVP, Innova, and Discmania, based on [OTB's 2025 retail sales ranking](https://otbdiscs.com/otbs-top-100-discs-of-2025/), not worldwide market share. **Show more** reveals every remaining catalog brand. No brand is checked by default. Collapsing the list retains filters and reports hidden selections on the button. Available brands come from the catalog API and are validated against the same catalog registry.
- After a search, use **More overstable**, **More understable**, **Faster**, or **Slower** to shift from the leading displayed result. The reference name, speed, and turn + fade appear beside the controls. Each click searches the catalog through MCP, preserves current brand/sort/bag preferences, and requires strictly higher/lower speed or stability. Speed shifts may cross disc categories. Slower is hidden at speed 1; Faster is hidden at speed 14. Empty shifts retain the current results. Changing sort preserves the latest shift; submitting a search starts fresh.
- Open a result for manufacturer imagery and add it to your bag. Bagged discs are excluded from subsequent searches; **My bag** allows removal.

The starter catalog has **24 discs across seven brands**. Flight numbers are source-linked curated seed data, not a complete or continuously refreshed database. Similarity uses weighted flight-number distance. Stability categories use turn + fade: understable < 0; stable >= 0 and < 2; overstable >= 2. This application heuristic is not a universal manufacturer standard. Weight, plastic, wear, power, and release affect actual flight.

Popularity means **detail-card selections on this installation**, stored in SQLite. It is not global sales. Fresh installations start at zero; ties use match score then name. Adding to a bag does not itself increment popularity.

## MCP and agent framework

The official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) supplies ClientSession, stdio transport, and FastMCP. A custom asyncio orchestrator manages a local model tool loop following [Ollama tool calling](https://docs.ollama.com/capabilities/tool-calling). It does not use LangGraph or the separate FastMCP v2 package. See [AGENT_FRAMEWORK.md](AGENT_FRAMEWORK.md) for the execution graph and controls.

External MCP hosts can launch the same tools using their actual Python executable and absolute path:

```json
{"mcpServers":{"disc-bag-tools":{"command":"C:/path/to/.venv/Scripts/python.exe","args":["C:/path/to/disc-bag-advisor/tools_server.py"]}}}
```

Tools are `search_discs`, `rank_discs`, `manufacturer_image`, and `record_selection`. Recommendation and detail endpoints create real MCP sessions; they do not shortcut to in-process domain calls. `/api/catalog` is a read-only UI bootstrap.

## Recovery and records

Invalid input receives 422, unknown discs 404, and tool outages a friendly 503. Browser requests time out after 70 seconds; model planning after 25 seconds; the workflow after 65 seconds. Read tools retry once, selection increments never retry. Failed searches retain previous visible results and saved bags.

Manufacturer requests use fixed HTTPS source URLs, a hostname allowlist, bounded redirects, two MB page limits, eight-second network timeouts, one-day image URL caching, and stale-cache fallback. Missing metadata, rate limits, hotlink restrictions, and browser image failures show recovery messages with an official-page link. Metadata can occasionally identify a promotional image; review imagery when expanding the catalog.

`runtime/` stores SQLite popularity/image-cache data and one JSON file per agent run, including the original query, preferences, results, mode, run ID, statuses, and timings. Bag contents stay in this browser. Logs can contain search text; stop the app and delete `runtime/` to reset history/cache/popularity. Runtime data, screenshots, environments, and credentials are excluded from source publication.

The server binds to localhost with host/origin checks. This is a single-user app. Internet hosting requires a Python-capable service plus deployment-specific authentication, limits, and persistence. The Python/stdio backend cannot run on static GitHub Pages or directly in Sites' Cloudflare Worker runtime. No hosted deployment is claimed.

## Checks and handoff

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tests/check_model.py
```

The first command runs offline checks including real MCP transport. The second verifies live Ollama tool calling. `tests/browser_check.py` is workspace QA for installed Edge/Playwright; adjust its optional driver path elsewhere. See [WORK_LOG.md](WORK_LOG.md) and [ONE_PAGE_SUMMARY.md](ONE_PAGE_SUMMARY.md).
