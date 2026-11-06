# Disc Bag Advisor - one-page summary

**Purpose.** Fieldwork recommends disc golf discs by name, reference discs, or flight category. The interface provides brand filters, sorting, manufacturer photos, a saved bag, and speed/stability refinements. Its local catalog contains 37 discs across 20 manufacturers.

**Agentic orchestration framework: custom Python asyncio.** Application code in `agent.py` and `model_agent.py`, built on Python's standard-library **asyncio**, controls the model/tool loop, tool discovery, allowed actions, deadlines, retries, fallback, and audit records. OpenAI interprets requests and requests search/rank function calls. The controller executes those calls through MCP and returns search observations to OpenAI. The host enforces catalog identity and brand/sort/bag constraints. Planning is limited to four model responses and 40 seconds within a 65-second workflow.

**Component roles.** FastAPI/Uvicorn serves the web interface. The official **MCP Python SDK / FastMCP** supplies tool definitions, client sessions, and transport. The **custom asyncio controller performs agent orchestration**. Normal flow: browser -> FastAPI -> controller -> OpenAI -> local MCP search/rank tools -> results. Refinements and OpenAI-failure fallback use deterministic MCP workflows.

**External services called during use**

| Service | Trigger and purpose | Data sent |
| --- | --- | --- |
| **OpenAI Responses API** - `https://api.openai.com/v1/responses` | Model-enabled searches; `gpt-5-mini` interprets the request and selects tools. Uses `store: false`. | Search text, instructions/tool schemas, and catalog search observations. The API key is server-side. |
| **Golf With Discs DiscFinder MCP** - `https://finder.golfwithdiscs.com/mcp` | **View disc**, country changes, and refresh call **`find_retailer_stock`** for retailer prices, variants, availability, and links. | Disc slug, country, offer limit, and stock filter. No OpenAI key; tested public calls needed no login. |
| **Manufacturer websites / image CDNs** | Disc selection fetches an official product page; the browser loads its image. Cached URLs reduce page fetches. | Product/image URLs through ordinary HTTPS requests; no OpenAI key. |

Retailer pages open only when users follow purchase links; no purchase is automated. DiscList rankings are a bundled snapshot, not a live search. GitHub hosts code, not recommendation data. The local MCP stdio server, catalog, SQLite, and JSON logs run inside DiscBag.

**Recovery and provenance.** DiscFinder is the sole stock source: no web search, model knowledge, or alternate inventory replaces it. Stock has a 25-second deadline and explicit empty/error states; imagery and bag controls remain independent. Retailer affiliate disclosures are preserved. Prices exclude shipping/checkout charges; confirm products and availability with retailers.

**Records and launch.** `WORK_LOG.md` records changes; `AGENT_FRAMEWORK.md` details orchestration. UUID-linked JSON logs retain inputs, source/tool, results, timings, and traces. SQLite stores local selection popularity and image-cache URLs. All 23 automated checks passed, with live service, browser, and standalone-isolation checks. DiscBag owns its runtime/packages. Run `./start.cmd`, then visit `http://127.0.0.1:8010`. Its OpenAI key stays in the ignored `.env`. The app is local and single-user. [Source repository](https://github.com/dougwalkerextension-sketch/disc-bag-advisor).
