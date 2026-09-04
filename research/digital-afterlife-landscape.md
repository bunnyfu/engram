# Digital Afterlife / Griefbot / Persona-Clone Landscape (as of Aug 2026)

## Commercial / hosted products

| Name | URL | Status | Approach | Pricing | Data feeds | Key lesson for a DIY local build |
|---|---|---|---|---|---|---|
| **HereAfter AI** | hereafter.ai (iOS/Android app) | Alive | **Scripted retrieval**: guided voice-recorded interview (life-story questions), answers matched to user questions and played back in the person's own recorded voice with photos; newer versions add generative avatar. Not a free-form LLM clone. | Freemium; ~$199 one-time/lifetime tier historically | Self-recorded audio answers to a structured question bank, photos | Retrieval of *authentic recorded answers* beats generation for trust: nothing the "person" says was hallucinated. A local build can combine: verbatim playback for covered topics + clearly-labeled generative fallback. |
| **You, Only Virtual (YOV)** — successor to **Eternos** | myyov.com | Alive (~300 paying users per The Atlantic, Feb 2026) | Bespoke "Versona": ML/LLM trained per-person on relationship data; **Versona Voice** generates phone calls with the deceased. Emphasis: each relationship produces a different "version" of the person | Subscription (bespoke onboarding) | Text messages, voice recordings, video chats collected pre- or post-mortem from *both* sides of the relationship | Persona is relationship-relative: fine-tune/condition on the dyadic conversation history (deceased ↔ specific relative), not a generic "person model." One clone per relationship. |
| **Project December** ("Simulate the Dead") | projectdecember.net | **Dead** — OpenAI cut Jason Rohrer's GPT-3 access in Sept 2021; project effectively shut down | Prompt-engineered GPT-3: user pasted sample texts + a persona "seed" paragraph; pay-per-token credit system | Micro-payment (~$5 per chunk of conversation) | A few pasted writing samples + hand-written persona description | (a) Tiny in-context samples of a person's writing can already produce a shockingly convincing style match — prompting often suffices before fine-tuning. (b) Building on a hosted API whose provider can kill the use-case is an existential risk → run local models. |
| **Replika** | replika.ai | Alive (pivot history: founded 2017 from the Roman Mazurenko memorial bot built from ~8k of his chat messages) | LLM backbone (historically GPT-3-derived, now in-house models) + per-user retrieval memory + scripted dialogue trees + feedback loop (upvotes) that adapts to the user; voice calls/AR on paid tier | Freemium; Pro ~$70/yr | Ongoing chat with the user, diary entries, user-authored backstory, voice samples | The origin story is the lesson: Luka's first clone was trained on one person's exported Telegram messages. Long-term *episodic memory store + retrieval* matters more to "feeling like them" than model size. |
| **Personal.ai** | personal.ai | Alive, pivoted to enterprise "Small Language Model" platform (memory/personas for professionals) | Proprietary per-user **Personal Language Model**: user-owned "memory stack" (structured memory blocks) + model trained/grounded on it; user can correct and reinforce memories | Was freemium ($40/mo Pro tier); now enterprise/B2B | Messages, docs, emails, meeting transcripts — anything the user syncs into their Memory Stack | Explicit, user-editable memory objects (not opaque embeddings) give correction/control: when the clone says something wrong, you fix the memory, not the weights. Editable memory > retraining. |
| **StoryFile** (StoryFile Life) | storyfile.com | Alive | **Pure retrieval, zero generation**: subject answers ~75–250 of a 250k-question bank on camera (originally 20-camera volumetric rig; now consumer webcam); NLP matches visitor questions to the best pre-recorded video clip; "hologram" funeral deployments | One-time packages (funeral/life-story tiers, hundreds of $) + institutional | Studio or webcam video answers to structured interview questions | Proves the market for *scripted authenticity*: families prefer knowing every word is real. A DIY build should record the person answering a large curated question bank while alive — highest-fidelity asset you can capture. |
| **DeepBrain AI re;memory / re;memory2** | aistudios.com/rememory | Alive (re;memory2 launched on their Dream Avatar stack) | High-end **digital human**: studio capture → talking-head video avatar + conversational AI for dialogue | ~$12k–$24k creation fee + ~$1,200 per showroom session (premium memorial service) | Studio video/voice capture of the person (ideally pre-mortem), interview content | Only the avatar rendering is hard; the persona/conversation layer is commodity. Locally: voice clone (open TTS) + a good system prompt gets ~80% of the felt experience at 0.1% of the cost. |
| **Seance AI** | seanceai.app | Alive (small indie, Jarren Rocks) | Thin wrapper: prompt-constructed fictional persona on a hosted LLM; deliberately **short, closure-oriented sessions**, not permanence | Freemium (~$10 premium unlocks voice) | User-entered name, personality traits, memories, diary entries; no bulk data ingestion | Deliberate scope-limiting ("a séance, not a resurrection") is an ethical/UX feature: framing the bot as a bounded ritual reduces harm and expectation. DIY builds should ship a disclaimer + session framing by design. |

## Newer entrants (2024–2026)

