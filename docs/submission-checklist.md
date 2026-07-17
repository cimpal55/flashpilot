# Submission checklist

This file tracks submission readiness; unchecked items are not claims of current
functionality.

## Milestone discipline

- [x] Binding Section 28.5 decisions acknowledged.
- [x] Prompt 0 kept separate from later milestones.
- [ ] Every later Section 29 prompt executed and accepted one at a time.

## Core proof

- [x] Deterministic CPU-only control workload has no downloads.
- [x] Repeated CI control runs match.
- [x] `safe_full` writes complete training state and direct restore matches the control.
- [x] Safe full and safe adapter-aware recovery pass the deterministic Recovery Gate.
- [x] Primary valid-but-incomplete checkpoint loads but diverges for the intended continuation reasons.
- [x] Parent performs a real kill and a new process restores.
- [x] GPT-5.6 contract and diagnosis roles work through labeled deterministic fixtures; live validation remains outstanding.
- [x] Sanitized failure request excludes every forbidden disclosure.
- [ ] Exactly one bounded repair iteration produces a new isolated strategy and run.
- [ ] Storage savings are reported only after recovery passes.

## Quality and submission

- [ ] Full P0 lint and tests pass.
- [ ] Clean-environment judge command passes without rebuilding from source.
- [ ] README covers setup, platforms, scope, GPT-5.6, Codex, prior art, security, and limitations.
- [ ] JSON and Markdown reports agree; optional HTML is generated only after P0 is green.
- [ ] No secrets, fabricated metrics, physical NAND claims, or unlabeled fixtures are committed.
- [ ] Demo video is public, has explanatory audio, and is under three minutes.
- [ ] Repository URL, installation instructions, and release artifact are ready.
- [ ] `/feedback` is run in the primary Codex thread and the real Session ID is saved.
- [ ] Devpost submission is completed before the official deadline.

## Prompt 4 agent boundary

- [x] Exactly two GPT-5.6 roles are implemented.
- [x] Live providers use Responses structured parsing, `gpt-5.6`, and `store=False`.
- [x] Fixture/replay providers and provenance are explicit.
- [x] Failure input is restricted to the sanitized Prompt 3 package.
- [x] Native repair capability is limited to the six binding actions.
- [x] Known non-native actions are reported as unsupported.
- [x] Unsafe, conflicting, duplicate, or unevidenced actions are rejected.
- [x] Agent metadata excludes the API key.
- [x] Repair-attempt admission is limited to one and performs no execution.
- [ ] One live contract call and one live diagnosis call are validated with a real API key.
- [ ] Prompt 5 repair execution and second verification are implemented.
