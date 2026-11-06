# Brief history of Disc Bag Advisor

Development recorded on November 6, 2026. This overview summarizes the milestones in [WORK_LOG.md](WORK_LOG.md); [ONE_PAGE_SUMMARY.md](ONE_PAGE_SUMMARY.md) describes the current application.

1. **Initial recommendation prototype.** The app began as a separate project inside the existing DGRag workspace. A FastAPI interface and custom Python asyncio orchestrator connected to local MCP tools for disc search, ranking, manufacturer images, and selection tracking. The first catalog contained 21 discs from four brands. A local Mistral model through Ollama selected tools, with a bounded fallback when it failed.

2. **Interactive search refinement.** Users gained controls for more overstable, more understable, faster, and slower recommendations. Refinements preserved brand filters and bag exclusions. Speed controls were hidden at the speed-1 and speed-14 limits. Sorting moved above brand preferences, and a top-five list with Show more expanded coverage to seven brands and 24 discs.

3. **Independent DiscBag application.** The project moved into its own DiscBag folder with VS Code launch support. Its initially shared Python dependency was then replaced with a private runtime and packages. Isolation checks verified that the app and MCP tools could run with access to DGRag blocked.

4. **Switch to OpenAI.** OpenAI's Responses API, using gpt-5-mini by default, replaced local Mistral inference. The custom asyncio orchestrator and MCP tools remained. Credentials stayed server-side in DiscBag's ignored .env, and controlled catalog fallback covered API failures.

5. **Broader coverage and a tighter interface.** The header and introduction became more compact. Manufacturer coverage grew to all 20 brands in the supplied DiscList snapshot, with 37 source-linked discs. The default five followed that ranking, and Show more exposed the remaining manufacturers.

6. **Live retailer stock through DiscFinder.** Golf With Discs DiscFinder was registered in Codex and connected directly to the app over remote HTTP MCP. View disc began calling find_retailer_stock to display retailer offers, prices, variants, and purchase links, with country selection and refresh. Stock failures explicitly return no substitute data from web search or model knowledge.

7. **Activity feedback and clearer documentation.** The decorative disc became a loading indicator that spins while requests are active, including overlapping requests, and respects reduced-motion preferences. The one-page summary was clarified to identify the custom asyncio orchestration framework and distinguish external service calls from local components.

Throughout development, the work log and GitHub repository recorded changes. Verification grew from nine initial automated checks to 23, supplemented by live OpenAI and DiscFinder calls, desktop/mobile browser checks, and standalone isolation checks.
