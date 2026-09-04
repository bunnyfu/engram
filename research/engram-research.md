# Academic Landscape for a Local Personal Engram (2022–2026, arXiv-focused)

## A. Agent memory architectures with consolidation/reflection

- **Generative Agents: Interactive Simulacra of Human Behavior** — arXiv:2304.03442 (2023). Memory stream + reflection + retrieval (recency/salience/relevance) enables believable, plan-driven agents. *The canonical template for engram design: raw event log + periodic reflection into higher-level summaries.*
- **MemoryBank: Enhancing LLMs with Long-Term Memory** — arXiv:2305.10250 (2023, AAAI'24). Ebbinghaus forgetting-curve updating: memories decay with time unless reinforced by significance/recall. *Directly applicable: time-weighted retention and user-personality synthesis from chat history.*
- **MemGPT: Towards LLMs as Operating Systems** — arXiv:2310.08560 (2023). OS-style hierarchical memory (main context ↔ external storage) with self-directed paging. *Foundation of Letta; shows LLMs can manage their own memory tiers via function calls.*
- **A-MEM: Agentic Memory for LLM Agents** — arXiv:2502.12110 (2025). Zettelkasten-style notes (context, keywords, tags) that auto-link and *evolve* — new memories trigger updates to old ones. *Closest match to a self-organizing personal engram without predefined schemas.*
- **Mem0: Production-Ready Scalable Long-Term Memory** — arXiv:2504.19413 (2025). Dynamic fact extraction/consolidation + optional graph memory; +26% over OpenAI memory on LOCOMO at lower latency/cost. *Production reference: extraction-based consolidation beats raw RAG on long multi-session histories.*
- **Zep: Temporal Knowledge Graph Agent Memory** — arXiv:2501.13956 (2025). Graphiti: temporally-aware knowledge graph for agent memory; beats MemGPT on DMR. *Temporal validity edges matter for evolving personal facts.*
- **MemoryOS** — arXiv:2506.06326 (2025). Three-tier storage (short/mid/long-term personal memory) with OS-inspired updating. *Explicit "personal memory" tier in hierarchical design.*
- **LoCoMo** — arXiv:2402.17753 (2024). Benchmark of very long-term (≥35 sessions) persona-grounded dialogues; shows RAG and long-context models degrade sharply at long horizons. *Defines the hard eval regime an engram must survive.*
- **LongMemEval** — arXiv:2410.10813 (2024, ICLR'25). Five long-term memory abilities incl. knowledge updates and abstention; commercial assistants fail often. *Abstention/knowledge-update are underbuilt in most engram designs.*

## B. Persona simulation / role-play fidelity of real individuals

- **Generative Agent Simulations of 1,000 People** (a.k.a. "LLM Agents Grounded in Self-Reports…") — arXiv:2411.10109 (2024). 2-hour interviews + surveys of 1,052 real people → agents replicate held-out GSS responses at 82–86% of participants' own test-retest reliability. *Best-case bound: high fidelity needs a 2-hour structured interview, not scraped text.*
- **Character-LLM: A Trainable Agent for Role-Playing** — arXiv:2310.10158 (2023). Fine-tune on profile-as-experience (Beethoven, Cleopatra) beats prompting for vividness/memorization. *Experience-rehearsal training for character simulacra.*
- **ChatHaruhi** — arXiv:2308.09597 (2023). Script-extracted memories + improved prompting for 32 fictional characters. *Memory-conditioned prompting baseline for person-simulation.*
- **IMPersona: Evaluating Individual-Level LM Impersonation** — arXiv:2504.04332 (2025). ⚠ SFT + hierarchical memory retrieval lets even Llama-3.1-8B fool humans in 44% of blind conversations vs 25% for best prompting. *Positive result for cloning feasibility at small scale — but also flags deception/safety risk.*
- **TwinVoice: Multi-dimensional Benchmark Towards Digital Twins** — arXiv:2510.25536 (2025). Real-context benchmark (social/interpersonal/narrative persona; 6 capabilities incl. opinion consistency, lexical fidelity, syntactic style). ⚠ Advanced models handle surface traits but degrade on deeper cognitive consistency. *Defines which engram outputs to evaluate.*

## C. Longitudinal user modeling / digital twin of a person

- **AI-native Memory 2.0: Second Me** — arXiv:2503.08102 (2025). Fully automated post-training pipeline from personal documents → parameterized personal model (memory as weights, not just retrieval). ⚠ LLM-judged evals underestimate quality. *The "train-your-twin" alternative to retrieval engrams; hybrid layered system is the practical pattern.*
- **Enabling Personalized Long-term Interactions via Persistent Memory & User Profiles** — arXiv:2510.07925 (2025). Incremental implicit user profiling across sessions; evaluated on LoCoMo/LongMemEval. *Profile-as-living-document approach.*
- **MemoryCD** — arXiv:2603.25973 (2026). First lifelong cross-domain memory benchmark from real multi-year user behavior (Amazon reviews), not synthetic personas. *Real longitudinal data >> scripted personas for evaluation.*
- **Social Digital Twins framework** — arXiv:2601.06111 (2026). LLMs as cognitive engines for population replicas. *Population-scale, less relevant to single-person engram.*

## D. Mimicking a specific person from limited data — evaluations & hard limits

- **Catch Me If You Can? Not Yet** — arXiv:2509.14543 (2025). ⚠ **Key negative result**: 40k+ generations, 400+ authors — SOTA LLMs approximate style only in structured genres (news, email) and fail on implicit, nuanced personal style from few-shot samples. *Hard limit: few examples capture surface style, not deep idiosyncrasy.*
- **How Well Do LLMs Imitate Human Writing Style?** — arXiv:2509.24930 (2025). Training-free authorship-verification/style-imitation framework; replication of a specific author "remains unclear" even with controlled prompting.
- **LLM-based Human Simulations Have Not Yet Been Reliable** — arXiv:2501.08579 (2025). ⚠ Position paper: systematic review finds persistent gaps vs authentic human action; attributes failures to inherent LLM limits + flawed simulation design.
- **The Chameleon's Limit: Persona Collapse & Homogenization** — arXiv:2604.24698 (2026). ⚠ Distinct assigned personas converge to a narrow behavioral mode across 10 LLMs (measured via Coverage/Uniformity/Complexity). *Failure mode: engram-conditioned agents may still regress to the model mean.*

## Takeaways for a local personal engram

1. **Architecture**: raw memory stream + reflection/consolidation (Generative Agents) + forgetting/reinforcement (MemoryBank) + self-organizing links/evolution (A-MEM) is the convergent design; Mem0/Zep show extraction + temporal graph beats raw RAG.
2. **Data thresholds**: best-case cloning of opinions/decisions needs ~2-hour structured interviews (Park et al., 2411.10109) or fine-tuning on personal corpora (Second Me, IMPersona); few-shot style transfer from a handful of samples demonstrably fails (2509.14543).
3. **Failure modes to design against**: persona collapse/homogenization, genre-dependent style leakage, stale-fact contamination (temporal invalidation — Zep), and hallucinated recall without abstention (LongMemEval).
4. **Evals**: TwinVoice capability split (opinion consistency, memory recall, lexical fidelity) + LoCoMo/LongMemEval for longitudinal memory; judge-based evals underestimate small personal models (Second Me caveat).
