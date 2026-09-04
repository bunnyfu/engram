# Alternative Directions for Capturing a Digital Likeness
*(Beyond "chat agent + consolidating memory store")*

Legend: Goal (a) = coach/psychologist that knows you · Goal (b) = posthumous copy that mimics you

---

## 1. Parameter-level cloning (LoRA/QLoRA on a personal corpus)

**Approach:** Fine-tune an open-weight LLM (Qwen2.5/Llama/Mistral 7B class) with LoRA/QLoRA adapters on journals, chat exports, blog posts, emails. Style and voice get baked into weights; facts still need retrieval.

**Key repos/URLs:**
- `xming521/WeClone` — one-stop pipeline: WeChat/chat-history cleaning → LLaMA-Factory LoRA/QLoRA (Qwen2.5-7B) → bind to Telegram/WhatsApp bot → optional voice clone. github.com/xming521/WeClone
- `mindverse/Second-Me` — full local "AI self" system; Hierarchical Memory Modeling + Me-Alignment (paper: arXiv 2503.08102). github.com/mindverse/Second-Me
- Tooling: `hiyouga/LLaMA-Factory`, `unslothai/unsloth`, `axolotl-ai-cloud/axolotl`, Lightning-AI `litgpt`, HF `peft`/`trl`.

**Realistic data volumes:**
- Recognizable *style*: ~5k–50k high-quality message pairs (WeClone community reports tens of thousands of chat lines as a good start; more data + cleaning > more epochs).
- Facts/biography: LoRA does **not** reliably memorize facts — don't expect it; pair with retrieval.
- Corpora below ~1–2k examples mostly yield a vibe layer, not a clone.

**Hardware (local):** QLoRA 7B: ~8–12 GB VRAM min (RTX 3060 12GB workable; Unsloth ~8–10GB), 24 GB (3090/4090) comfortable; 13B needs ~20GB+. Train time: hours for a few epochs on a 7B.

**Maturity:** Medium-high. Active repos, working tutorials; quality ceilings are real (persona drifts to base-model assistant-ness without careful data).

**Goal fit:** (a) Medium alone — needs a retrieval layer for accurate self-knowledge. (b) **Strong** — this is the only direction that makes the *weights themselves* sound like you.

---

## 2. Voice cloning (speech layer of the engram)

**Approach:** Zero-/few-shot speaker cloning from short reference audio; optional fine-tuning for higher fidelity.

**Key repos/URLs & sample needs:**
- **XTTS v2** (`coqui-ai/TTS`, fork `idiap/coqui-ai-TTS`) — ~6s minimum, 15–30s recommended; 17 languages; embeddings truncated at ~12s/file, so quality of reference > quantity. Inference ~4 GB VRAM.
- **F5-TTS** (`SWivid/F5-TTS`) — zero-shot from 5–15s reference; fine-tune with ~30 min–1 h of clean audio on 16 GB+ VRAM (24 GB comfortable); real-time inference; ComfyUI/LocalAI integrations.
- **OpenVoice V2** (`myshell-ai/OpenVoice`, MIT) — instant clone from a short clip; tone-color converter decouples voice from style/emotion (V2: multi-accent, emotion control).
- Worth adding: **GPT-SoVITS** (`RVC-Boss/GPT-SoVITS`) — very high similarity from ~1 min of audio, popular for personal clones; **CosyVoice 2** (FunAudioLLM).

**Hardware (local):** Inference 4–8 GB VRAM (or CPU, slowly); fine-tuning 12–24 GB. All run offline.

**Maturity:** High / production-adjacent — this is the most solved of the five directions.

**Goal fit:** (a) Medium — voice adds presence/empathy to a coach. (b) **Strong** — voice is the highest-emotional-bandwidth mimicry channel; 30s–5min of audio often suffices for a recognizable copy.

---

## 3. Life-logging capture pipelines (datafeeds, not models)

**Approach:** Continuous passive capture of screen/audio → OCR + embedding index → natural-language recall. Serves as the raw corpus for everything else (fine-tuning data, KG episodes, retrieval store).

**Key projects:**
- Commercial: **Microsoft Recall** (Copilot+ PCs, NPU, on-device snapshots), **Rewind.ai** (macOS), **Limitless** (pendant + cloud).
- Open: **screenpipe** (`screenpipe/screenpipe`, Rust, source-available, YC S26) — continuous screen+audio capture, local store, plugin "pipes", feeds agents; most mature/active. Runs Mac/Win/Linux, CPU-friendly.
- **OpenRecall** (`openrecall/openrecall`, Python) — screenshots + OCR + semantic search, fully local.
- **Pensieve** (`arkohut/pensieve`) — passive recording, local index, web UI; Rewind/Recall-inspired.
- Also: **Windrecorder** (Windows), TimeScroll.