| Name | URL | Status | Notes / lesson |
|---|---|---|---|
| **Afterlife AI** | afterlife.ai | Alive (2025–26) | Guided voice capture interview → generative "Persona" that answers in your way; positions itself as opt-in legacy service vs. posthumous data-mining. Lesson: opt-in/consent framing and "living likeness" marketing is where the category is heading. |
| **2wai** | 2wai.ai | Alive (launched June 2025, co-founder actor Calum Worthy) | Consumer app; "HoloAvatars" — real-time conversational video avatars in 40+ languages; pitched both for creators and for deceased relatives ("grandma's avatar"). Lesson: real-time video-avatar UX is now commodity consumer tech. |
| **Sensay** | sensay.io | Alive | Web3-flavored "digital replicas" (SNSY token); replicas trained on personal data, incl. dementia-patient preservation angle. Lesson: data-portability/ownership story (user owns the replica) resonates — exportable model+memory should be a DIY design goal. |
| **Meta patent US12513102B2** (granted Dec 2025) | — | Patent only | LLM simulation of a user from their social-media data, incl. posthumous. Lesson: the non-consensual version of this is being productized at platform scale — DIY/local with explicit consent is the counter-position. |

## "Talk-to-yourself" / coaching angle

- **MIT Media Lab "Future You"** (2024 research project): chat with an age-progressed 60-year-old version of yourself; LLM conditioned on a structured self-profile questionnaire + age-progressed photo. Shown to reduce anxiety and increase future-self continuity. Lesson: for coaching clones, a **future-self persona** (prompted from a goals/values questionnaire) is more useful than a faithful mirror clone — the design target is aspirational, not archival.
- Personal.ai and Replika also market journaling/self-coaching uses of the same stack.

## Open-source persona clones from chat exports

| Project | URL | Status | Approach | Lesson |
|---|---|---|---|---|
| **WeClone** ⭐ most complete | github.com/xming521/WeClone (docs.weclone.love) | Active (Telegram source added 07/2025; WhatsApp/Discord planned) | Full pipeline: WeChat/Telegram export → cleaning/PII filtering → **LoRA SFT via LLaMA-Factory** (default Qwen2.5-VL-7B-Instruct; recommends 14B+) → optional voice clone (0.5B TTS on WeChat voice messages) → deploy as a chat bot (WeChat/Telegram/Discord/Slack). VRAM table: QLoRA 7B ≈ 6GB. | The reference architecture for DIY: data hygiene (PII scrubbing) + LoRA on 14B+ + a real chat-platform front end. Fully documented — closest thing to a published architecture in this space. |
| **whatsapp-ai-clone / kinggongzilla** (now LatentMindAI/perzonalized-ai-chatbot) | github.com/kinggongzilla/whatsapp-ai-clone | Archived-ish (2023) | Parse WhatsApp .txt export → CSV (sender, message, ids) → LoRA fine-tune Llama-2-7B | Minimal viable recipe: export → thread reconstruction → LoRA. Including *both sides* of the conversation preserves dialog context (others' messages as prompt, yours as completion). |
| **GPT-is-you** | github.com/rchikhi/GPT-is-you | Small/stale | Prompt/RAG-style personalization from WhatsApp history | Prompt-only clone is a fine baseline; fine-tuning is optional until data volume justifies it. |
| **Amal-David/whatsapp-llm** | github.com/Amal-David/whatsapp-llm | Small | Python toolkit: WhatsApp data → personalized clone | Same pattern; preprocessing (threading replies, timestamps) is where the quality is won. |
| Adjacent tooling | Memotrace/留痕 (WeChat export), chatlog, Telegram Desktop export | Active | Data-extraction layer only | The hardest DIY step is often *getting clean data out* of WeChat/WhatsApp; these exporters are the unglamorous prerequisite. |

## Who publishes architecture / prompts?

- **WeClone** — fully open pipeline, docs site, training configs (the most transparent).
- **WhatsApp-clone repos** — open code by definition; kinggongzilla repo includes data-prep instructions.
- **Project December** — Rohrer publicly discussed the prompt-seeding mechanics (persona paragraph + sample text); no code released.
- **Replika** — origin story (Mazurenko bot from exported Telegram chats) documented, but current models proprietary.
- **MIT Future You** — academic paper describing the system-prompt/questionnaire design.
- **Commercial griefbots (HereAfter, YOV, StoryFile, DeepBrain, Seance, Afterlife, 2wai, Sensay)** — **none** publish prompts or architectures; all are black boxes.

## Cross-cutting lessons for a DIY local build

1. **Capture first, model later**: the scarce asset is consensual, structured self-recordings (question-bank interviews à la StoryFile/HereAfter) — models will keep improving, data won't.
2. **Hybrid retrieval + generation**: verbatim playback for known topics, clearly-labeled generative persona for the rest.
3. **LoRA fine-tune on dyadic chat history** (both sides of the conversation), 14B+ base, QLoRA fits on a single consumer GPU; scrub PII before training (WeClone pattern).
4. **Editable memory objects** (Personal.ai pattern) for facts/beliefs; fine-tune only for *style*, not facts — facts change, style doesn't.
5. **Run local**: Project December's death shows provider ToS is the single biggest platform risk in this category.
6. **Design for closure and consent**: bounded-session framing (Seance AI), opt-in capture (Afterlife AI), exportable artifacts (Sensay) are the features that differentiate ethically defensible builds.
