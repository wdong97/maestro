# Writing Framework

Use this reference only when the main skill asks for deeper support: multi-section website or landing page copy, sales or offer critique, cold outreach, lifecycle email, social post/thread work, CRO critique, or full humanization passes.

The operational contract lives in `SKILL.md`: modes, output schemas, quality gate, edit-in-place rules, and safety guardrails. This file provides practical patterns and checks.

## Product Context

Before asking foundational product, audience, positioning, offer, or voice questions, use existing context when present:

- `.agents/product-marketing.md`
- `.claude/product-marketing.md`
- `.codex/product-marketing.md`
- `.agents/product-marketing-context.md`
- `.claude/product-marketing-context.md`
- `.codex/product-marketing-context.md`

Useful context: product category, target audience, jobs to be done, pain points, alternatives, differentiation, objections, switching anxieties, customer language, brand voice, proof points, business goal, and conversion action.

## Proof Handling

Never keep a strong claim just because it sounds good. Triage every claim:

- Substantiate: add a metric, testimonial, customer, demo, screenshot, study, or named example.
- Soften: replace certainty with a narrower, supportable claim.
- Convert to mechanism: explain how the outcome happens instead of asserting the outcome.
- Make conditional: show who it works for, when, or under what constraint.
- Remove: cut claims that cannot be supported and do not help the reader decide.
- Ask: request evidence before writing case-study, "trusted by," quantified, health, financial, legal, or safety claims.

## Website And Landing Pages

Use this structure when the user wants a page, hero, or CRO rewrite:

- Hero: headline, subhead, primary CTA, secondary CTA when useful, proof cue.
- Problem/context: show the reader you understand the current state.
- Promise/mechanism: explain the specific outcome and how the product gets them there.
- Benefits: 3-5 outcomes, not feature dumps.
- Proof: testimonials, logos, numbers, demos, examples, screenshots, or case studies near claims.
- Objections: price, fit, switching, time, implementation, trust, and risk.
- Final CTA: repeat the value and reduce uncertainty about the next step.

Page-specific checks:

- Homepage: clear positioning for cold visitors and paths for different intents.
- Landing page: one audience, one promise, one primary CTA, strong traffic-source match.
- Pricing page: reduce "which plan is right for me?" anxiety and clarify the default choice.
- Feature page: feature to benefit to outcome, with examples and proof.
- About page: story in service of customer trust, not company autobiography.

CRO critique should separate quick wins, high-impact changes, test ideas, and copy alternatives.

## Offer Critique

If the copy is trying to sell but the offer feels weak, diagnose the offer before polishing language.

Use the value equation:

```text
Value = (Dream outcome x Perceived likelihood of achievement) / (Time delay x Effort and sacrifice)
```

Check:

- Audience: who is this clearly for?
- Promise: what concrete result is being offered?
- Mechanism: why should this work?
- Proof: what makes the promise believable?
- Risk reversal: guarantee, trial, demo, preview, clear expectations, or cancellation terms.
- Friction: price confusion, effort, setup, switching, decision complexity.
- Urgency: real reason to act now, or omit urgency.
- Packaging: name, deliverables, tiers, bonuses, payment structure.
- Smallest improvement: the one offer component most likely to lift conversion.

Do not fix a weak offer by inflating copy.

## Email And Outreach

### Cold Outreach

Write like a peer who noticed something relevant.

- Lead with the recipient's world, not your company intro.
- Personalization must connect to the problem.
- Keep one low-friction ask, usually interest-based rather than a calendar demand.
- Use short, boring, internal-looking subject lines.
- One proof point beats a feature dump.
- Avoid fake "Re:" or "Fwd:", multiple links, images, "I hope this finds you well," and "just checking in."

Common shape:

```text
Observation or trigger
Problem it usually implies
Relevant proof or mechanism
Low-friction ask
```

### Lifecycle Email

One email, one job.

- Trigger: what caused this email?
- Audience state: what do they know or believe now?
- Job: activate, educate, reassure, recover, upsell, renew, or win back.
- Value: give before asking when the relationship is early.
- CTA: one primary next step.

Common sequences: welcome, nurture, onboarding, re-engagement, post-purchase, usage, billing, and campaign emails.

## Social And Posts

Use social writing when the goal is distribution, audience-building, launch support, or founder/company voice.

Patterns:

- Point of view: claim, reason, example, implication.
- Founder post: lived observation, specific lesson, what changed.
- Product launch: who it is for, what changed, why now, proof, next step.
- Tactical thread: problem, steps, example, caveat, CTA.
- Contrarian take: common belief, disagreement, evidence, practical takeaway.
- Proof-led post: result, context, mechanism, lesson, next action.

Avoid engagement bait, fake vulnerability, generic inspirational endings, over-polished LinkedIn voice, and claims without context.

## Humanization

Humanization should preserve meaning, not merely make prose casual.

Preserve:

- Facts and numbers.
- Level of certainty.
- Named entities.
- Technical meaning.
- Author stance.
- Legal or compliance wording.
- Intentional awkwardness or unusual phrasing that belongs to the voice.

Voice profile to extract from samples:

- Sentence length and rhythm.
- Vocabulary and formality.
- Directness and warmth.
- Humor or edge.
- Punctuation habits.
- Paragraph shape.
- Phrases to use or avoid.
- Allowed imperfections.

High-signal AI tells:

- Vague hype: powerful, seamless, robust, next-level, unlock, elevate.
- Fake authority: experts agree, widely recognized, industry-leading without proof.
- Chatbot residue: of course, certainly, let's dive in, I hope this helps.
- Over-neat structure: symmetrical lists, forced trios, generic labeled sections.
- Generic endings: vague optimism or "future looks bright."
- Unsupported breadth: "whether you're X or Y" when the audience is narrower.
- Hedge stacks: could potentially, may eventually, might ultimately.
- Placeholder leaks: bracketed instructions, unfinished dates, citation tokens, pasted chat markup.

## Persuasion Checks

Use these as decision checks, not labels to show the user:

- Jobs to Be Done: frame around what the reader is trying to accomplish.
- Status quo bias: make switching feel safe and easy.
- Loss aversion: state the cost of inaction without fearmongering.
- Social proof: use relevant examples from people like the reader.
- Authority: use credible expertise or named proof.
- Paradox of choice: reduce options and recommend a default when helpful.
- Regret aversion: reduce fear through trials, guarantees, previews, or clear expectations.

If a tactic creates pressure without serving the reader's real interest, do not use it.

## Compact Examples

Website:

- Weak: "Unlock seamless workflows for modern teams."
- Better: "Turn scattered client requests into approved tasks before your next standup."
- Why: names the before state, the audience situation, and the concrete outcome.

Offer:

- Weak: "Join the ultimate growth program, worth $10,000."
- Better: "In four weeks, leave with a tested onboarding sequence, three customer-backed offers, and the metrics to know which one is working."
- Why: replaces inflated value with deliverables, timeline, and proof mechanism.

Cold email:

- Weak: "I hope this finds you well. We help teams leverage AI for better outcomes."
- Better: "Saw you're hiring two SDRs. Teams usually do that right before outbound QA gets messy. We helped Acme cut review time by 40%. Worth comparing notes?"
- Why: uses a trigger, problem, proof, and low-friction ask.

Humanization:

- Weak: "In today's evolving landscape, this solution empowers teams to unlock efficiency."
- Better: "Teams lose hours moving the same request between docs, Slack, and Jira. This keeps the request in one place until someone approves it."
- Why: replaces abstraction with a concrete scene and mechanism.
