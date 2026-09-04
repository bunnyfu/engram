# Digital-Engram Memory Backends — Research Digest (Aug 2026)

Star counts pulled live from GitHub API on 2026-08-27.
Legend: **[CONSOLIDATION]** = genuine write-time/sleep-time synthesis (extraction, merging, reflection, updating) — not just embedding search. **[GRAPH]** = structured/KG consolidation. **[RAG]** = mostly vector/keyword recall with little synthesis.

## Tier 1 — Memory frameworks with real consolidation / reflection

- **Letta (fka MemGPT)** — https://github.com/letta-ai/letta — ⭐24.5k, active (pushed 2026-08). **[CONSOLIDATION]**
  Agent OS where the LLM self-edits tiered memory: editable `human`/`persona` core-memory blocks + archival store, with tool calls to rewrite its own memory. The `human` block is literally the distilled user profile — closest shipping analog to an engram "user block". Runs local (Ollama/local endpoints). The original repo also ships persona/human seed files (system-prompt artifacts for mimicry).

- **Honcho** — https://github.com/plastic-labs/honcho — ⭐6.9k, active. **[CONSOLIDATION]**
  The most on-target project for "profile the user": a deriver asynchronously turns every message batch into a structured *user representation* (preferences, beliefs, contradictions) and a "Dialectic" agent synthesizes reasoning about the user's current state, injected into the system prompt (peer cards + representations). Self-hostable. Hermes Agent already integrates it — direct reuse path.

- **Mem0** — https://github.com/mem0ai/mem0 — ⭐64.2k, very active. **[CONSOLIDATION]**
  Write-path LLM pipeline: extract candidate facts from each turn, then decide ADD/UPDATE/DELETE/NOOP against existing memories (dedupe + contradiction resolution), optional graph variant. Local-capable (local LLM + Qdrant/Neo4j). OpenMemory MCP server ships inside the same repo. Consolidation is fact-level, not narrative/reflection-level.

- **Hindsight (Vectorize)** — https://github.com/vectorize-io/hindsight — ⭐21.5k, very active, has arXiv paper (2512.12818). **[CONSOLIDATION]**
  Explicitly "learn, not just remember": three ops — retain / recall / **reflect** — with typed memories, "observations", and mental models; markets itself as eliminating plain-RAG/KG shortcomings; SOTA claims on long-term-memory benchmarks. Embedded Python mode (no server) makes it local-friendly. Newer but strong fit.

- **LangMem** — https://github.com/langchain-ai/langmem — ⭐1.6k, active. **[CONSOLIDATION]**
  Functional primitives: hot-path memory tools plus a **background memory manager** that extracts, consolidates, and generalizes memories into updatable profile docs (semantic/episodic/procedural). Storage-agnostic; LangGraph-native. Best pick if building your own consolidation loop in LangGraph.

- **Zep / Graphiti** — https://github.com/getzep/graphiti (⭐30.3k) + https://github.com/getzep/zep (⭐4.9k, now examples/integrations) — active. **[GRAPH]**
  Temporal knowledge graph: entities/edges with validity windows, fact invalidation on contradiction, community summarization. Excellent for evolving beliefs over time ("used to believe X, now Y") but heavier (graph DB, cloud-leaning Zep service).

- **MIRIX** — https://github.com/Mirix-AI/MIRIX — ⭐3.4k, active, arXiv 2507.07957. **[CONSOLIDATION]**
  Multi-agent memory system: six typed stores (Core w/ `human`+`persona` blocks, Episodic, Semantic, Procedural, Resource, Knowledge Vault) each managed by a dedicated agent, with screen-activity capture consolidated into structured memories. Privacy-first/local storage. Very aligned with a whole-life engram, but complex (Postgres, Docker, multi-agent).

- **MemOS** — https://github.com/MemTensor/MemOS — ⭐11k, active. **[CONSOLIDATION]**
  "Memory operating system": memory scheduling, migration between parametric/activation/plaintext memory, async memory-add, preference memory; published results on LoCoMo/LongMemEval/PersonaMem/PrefEval. Research-grade but actively engineered; worth watching for consolidation ideas.

- **Cognee** — https://github.com/topoteretes/cognee — ⭐30.3k, very active. **[GRAPH]**
  Ingestion pipelines (ECL) that build self-hosted knowledge graphs over your data with multiple retrieval modes. Strong on document ingestion → graph; consolidation is structural (graph build), less "reflective". Good complement for ingesting a person's corpus, less so for per-conversation profiling.

