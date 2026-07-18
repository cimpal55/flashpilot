# Submission checklist

This file tracks submission readiness; unchecked items are not claims of current
functionality.

## Milestone discipline

- [x] Binding Section 28.5 decisions acknowledged.
- [x] Prompt 0 kept separate from later milestones.
- [x] Prompts 0 through 6 and Prompt 8 executed one at a time; optional Prompt 7 was intentionally skipped.

## Core proof

- [x] Deterministic CPU-only control workload has no downloads.
- [x] Repeated CI control runs match.
- [x] `safe_full` writes complete training state and direct restore matches the control.
- [x] Safe full and safe adapter-aware recovery pass the deterministic Recovery Gate.
- [x] Primary valid-but-incomplete checkpoint loads but diverges for the intended continuation reasons.
- [x] Parent performs a real kill and a new process restores.
- [x] GPT-5.6 contract and diagnosis roles have accepted live captures and clearly labeled fixture replays.
- [x] Sanitized failure request excludes every forbidden disclosure.
- [x] Exactly one bounded repair iteration produces a new isolated strategy and run.
- [x] Storage savings are reported only after recovery passes.

## Quality and submission

- [x] Full P0 lint and tests pass.
- [x] Clean-environment judge command passes without rebuilding from source.
- [x] README covers setup, platforms, scope, GPT-5.6, Codex, prior art, security, and limitations.
- [x] JSON, Markdown, and self-contained HTML reports derive from the same typed result.
- [x] No secrets, fabricated metrics, physical NAND claims, or unlabeled fixtures are committed.
- [ ] Demo video is public, has explanatory audio, and is under three minutes.
- [x] Repository URL, installation instructions, and committed wheel artifact are ready.
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
- [x] One live contract call and one live diagnosis call are validated with a real API key.
- [x] Prompt 5 repair execution and second verification are implemented.

## Prompt 5 bounded loop

- [x] Captured GPT-5.6 responses are replayed without an API call.
- [x] Six supported actions map to six explicit strategy fields.
- [x] The known strategy-change action remains unsupported and unexecuted.
- [x] The failed checkpoint is fingerprint-identical before and after repair.
- [x] Exactly one attempt is admitted; attempt two is refused.
- [x] The second worker is really terminated and recovery uses a distinct PID.
- [x] The final trajectory exactly matches control with zero tolerance.
- [x] Logical recurring-byte reduction is reported only after the final gate passes.

## Prompt 6 judge experience

- [x] `flashpilot demo --provider fixture` is the primary installed command.
- [x] Default execution creates and prints a unique full-UUID run directory.
- [x] Rich output shows every required stage and distinguishes model advice from guardrails.
- [x] GPT source is explicitly labeled captured-response fixture/replay.
- [x] Savings appear only after VERIFIED and separate the one-time base cost.
- [x] The exact logical-byte measurement disclaimer remains visible.
- [x] `flashpilot doctor` reports every required local prerequisite and limitation.
- [x] Replay fixtures are included in the installed wheel.
- [x] A new standard virtual environment installed the prebuilt wheel successfully.
- [x] Installed `doctor` and `demo` passed from outside the repository.
- [x] Verified runtime is identified as Python 3.12.13; Python 3.11 is not claimed verified.
- [x] Prompt 7 was intentionally skipped; no stretch functionality was added.

## Prompt 8 final audit

- [x] `result.json` remains the canonical machine-readable artifact; no redundant `report.json` was added.
- [x] README positions FlashPilot as a qualification and verification harness, not a serializer replacement.
- [x] README separates GPT-5.6, Codex, human, deterministic-code, and Recovery Gate responsibilities.
- [x] README uses the independently accepted Prompt 6 byte measurements exactly.
- [x] Devpost-ready English text covers every requested submission field.
- [x] English voiceover covers the complete proof and is under three minutes.
- [x] Release checklist preserves external publication and license decisions for the human.
- [x] No new live API call was made.
- [x] Prompt 8 stopped without beginning any later work.
