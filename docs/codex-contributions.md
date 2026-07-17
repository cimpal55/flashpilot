# Codex contributions

## Milestone 0

Codex performed the following concrete work under human-approved scope:

- read and reconciled the complete V4 plan with the binding V4.1 override;
- inspected the initially empty repository and local command availability;
- designed the narrow Prompt 0 architecture and recorded the three largest risks;
- created the Python `src` layout, test layout, configuration, and documentation scaffolds;
- implemented immutable CI and demo workload profiles;
- implemented deterministic step-derived synthetic next-token batches;
- implemented the tiny Transformer-like frozen base and trainable residual adapter;
- implemented dropout-active training and fixed dropout-disabled evaluation;
- implemented AdamW training, a linear learning-rate scheduler, and control-run summaries;
- implemented deterministic digests for trainable, optimizer, scheduler, and evaluation state;
- added unit tests and an integration test for exact repeated-control equality;
- ran and recorded the required quality gates with actual output.

Codex did not implement checkpoints, GPT providers, repair execution, process
killing, a Recovery Gate, HTML, packaging, or any later milestone feature.

