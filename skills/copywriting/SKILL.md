---
name: copywriting
description: Write, rewrite, critique, scan, humanize, and edit persuasive, marketing, sales, outreach, lifecycle, social, website, product-facing, or voice-sensitive copy. Use for conversion, positioning, proof, offers, CTAs, headlines, customer-facing clarity, or removing AI-writing tells. Not for code, code comments, commit messages, API/reference docs, agent prompts, or ordinary internal notes unless the user explicitly asks for persuasion, voice, or customer-facing polish.
---

# Copywriting

## Overview

Use this skill for both creating writing from scratch and improving writing that already exists. The writing should be clear, persuasive when persuasion is appropriate, and recognizably human. Keep the work ethical: make the reader's next step clearer without lying, hiding material tradeoffs, inventing proof, manufacturing scarcity, or flattening the author's voice.

## Core Workflow

1. Identify the surface: website, landing page, product UI, email, ad, post, outreach, offer, headline, CTA, or other customer-facing prose.
2. Check for existing product-marketing context before asking for basics.
3. Identify the reader, their current belief, the desired belief, the message, the action, and the proof available.
4. Pick the primary job using the mode rules below.
5. Choose the right structure for the surface:
   - Websites and landing pages: headline, subhead, proof, outcome, objections, CTA, scannable sections.
   - Product UI: concise labels, clear states, useful errors, action-oriented CTAs.
   - Emails and outreach: relevant opener, reason, value, proof, low-friction ask.
   - Social posts: point of view, concrete detail, rhythm, credible examples, clean ending.
6. Use the quick workflow for small requests. Read `references/writing-framework.md` only when the criteria in the References section apply.
7. For existing writing, choose the lightest edit that solves the problem. Preserve strong human passages.
8. Cut corporate filler, unsupported claims, fake urgency, generic AI tone, and anything that makes the reader work harder than needed.
9. Run the compact quality gate below before returning.
10. Return usable writing first. Add rationale, issue lists, or variants only when helpful.

## Context Discovery

Before asking foundational product, audience, positioning, offer, or voice questions, check for:

- `.agents/product-marketing.md`
- `.claude/product-marketing.md`
- `.codex/product-marketing.md`
- `.agents/product-marketing-context.md`
- `.claude/product-marketing-context.md`
- `.codex/product-marketing-context.md`

If one exists, use it and only ask for task-specific gaps. If none exists, continue from the user's supplied context and ask only the smallest useful set of questions.

## Mode Rules

- `write`: create new text from notes, goals, or rough context.
- `update`: improve existing text while preserving intent and any strong voice.
- `critique`: diagnose weak writing and provide concrete fixes.
- `scan`: identify issues without rewriting when the user says scan, detect, flag only, or just tell me what is wrong.
- `edit-in-place`: update a named local file only when the user explicitly asks to rewrite or clean up copy in that file.
- `humanize`: remove AI-sounding patterns while preserving meaning, proof, and author voice.
- `variants`: generate options for headlines, hooks, CTAs, openers, sections, or angles. Default to 3 variants unless the user specifies a count.

If modes conflict, preserve the user's requested artifact first. For example, if they ask "make this better," return the improved version before explaining issues. If they ask "audit only," do not rewrite unless they later ask for it.

Treat "audit" as `scan` unless the user asks for fixes, recommendations, conversion improvements, or a rewrite; then use `critique` or `update`.

Default to `update` when the user provides existing copy with no explicit mode. Default to `write` when the user provides only goals, notes, or a brief.

Mode decision table:

- `audit only` / `scan only` / `flag only`: `scan`, no rewrite.
- `review this` / `why is this not working` / `recommend fixes`: `critique`.
- `make this better` / `rewrite this` / `humanize this`: `update` or `humanize`.
- `fix this file` / `edit this page copy in file`: `edit-in-place`.
- `give me options` / `make variants`: `variants`.

## Information To Gather

If the user provides enough context, proceed directly. If context is missing and assumptions would materially change the copy, ask for the smallest useful set of facts:

- Reader: who is reading and what they already believe.
- Surface: website, UI, email, ad, post, outreach, offer, headline, CTA, etc.
- Goal: inform, persuade, sell, explain, reassure, onboard, recover, invite, reply, subscribe, click, start trial, etc.
- Offer or message: what is being sold, requested, explained, or changed.
- Proof: testimonials, metrics, credentials, demos, case studies, reviews.
- Offer strength: dream outcome, likelihood of success, time to value, effort or sacrifice required.
- Voice sample: 2-3 paragraphs from the author when the user wants personal voice matching.
- Constraints: tone, format, channel, length, prohibited claims, compliance limits.

