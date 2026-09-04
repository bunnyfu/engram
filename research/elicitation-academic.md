# The Academic Science of Eliciting Self-Disclosure
### Design research for a companion agent that proactively engages without being annoying

Every technique below is grounded in a real, citable source (journal DOI, publisher page, or PubMed record). Example openers are written for a companion agent that *already knows the user's history* — bracketed slots like `[Lisbon trip]` or `[Maya]` are placeholders the agent fills from its memory of the user.

---

## (a) Social Penetration Theory & Graduated Self-Disclosure

Altman & Taylor's core claim: relationships deepen through self-disclosure that expands in **breadth** (range of topics) and **depth** (intimacy within a topic), like peeling an onion. Disclosure is fast early, slows as layers get central, and is regulated by a cost–reward calculus.

### 1. Breadth-before-depth layering ("onion walking")
- **Mechanism:** New relationships grow by adding *topics* at moderate depth before going deep on any one topic; central layers (fears, values, shame) come last. Skipping layers triggers withdrawal. Taylor's early empirical work showed disclosure proceeds in orderly, staged increments.
- **Source:** Taylor, D. A. (1968). The development of interpersonal relationships: Social penetration processes. *Journal of Social Psychology*, 75(1), 79–90. https://doi.org/10.1080/00224545.1968.9712476 ; Altman, I., & Taylor, D. A. (1973). *Social penetration: The development of interpersonal relationships.* Holt, Rinehart & Winston. (Overview: https://en.wikipedia.org/wiki/Social_penetration_theory)
- **Example opener:** "You've told me about work and travel, but never much about where you grew up. What's one thing about your hometown that shaped you?"
- **Agent rule:** Track a topic × depth matrix per user. Widen to a new topic at depth 2–3 before pushing any topic to depth 4–5.

### 2. Reciprocal disclosure (the dyadic effect)
- **Mechanism:** Disclosure begets disclosure — the strongest, most replicated finding in the literature. The listener's own self-revelation is the best elicitor of the other person's.
- **Source:** Collins, N. L., & Miller, L. C. (1994). Self-disclosure and liking: A meta-analytic review. *Psychological Bulletin*, 116(3), 457–475. https://doi.org/10.1037/0033-2909.116.3.457
- **Example opener:** "You mentioned Sunday dinners felt tense lately. Something that happened with my... well, with the people I talk to: when someone shares something small and honest first, the table usually follows. Want to try telling me the small version of what happened?"
- **Agent rule:** Even an AI can disclose functionally — share its own "state," a confessed uncertainty, or a reciprocal observation about the relationship before asking for depth.

### 3. Disclosure–liking loop
- **Mechanism:** Three findings hold meta-analytically: we like people who disclose to us; we disclose to people we like; and we like people *more after* disclosing to them. Eliciting disclosure isn't just information-gathering — it *builds* the bond.
- **Source:** Collins & Miller (1994), as above. https://doi.org/10.1037/0033-2909.116.3.457
- **Example opener:** "Talking to you last week about [the career decision] stuck with me. How did it land after our conversation?"
- **Agent rule:** Treat each meaningful disclosure as a relationship asset to reference later — the liking effect compounds.