**Hardware:** Cheap — no GPU required for capture/OCR; tens of GB–TB disk over months; optional local LLM (8–16 GB VRAM) if you want on-device summarization.

**Maturity:** screenpipe high/medium-high; OpenRecall/Pensieve medium (personal-project energy).

**Goal fit:** (a) **Strong** — gives a coach ground-truth behavioral context ("what you actually did all week"). (b) Medium — indispensable as *corpus source*, but captures behavior, not inner voice; pair with direction 1/4.

---

## 4. Structured self-modeling (knowledge graphs / personal ontologies)

**Approach:** Extract entities, relationships, and temporally-versioned facts into a graph instead of free-text notes; query by traversal + semantic search. Contradictions and change-over-time become first-class.

**Key repos/URLs:**
- **Graphiti** (`getzep/graphiti`) — temporal/bi-temporal KG memory for agents on Neo4j/FalkorDB; ingests "episodes", tracks fact invalidation, prescribed + learned ontology. Backed by Zep (cloud option).
- **Mem0** (`mem0ai/mem0`) — memory layer with optional graph store (Neo4j/Memgraph).
- **Cognee** (`topoteretes/cognee`) — ECL pipeline turning docs into KG + vector memory.
- Academic: personal knowledge graph (PKG) literature (Jilek et al. 2023; RDF/ACL access control, provenance per statement) — relevant for posthumous data rights.

**Hardware:** Light — Neo4j community or FalkorDB embedded runs on a laptop; main cost is LLM extraction calls (local 7B or API).

**Maturity:** Medium-high for Graphiti/Mem0 (active, production users); personal-ontology tooling remains DIY.

**Goal fit:** (a) **Strongest single direction for (a)** — a coach needs accurate, queryable, current facts about you (people, health, projects, values, how they've changed). (b) Medium — structure captures *what* you were, not *how* you sounded; combine with 1+2.

---

## 5. Hybrid retrieval + parametric / continual learning

**Approach:** Keep the base model frozen-ish; periodically distill high-value memories into adapters while retrieval supplies the long tail. Research frontier: how to keep updating without catastrophic forgetting.

**Key work/repos:**
- **RAFT** (Retrieval-Augmented Fine-Tuning, Shishir Patil / Gorilla) — train model to use retrieved context well; practical hybrid recipe.
- **HippoRAG / HippoRAG 2** (`OSU-NLP-Group/HippoRAG`) — hippocampus-inspired KG + Personalized PageRank over RAG index; strong long-term-memory benchmarks; arXiv 2502.14802 frames non-parametric continual learning.
- **Sparse memory finetuning** (arXiv 2510.15103) — update only memory slots; Pareto-beats LoRA and full FT on the learn/forget tradeoff for factual QA.
- **Model editing**: ROME/MEMIT via `zjunlp/EasyEdit`, WISE — surgical fact edits without retraining.
- Classic continual learning applicable to LoRA: replay buffers, EWC-style regularization, adapter stacking / LoRAHub, MoLE (mixture of LoRA experts).

**Hardware:** Varies — retrieval+LoRA-refresh fits a 24 GB card; continual-pretraining experiments want A100-class or cloud bursts.

**Maturity:** RAG+periodic-LoRA is production-feasible today; sparse memory FT / HippoRAG / model editing are research-stage (papers + reference code, not turnkey products).

**Goal fit:** (a) **Strong** — the pragmatic architecture for a living coach: graph/vector retrieval for facts + scheduled adapter refresh for evolving style. (b) Strong — the only route that keeps both style and facts fresh long-term; for a static posthumous copy, a final one-shot hybrid build is the natural endpoint.

---

## Cross-cutting synthesis

| Direction | Cost (local) | Maturity | Coach (a) | Posthumous copy (b) |
|---|---|---|---|---|
| 1. LoRA/QLoRA cloning | 12–24 GB VRAM | Med-high | M | **S** |
| 2. Voice cloning | 4–8 GB VRAM | High | M | **S** |
| 3. Life-logging feeds | CPU + disk | Med-high | **S** | M (corpus) |
| 4. Knowledge graphs | CPU/light | Med-high | **S** | M |
| 5. Hybrid/continual | 24 GB+ / mixed | Mixed | **S** | S |

A serious "digital likeness" stack is a composition: **3 feeds → 4 structures → 5 keeps current → 1 provides voice-in-text → 2 provides voice-in-speech**. The SOUL.md+Hindsight approach is essentially a lightweight subset of 4+5 with none of 1/2.