- **Generative Agents (Stanford)** — https://github.com/joonspk-research/generative_agents — ⭐22k, stale (2024). **[CONSOLIDATION]**
  The canonical memory-stream + recency/importance/relevance retrieval + periodic **reflection** that synthesizes raw observations into higher-level beliefs. Dormant code, but the reflection algorithm is the blueprint every engram build should copy. Smaller reimpls: mgarasz/llm-memory-stream (8⭐), NirDiamant/Agent_Memory_Techniques (933⭐, 30 runnable notebooks incl. consolidation/self-reflection/forgetting chapters — great teaching artifact).

- **StanfordHCI/genagents** — https://github.com/StanfordHCI/genagents — ⭐587, stale. **[CONSOLIDATION]**
  "Generative Agent Simulations of 1,000 People": builds an agent of a *specific real person* from a 2-hour interview, with pre-populated memory stream. Closest academic precedent to "digital copy of a person"; useful for architecture and eval methodology (how well does the copy match the person?).

## Tier 2 — User-profiling / 'learn the user' specific

- **Second Me** — https://github.com/mindverse/Second-Me — ⭐15.7k, but stale (last push 2025-09). **[CONSOLIDATION — different paradigm]**
  Explicitly a local, private "AI self": ingests your documents/chats, builds hierarchical memory, then *fine-tunes* a model (LoRA-style training pipeline) to mimic you. The only mainstream repo whose goal is literally a digital twin. Risk: momentum fading; training pipeline is heavier than memory-store approaches.

- **Supermemory** — https://github.com/supermemoryai/supermemory — ⭐29.1k, very active. **[RAG+profile, partial consolidation]**
  Fast memory engine + app, runnable fully locally; builds a user-profile summary injected at conversation start, plus plugins for Claude Code/OpenCode/Hermes. Profile layer is useful; consolidation depth is shallower than Honcho/Letta.

- **GetProfile** — https://github.com/getprofile/getprofile — ⭐37, low activity. **[CONSOLIDATION, tiny]**
  Drop-in LLM proxy that gives any model persistent memory and *structured user understanding*. Tiny but the proxy pattern (profile extracted transparently from all traffic) is worth stealing.

- **dilettacal/digital-twin** — https://github.com/dilettacal/digital-twin — ⭐1. **[RAG]**
  FastAPI/Next.js/Bedrock "represent you" chatbot from LinkedIn + facts + style notes. Toy, but a minimal reference for static-persona prompting.

- **Letta/MemGPT persona & human seed files** — in-repo `personas/` + `humans/` examples. System-prompt artifacts: the `human` block format (a concise, LLM-maintained dossier on the user) is the de-facto template for "learn the user" prompting.

## Tier 3 — Local storage backends (no real consolidation; plumbing only)

- **basic-memory** — https://github.com/basicmachines-co/basic-memory — ⭐3.8k, active. **[RAG]** Markdown files + SQLite FTS over MCP; durable, local, human-readable — great storage substrate, zero synthesis.
- **mcp-memory-service** — https://github.com/doobidoo/mcp-memory-service — ⭐1.9k, active. **[RAG]** SQLite-vec memory over MCP for Claude/LangGraph/CrewAI; tags + semantic search, no consolidation.
- **LightMem** — https://github.com/zjunlp/LightMem — ⭐1.1k, ICLR 2026. **[CONSOLIDATION-lite]** Efficiency-focused memory-augmented generation (compression/offline distillation of memories); useful for cost control of a consolidation loop.
- **NirDiamant/Agent_Memory_Techniques** — ⭐933, active. Educational: 30 notebooks covering consolidation, self-reflection, hierarchical layers, forgetting/decay + integrations with Mem0/Letta/Zep/Graphiti. Best single learning resource before building.

## Recommendation sketch for a local engram
1. **Core profiling loop**: Honcho-style deriver (or LangMem background manager) producing a structured user representation, injected as a Letta-style `human` core-memory block.
2. **Reflection/consolidation**: copy Generative Agents' reflection (or Hindsight's reflect op) on a schedule — synthesize beliefs/goals/style from episodic memories.
3. **Temporal beliefs**: Graphiti-style validity windows if you need "beliefs that changed over time".
4. **Mimicry endgame**: Second Me shows the fine-tuning route; alternatively keep mimicry purely prompt-side via the consolidated profile (cheaper, editable).
5. Avoid pure-RAG stores (Tier 3) as anything but the storage layer.
