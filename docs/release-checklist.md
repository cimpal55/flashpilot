# Release checklist

Unchecked items require a human decision or an external publication action.

## Code and evidence

- [x] Prompt 7 was intentionally skipped and feature freeze remained in effect.
- [x] Prompt 8 final audit inspected the binding scope and persisted evidence.
- [x] The prebuilt wheel installs without rebuilding FlashPilot from source.
- [x] `flashpilot doctor` passes in a clean standard virtual environment.
- [x] The fixture judge path performs no application API or network call.
- [x] The default demo, audit, verify, and replay commands pass after installation.
- [x] `result.json` is canonical; no redundant `report.json` is produced.
- [x] Markdown, HTML, Rich output, and README use the same verified byte metrics.
- [x] Fixture and captured-live provenance are explicit and secret-free.
- [x] Physical NAND writes, write amplification, and SSD lifetime are identified
  as not measured.
- [x] Ruff, formatting, and pytest quality gates pass.

## Submission assets

- [x] README judge instructions and scope are final.
- [x] English voiceover script is under three minutes.
- [x] Devpost title, tagline, category, description, implementation, measured
  result, limitations, and roadmap are ready.
- [x] Submission checklist is current.
- [x] Prebuilt wheel path and SHA-256 are documented in the build log.
- [ ] Human selects and adds the intended repository license.
- [ ] Human records the demo video with explanatory audio.
- [ ] Human verifies the final video is under three minutes.
- [ ] Human uploads the video publicly to YouTube and records its URL.
- [ ] Human runs `/feedback` in the primary Codex thread and records the real
  Session ID.
- [ ] Human reviews public repository visibility and removes no required evidence.
- [ ] Human optionally publishes a GitHub Release and attaches the verified wheel.
- [ ] Human submits Devpost before the official deadline.

## Final external fields

- Repository URL: <https://github.com/cimpal55/flashpilot>
- YouTube URL: pending human publication
- `/feedback` Session ID: pending human command; never invent
- Devpost URL: pending human submission
- License: pending human selection