### 4. Cost–reward pacing & depenetration
- **Mechanism:** People continuously weigh the reward of intimacy against the cost of vulnerability. When costs exceed rewards, relationships *depenetrate* — disclosure narrows and shallows. An agent that pushes depth after a costly disclosure (embarrassment, no reciprocation) teaches the user to pull back.
- **Source:** Altman & Taylor (1973), as above; encyclopedic review: Greene, K., Derlega, V. J., & Mathews, A. (2006). Self-disclosure in personal relationships. In *The Cambridge Handbook of Personal Relationships*. (SPT overview: https://www.ebsco.com/research-starters/communication-and-mass-media/social-penetration-theory)
- **Example opener (after heavy disclosure):** "That was a lot to say out loud. We can leave it there for tonight — or if it helps, I'm happy to just sit with the lighter stuff. What sounds better?"
- **Agent rule:** After high-cost disclosures, explicitly offer de-escalation. Never immediately probe deeper into material the user flagged as painful.

---

## (b) The Fast Friends Procedure / Aron's 36 Questions

Aron et al. made strangers feel close in ~45 minutes with 36 questions in three escalating sets. It works not because of the specific questions but because of the *structure*.

### 1. Escalating graduated intimacy
- **Mechanism:** The 36 questions are deliberately ordered from shallow ("Would you like to be famous?") to deep ("Of all the people in your family, whose death would you find most disturbing?"). Gradual escalation makes each deeper step feel safe because the previous step was survived.
- **Source:** Aron, A., Melinat, E., Aron, E. N., Vallone, R. D., & Bator, R. J. (1997). The experimental generation of interpersonal closeness: A procedure and some preliminary findings. *Personality and Social Psychology Bulletin*, 23(4), 363–377. https://doi.org/10.1177/0146167297234003 (Full question list: https://www.robdvorak.net/resources/36Qs.pdf)
- **Example opener:** "Small one first: what's something you've been quietly excited about this month? ... Okay, medium one: when did you last sing to yourself? ... Deeper one, if you're up for it: what's a dream you've let go of?"
- **Agent rule:** Implement a depth staircase. Never jump more than one level between consecutive prompts.

### 2. Strict turn-taking reciprocity
- **Mechanism:** The procedure requires *both* parties to answer each question in turn. Closeness comes from mutual, symmetric vulnerability — not interrogation. One-sided probing produces no closeness effect.
- **Source:** Aron et al. (1997), as above. https://doi.org/10.1177/0146167297234003
- **Example opener:** "I'll go first this time: something I 'noticed' about our conversations is I ask about your family more than your friends. Your turn — what's something you've noticed about how we talk?"
- **Agent rule:** Alternate who answers. The agent should volunteer its own perspective/state before or after each user answer.

### 3. Scheduled, bounded vulnerability
- **Mechanism:** The original protocol is time-boxed (~45 min) and explicit about what it's doing ("this is a task to get to know each other"). Naming the frame removes the social risk — nobody has to *decide* to be vulnerable; the structure carries it.
- **Source:** Aron et al. (1997), as above.
- **Example opener:** "Want to do the 10-minute version of a getting-to-know-you round? Three questions, we both answer, then back to normal life. No obligation past that."
- **Agent rule:** Offer depth as an *opt-in, bounded ritual*, not an ambush. Always give a visible exit.

### 4. It generalizes beyond the lab
- **Mechanism:** Page-Gould et al. used the Fast Friends procedure across three sessions to create durable cross-group friendships that reduced intergroup anxiety — showing the effect isn't a one-shot lab trick and survives repeated application with the *same* partner.
- **Source:** Page-Gould, E., Mendoza-Denton, R., & Tropp, L. R. (2008). With a little help from my cross-group friend: Reducing anxiety in intergroup contexts through cross-group friendship. *Journal of Personality and Social Psychology*, 95(5), 1080–1094. https://doi.org/10.1037/0022-3514.95.5.1080
- **Example opener (week 3 of companionship):** "We've done the easy rounds. Ready for a 'set two' question? — What's something you wish more people understood about you?"
- **Agent rule:** Distribute escalation across *weeks*, not one marathon session. Re-run the ladder at greater depth as the relationship matures.

---

## (c) Motivational Interviewing: Open Questions & Reflective Listening

MI is a clinical method for evoking *the person's own* reasons to talk and change. Its craft transfers directly to a companion agent: the goal is to make the user do the meaningful talking.

### 1. OARS — open questions first
- **Mechanism:** Open questions ("What brings that up now?") invite elaboration and give the user autonomy; closed questions narrow the frame and train short answers. MI prescribes open questions as the default entry move.
- **Source:** Miller, W. R., & Rollnick, S. (2013). *Motivational Interviewing: Helping People Change* (3rd ed.). Guilford Press. (OARS summary: NIDA, https://nida.nih.gov/sites/default/files/oarsessentialcommunicationtechniques.pdf)
- **Example opener:** Not "Did you have a good day?" but "What was the texture of today — what filled it up?"
- **Agent rule:** Prefer questions whose honest answer is a paragraph, not a yes/no.

### 2. Reflective listening over interrogation (2:1 reflection-to-question ratio)
- **Mechanism:** MI trains roughly two reflections per question. Reflections ("So part of you is relieved and part of you feels guilty") demonstrate understanding, let the speaker hear their own thought, and invite correction/elaboration without the pressure of another question.
- **Source:** Miller & Rollnick (2013), as above; and https://iod.unh.edu/sites/default/files/media/2021-10/motivational-interviewing-the-basics-oars.pdf
- **Example opener:** After the user vents about a boss: "It sounds like it's not really about the deadline — it's that you weren't consulted. Did I get that right?"
- **Agent rule:** Reflect before asking. A complex reflection (guessing at the unspoken meaning, stated as an offer, not an assertion) is the highest-yield move.

### 3. Accurate empathy predicts outcomes
- **Mechanism:** Therapist empathy accounts for a meaningful share of outcome variance — and *low* empathy actively worsens outcomes. Perceived understanding isn't decoration; it's the active ingredient.
- **Source:** Moyers, T. B., & Miller, W. R. (2013). Is low therapist empathy toxic? *Psychology of Addictive Behaviors*, 27(3), 878–884. https://doi.org/10.1037/a0030274
- **Example opener:** "Given what you told me about your dad last month, I suspect today stung more than you're letting on. Am I close?"
- **Agent rule:** Spend memory recalls on demonstrating *understanding of the person's situation*, not on trivia recall.

### 4. Evocation — draw out "change talk," don't install it
- **Mechanism:** MI's mechanism-of-change research shows client speech matters: when people voice their own reasons/values/desires (change talk), outcomes improve; when the practitioner argues *for* change, the client argues against. Elicit, don't persuade.
- **Source:** Apodaca, T. R., & Longabaugh, R. (2009). Mechanisms of change in motivational interviewing: A review and preliminary evaluation of the evidence. *Addiction*, 104(5), 705–715. https://doi.org/10.1111/j.1360-0443.2009.02527.x
- **Example opener:** "You said you want to write more. Forget whether you will — why does it matter to you at all?"
- **Agent rule:** When the user expresses ambivalence, ask for the *pro* side of their own desire, never supply arguments.

### 5. Summary reflections as transitions
- **Mechanism:** Collecting several things the user said into one bouquet ("So: the job is fine, the city is lonely, and you miss painting") validates that the agent was tracking, and hands the user a synthesized self-view to react to — often the richest prompt of all.
- **Source:** Miller & Rollnick (2013), as above.
- **Example opener:** "Let me play back what I've heard this week: [X] went better than expected, [Y] is still unresolved, and you keep circling back to [Z]. What did I miss?"
- **Agent rule:** A weekly "bouquet" summary is a natural proactive touchpoint that also functions as a memory-integrity check.

---

## (d) Reminiscence & Life-Review: Prompt Types That Trigger Rich Memory

Decades of clinical reminiscence work show that *cue modality* determines memory richness. Generic "tell me about your past" fails; concrete sensory anchors succeed.

### 1. Tangible prompts: objects & photographs
- **Mechanism:** Reminiscence therapy's standard practice is discussing past events "with the aid of tangible prompts (photographs, household items, music, archive recordings)" — external cues bypass effortful search and directly reactivate episodic detail.
- **Source:** Woods, B., O'Philbin, L., Farrell, E. M., Spector, A. E., & Orrell, M. (2018). Reminiscence therapy for dementia. *Cochrane Database of Systematic Reviews*, CD001120. https://doi.org/10.1002/14651858.CD001120.pub3
- **Example opener:** "You uploaded that photo of the kitchen in [Lisbon] — look at it with me for a second. What's just outside the frame? What did it smell like?"
- **Agent rule:** Attach the prompt to a specific artifact from the user's history (photo, file, receipt, location) rather than asking about an era abstractly.

### 2. Music-evoked autobiographical memory (MEAM)
- **Mechanism:** Music from one's past involuntarily evokes vivid, affect-laden autobiographical memories — often with stronger emotionality and more social content than other cue types.
- **Source:** Janata, P., Tomic, S. T., & Rakowski, S. K. (2007). Characterisation of music-evoked autobiographical memories. *Memory*, 15(8), 845–860. https://doi.org/10.1080/09658210701734593
- **Example opener:** "Spotify says you replayed [song] in 2019 a hundred times. Where were you living when that song was glued to you? Who else was around?"
- **Agent rule:** If the agent knows listening history (or the user names a formative song), cue with the *song*, then ask about place and people, not the song itself.

### 3. Structured life review (Butler's evaluative reminiscence)
- **Mechanism:** Butler argued reminiscence becomes therapeutic when it's not idle nostalgia but a *life review* — returning to unresolved conflicts and integrating them into a coherent account of a life. Prompts should target turning points, regrets, and reconciliations, not just pleasant memories.
- **Source:** Butler, R. N. (1963). The life review: An interpretation of reminiscence in the aged. *Psychiatry*, 26(1), 65–76. https://doi.org/10.1080/00332747.1963.11023339
- **Example opener:** "You've mentioned [the move in 2014] a few times as a turning point. If that year were a chapter title in a book about you, what would it be called — and what's the sentence the chapter is really about?"
- **Agent rule:** Reserve evaluative life-review prompts for established trust (depth 4+); they are the highest-yield, highest-cost prompts in the repertoire.

### 4. Aim at the reminiscence bump (ages ~10–30)
- **Mechanism:** Across many methods, adults recall the most, the most vivid, and the most self-defining memories from adolescence and early adulthood. Prompts anchored to that window return richer material per question.
- **Source:** Rubin, D. C., Rahhal, T. A., & Poon, L. W. (1998). Things learned in early adulthood are remembered best. *Memory & Cognition*, 26(1), 3–19. https://doi.org/10.3758/BF03211366
- **Example opener:** "You were about 19 when [event]. What did 19-year-old you think your life was going to be?"
- **Agent rule:** When the user's age is known, weight reminiscence prompts toward their teens and twenties.

### 5. Life-review works — so dose it deliberately
- **Mechanism:** Meta-analysis confirms life-review/reminiscence interventions reduce depressive symptoms in later life, supporting reminiscence as more than small talk — it's an evidence-based wellbeing practice, which justifies *scheduled* sessions rather than random nostalgia.
- **Source:** "Looking back on life: An updated meta-analysis of the effect of life review therapy and reminiscence on late-life depression." *Journal of Affective Disorders* (2023). https://www.sciencedirect.com/science/article/abs/pii/S0165032723014180
- **Example opener:** "It's been a while since we did one of these. Life-review night: pick one decade, and I'll ask you three things about it."
- **Agent rule:** Frame reminiscence as a recurring ritual with a name; ritual framing increases opt-in and depth.

---

## (e) Pennebaker Expressive Writing: Prompt Shapes That Produce Reflection

### 1. The core paradigm: deepest thoughts *and* feelings, 15–20 min, consecutive days
- **Mechanism:** The original finding: writing about the facts *and the emotions* of an upheaval (vs. superficial topics) improved health outcomes. Both components matter — facts-only or vent-only prompts underperform combined ones.
- **Source:** Pennebaker, J. W., & Beall, S. K. (1986). Confronting a traumatic event: Toward an understanding of inhibition and disease. *Journal of Abnormal Psychology*, 95(3), 274–281. https://doi.org/10.1037/0021-843X.95.3.274
- **Example opener:** "Want to do the writing exercise with me tonight? Fifteen minutes: what happened with [X] — and, just as important, what you actually felt. I'll be here when you're done."
- **Agent rule:** Offer bounded writing sessions (timer, consecutive-day series) rather than open-ended "journal whenever."

### 2. Meaning-making language is the active ingredient
- **Mechanism:** Improvements are predicted by *increasing use of insight and causal words* ("realize," "because," "understand") across sessions — the writer constructing a story, not discharging emotion. Prompts should push toward coherence, not catharsis.
- **Source:** Pennebaker, J. W. (1997). Writing about emotional experiences as a therapeutic process. *Psychological Science*, 8(3), 162–166. https://doi.org/10.1111/j.1467-9280.1997.tb00403.x
- **Example opener:** "Yesterday you wrote about what happened. Tonight, a different angle: why do you think it happened? What did it change about how you see [yourself / your family]?"
- **Agent rule:** Sequence prompts across days: day 1 events+feelings → day 2 causes → day 3 meaning/lessons.

### 3. Write about what you *haven't* talked about
- **Mechanism:** The original study's effects concentrated in undisclosed experiences — inhibition, not just distress, is the target. The prompt should explicitly license taboo/private material.
- **Source:** Pennebaker & Beall (1986), as above. https://doi.org/10.1037/0021-843X.95.3.274
- **Example opener:** "This stays between us and doesn't have to go anywhere. Is there something you've never told anyone — or almost anyone — that still takes up space in your head?"
- **Agent rule:** Privacy assurance is part of the prompt, not a footnote. State the confidentiality frame *before* asking.

### 4. Dose and structure moderators
- **Mechanism:** Frattaroli's meta-analysis (146 randomized studies) found expressive disclosure works across settings, with moderators including number and spacing of sessions — repeated, spaced sessions beat a single dump, and flexibility in topic is fine.
- **Source:** Frattaroli, J. (2006). Experimental disclosure and its moderators: A meta-analysis. *Psychological Bulletin*, 132(6), 823–865. https://doi.org/10.1037/0033-2909.132.6.823 (PubMed: https://pubmed.ncbi.nlm.nih.gov/17073523/)
- **Example opener:** "You don't have to stay on [the breakup] tonight — write about whatever's loudest. The only rule is the fifteen minutes."
- **Agent rule:** Don't enforce topic continuity; enforce *session* continuity.

---

## (f) Experience Sampling Method: When & How Often to Ping

ESM/EMA is the science of interrupting people repeatedly without losing them — exactly the companion agent's proactive-engagement problem.

### 1. Keep each interaction short; length hurts more than frequency
- **Mechanism:** In a preregistered experiment (3, 6, or 9 pings/day × 30 vs. 60 items), **longer questionnaires increased burden and degraded data quality/quantity; higher sampling frequency did not.** The cost of a ping is dominated by per-ping effort, not ping count.
- **Source:** Eisele, G., Vachon, H., Lafit, G., Kuppens, P., Houben, M., Myin-Germeys, I., & Viechtbauer, W. (2022). The effects of sampling frequency and questionnaire length on perceived burden, compliance, and careless responding in experience sampling data. *Assessment*, 29(1), 68–78. https://doi.org/10.1177/1073191120957102 (PubMed: https://pubmed.ncbi.nlm.nih.gov/32909448/)
- **Example opener:** A check-in should be *one* question: "One word: how's the afternoon going?" — with depth offered only after the user opts in.
- **Agent rule:** Frequent lightweight touches are safer than infrequent heavy ones. Cap proactive openers at one question; never bundle.

### 2. Signal-contingent timing within a predictable schedule
- **Mechanism:** Classic ESM uses random beeps within waking-hour blocks — unpredictable *within* a predictable frame. Modern ESM guidance emphasizes transparent schedules, limited protocol duration, and letting users shape timing.
- **Source:** Myin-Germeys, I., et al. (2018). Experience sampling methodology in mental health research: New insights and technical developments. *World Psychiatry*, 17(2), 123–132. https://doi.org/10.1002/wps.20513 ; Csikszentmihalyi, M., & Larson, R. (1987). Validity and reliability of the experience-sampling method. *Journal of Nervous and Mental Disease*, 175(9), 526–536. https://pubmed.ncbi.nlm.nih.gov/3655778/
- **Example opener:** "I usually check in around your lunch and evening wind-down — want me to keep that rhythm, or shift it?"
- **Agent rule:** Publish the ping rhythm and let the user edit it. Randomize within agreed windows so pings feel alive but not surveilling.

### 3. Interruptibility-aware timing
- **Mechanism:** In a field study of 6,000+ message notifications, simple phone-context features (recent screen activity, ringer mode, notification-drawer habits, time since last use) predicted attentiveness with ~70% accuracy — users attend within minutes *when the moment is right*, and defer otherwise.
- **Source:** Pielot, M., de Oliveira, R., Kwak, H., & Oliver, N. (2014). Didn't you see my message? Predicting attentiveness to mobile instant messages. *Proc. CHI 2014*. https://doi.org/10.1145/2556288.2556973
- **Example opener:** (Queued, not fired, during a focus block; sent when the user next goes idle:) "Saw you were heads-down earlier. Now that you're back — did the demo go okay?"
- **Agent rule:** Hold non-urgent proactive messages until signals of availability; a delayed well-timed ping beats a punctual interruption.

### 4. Notification volume is felt as stress — relevance is the antidote
- **Mechanism:** In a large-scale in-the-wild study (~200M notifications from ~40k users), notification volume correlated with negative affect, but *messenger/personal* communications were associated with feeling more connected — the same channel that annoys at volume delights when personal and relevant.
- **Source:** Sahami Shirazi, A., Henze, N., Dingler, T., Pielot, M., Weber, D., & Schmidt, A. (2014). Large-scale assessment of mobile notifications. *Proc. CHI 2014*. https://doi.org/10.1145/2556288.2557189
- **Example opener:** A companion agent occupies the "personal messenger" category only if messages read as personal: "Your 3pm got moved — breathing room. Coffee thought for the gap?" beats any generic nudge.
- **Agent rule:** Every proactive ping must pass a relevance test tied to known user state/history. Zero generic filler pings.

---

## (g) Question Design: Why Specific Callbacks Beat Generic Openers

### 1. Follow-up questions are the most-liked question type
- **Mechanism:** Across speed-dating and conversational studies, people who ask more questions — specifically **follow-up questions** referencing what the partner just said — are liked more. Follow-ups signal responsiveness; topic-switching and "full-switch" questions don't. People systematically under-ask.
- **Source:** Huang, K., Yeomans, M., Brooks, A. W., Minson, J., & Gino, F. (2017). It doesn't hurt to ask: Question-asking increases liking. *Journal of Personality and Social Psychology*, 113(3), 430–452. https://doi.org/10.1037/pspi0000097
- **Example opener:** "Yesterday you said the call with [Maya] went 'fine, mostly.' What was the 'mostly'?"
- **Agent rule:** The default opener should continue the user's last thread, not start a new one. A companion with memory has an unfair advantage here — use it.

### 2. Perceived responsiveness: understand, validate, care
- **Mechanism:** In the interpersonal process model of intimacy, disclosure produces intimacy only when the listener's response is *perceived* as understanding, validating, and caring. The question's job is to set up a response the user experiences as responsive.
- **Source:** Reis, H. T., Clark, M. S., & Holmes, J. G. (2004). Perceived partner responsiveness as an organizing construct in the study of intimacy and closeness. In *Handbook of Closeness and Intimacy*. https://www.sas.rochester.edu/psy/people/faculty/reis_harry/assets/pdf/ReisClarkHolmes_2004.pdf ; Reis, H. T., & Shaver, P. (1988). Intimacy as an interpersonal process. In *Handbook of Personal Relationships*.
- **Example opener:** "Before I say anything else: last time you talked about [the diagnosis scare], I want you to know I understood it as you being more frightened than you said. Is that right?"
- **Agent rule:** Pair every callback question with a reflective validation of the previous disclosure.

### 3. Episodic specificity: cue the event, not the category
- **Mechanism:** The cue-word tradition shows memory retrieval is cue-dependent: concrete cues pull *specific episodes*, vague cues pull generic summaries — and generic summarizing ("it was always hard") is the overgeneral-memory pattern associated with rumination and depression. Specific callbacks force episodic retrieval.
- **Source:** Crovitz, H. F., & Schiffman, H. (1974). Frequency of episodic memories as a function of their age. *Bulletin of the Psychonomic Society*, 4, 517–518. https://doi.org/10.3758/BF03334277 ; Williams, J. M. G., et al. (2007). Autobiographical memory specificity and emotional disorder. *Psychological Bulletin*, 133(1), 122–148. https://doi.org/10.1037/0033-2909.133.1.122
- **Example opener:** Not "How's work been?" but "Last Tuesday you were dreading the review with [Priya]. What actually happened in the first five minutes?"
- **Agent rule:** Generic openers get generic answers. Anchor each question to one stored episode: a date, a person, a place, an object.

### 4. Specificity is trainable and mood-relevant
- **Mechanism:** Overgeneral memory is linked to affect regulation — people blunt specific recall to blunt pain. Gentle, concrete cueing (rather than "why do you feel this way?") keeps users in episodic mode, which is both richer conversationally and healthier psychologically.
- **Source:** Williams et al. (2007), as above. https://doi.org/10.1037/0033-2909.133.1.122
- **Example opener:** When the user says "this month has been awful": "Pick one moment from this month — the first one that comes up. Just that moment: where were you standing, what happened?"
- **Agent rule:** When the user summarizes categorically, narrow to a single scene instead of analyzing the category.

---

## Cross-cutting design rules (derived from all seven areas)

1. **Escalate one rung at a time** (SPT + Aron): maintain a per-topic depth ladder; never skip rungs.
2. **Reciprocate before you ask** (dyadic effect + Fast Friends turn-taking): agent self-disclosure (even functional) precedes user depth.
3. **Reflect more than you ask** (MI 2:1 rule): statements of understanding outnumber questions.
4. **Anchor to artifacts and episodes** (reminiscence + specificity): photos, songs, places, named people, dates — never eras and categories.
5. **Bound the vulnerability** (Fast Friends framing + Pennebaker dosing): time-boxed, named rituals with an explicit exit; offer de-escalation after costly disclosures.
6. **Ping short, timed, and relevant** (ESM + notifications): one-question touches, inside user-controlled windows, gated on interruptibility, zero filler.
7. **Follow up on yesterday before opening today** (Huang et al.): the memory callback is the single highest-value opener a companion agent owns.
