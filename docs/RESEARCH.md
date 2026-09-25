# Research note — LLD practice (1–2 pages)

## 1. Learner problem

Low-Level Design practice is easy to start and hard to evaluate. A learner can spend an hour designing a Parking Lot or
Elevator system and still not know whether the responsibilities, abstractions, relationships, and trade-offs are good.
From the assignment brief and helping guide, the concrete pains are:

1. **No ground truth, many valid answers.** Two competent designs can look entirely different (e.g. per-floor managers vs
   a central allocator). Learners stall asking “which one is right?” instead of “what trade-off did I make?”.
2. **Feedback is vague or absent.** Peers say “looks good”; interviewers give a score with no evidence. The learner
   cannot tell what to change on the next attempt.
3. **No retained evidence.** Attempts live in notebooks/whiteboards and are lost, so improvement across attempts is
   invisible — there is no learning loop, just one-time solving.
4. **Unclear submission bar.** Learners don’t know what a “complete” attempt contains: requirements mapping,
   assumptions, class contracts, workflows, trade-offs, edge cases.

So the product question is: *what is the smallest submission that proves design thinking, and what is the smallest
feedback that teaches?*

## 2. Existing approaches (from supplied material + general knowledge)

Sources actually used: the two assignment PDFs (brief + helping guide), the supplied CipherSchools platform content /
UI-UX audit, and the 20-point website checklist. No external scraping was performed; the notes below reflect
well-established, verifiable patterns in interview prep and the audit’s observations.

- **Interview-prep content (books/videos):** Parking Lot / Elevator / Vending Machine walkthroughs teach one reference
  solution well but leave the learner unable to self-grade alternatives. Gap: reference-solution anchoring.
- **Course platforms (per the CipherSchools audit):** video + notes + streaks + points drive consistency and
  discipline, but assessment is watch-time/completion, not design quality. Gap: no design judgment; gamification
  measures attendance, not understanding.
- **AI chat feedback (naive “is this good?” prompts):** fluent but inconsistent — scores drift between runs, advice is
  generic, and failures look like answers. The helping guide explicitly warns against unconstrained scoring prompts.
  Gap: no fixed rubric, no evidence requirement, no failure honesty.
- **Human review (paid mocks, Discord Q&A per the audit’s community model):** high quality but slow, expensive, and
  unscalable for daily practice. Gap: turnaround time kills the retry loop.

## 3. Key gaps → product direction

| Gap | Direction taken |
|---|---|
| Many valid designs, one reference answer | Rubric over resemblance: score responsibilities, coupling, interfaces, trade-offs with evidence quoted from the submission; state explicitly that alternatives can score well. |
| Vague scores | Fixed shape per criterion: score → evidence → concern → suggestion → confidence. |
| Inconsistent AI | Separate deterministic checks (required fields, lengths, state transitions, idempotency) from judgment; deterministic rule-based evaluator by default; LLM only where reasoning helps, behind schema validation + timeouts + honest failed states. |
| Lost attempts | Persist every submission before evaluation; full history; retry clones to a new draft so progress is visible. |
| Unclear submission bar | Six-section structured text format (assumptions, classes, interfaces, workflows, trade-offs, edge cases) — enough evidence with minimal tooling; code/diagram left as documented extension points. |

Out of scope on purpose: authentication, payments, LMS features, diagram editors, microservices/Kafka — none of them
shorten the practice loop for a 2-day MVP.