When context is incomplete but the task is low-risk, state the assumptions briefly and continue.

Ask before proceeding when missing context would change the copy materially:

- Ask for audience before cold outreach or role-specific landing page copy.
- Ask for proof before writing case-study, "trusted by," or quantified outcome claims.
- Ask for compliance constraints before health, financial, legal, safety, or regulated claims.
- Proceed with assumptions for low-risk headline, CTA, tone, or short variant work.

## Output Patterns

For writing, updating, rewriting, or humanizing, return:

- `Version`: polished copy.
- `What changed`: concise bullets tied to reader belief, clarity, voice, proof, and objections.
- `Remaining proof gaps`: only include when claims need substantiation.
- `Alternatives`: only include when the user asks for options or the channel benefits from variants.
- `Second-pass audit`: only include when the user asks for AI cleanup, high polish, or verification of the rewrite.

For critique, return:

- `Highest-impact fixes`: ordered by conversion risk.
- `Line edits`: quote short snippets only as needed, then rewrite.
- `Missing proof or claims`: list what must be substantiated.
- `Suggested rewrite`: include a usable replacement when possible.

For scan mode, return:

- `Clear problems`: issues worth fixing.
- `Judgment calls`: patterns that may be intentional or contextually fine.
- `Highest-impact fixes`: the shortest path to better writing, without rewriting unless the user asks.

For variants mode, return:

- `Variants`: default 3 options unless the user specifies another count.
- `Best pick`: the strongest option and why.
- `Tradeoffs`: only include when options serve meaningfully different angles.

For edit-in-place mode, return:

- `Files changed`: paths edited.
- `Edits made`: concise summary.
- `Verification`: what was re-read or checked.

For short, single-surface edits like one CTA, subject line, or sentence, return the copy alone unless the user asks for rationale.

## Edit-In-Place Contract

When editing files directly:

1. Inspect the target file or relevant range before editing.
2. Make the smallest scoped edits that satisfy the copy request.
3. Preserve quoted text, code blocks, legal/compliance wording, attributed text, and unrelated content unless explicitly asked.
4. Re-read changed ranges and check the diff.
5. Run formatting, lint, or tests only when existing project conventions make that appropriate for the edited file.
6. Report files changed, what changed, and verification. Mention files intentionally left unchanged when relevant.

## Compact Quality Gate

Before returning any writing, check:

- Directness: the copy states the point instead of announcing it.
- Specificity: vague claims are replaced with facts, examples, concrete outcomes, or softer wording.
- Proof: claims match the evidence provided.
- Voice: the text sounds like a person, brand, or author, not generic model output.
- Action: the next step is clear when a next step is needed.
- Integrity: no fake proof, fake scarcity, inflated certainty, or unsupported regulated claim.

Default to one rewrite plus one gate pass. Do not keep regenerating beyond two total passes unless the user explicitly asks for more iteration.

## Guardrails

- Keep persuasion aligned with the reader's real interests.
- Affirm legitimate needs and aspirations; do not attack identity, insecurity, or hard beliefs.
- Use urgency only when it has a real reason: limited capacity, deadline, price change, opportunity cost, or delay cost.
- Admit meaningful limitations when doing so improves trust and prevents overclaiming.
- Do not create fake testimonials, fabricated numbers, invented credentials, or false scarcity.
- Do not fabricate personal quirks, anecdotes, sources, or specificity just to make the copy feel human.
- Do not treat AI-writing signals as proof of authorship. Use them as editing signals only.
- When editing a file, do not rewrite quoted material, code blocks, legal text, or attributed text unless the user explicitly asks.
- For health, financial, legal, safety, or regulated claims, avoid specific outcome guarantees and preserve or request compliance language.
- Do not help write copy for scams, coercion, harassment, deceptive medical/financial claims, or exploitative targeting.

## References

Read `references/writing-framework.md` for multi-section website or landing page copy, sales or offer critique, cold outreach, lifecycle email, social post/thread work, CRO critique, full humanization passes, or when the compact quality gate is not enough. Do not read it for one-line CTAs, simple tone edits, typo-level copy edits, or scan-only tasks unless the user asks for deeper reasoning.
