# GPT-5.6 captured-response fixtures

The two JSON fixtures in this directory reproduce the independently accepted,
secret-free GPT-5.6 structured responses from Prompt 4. Their metadata sidecars
retain the original live provider, model, response ID, request hash, timestamp,
prompt and schema versions, `store=false`, and accepted validation status.

FlashPilot loads them through fixture providers and labels each runtime use as
`provider=fixture`, `live_or_fixture=fixture`, and
`source=captured_live_response_replay`. Fixture replay performs no API call.
The captured response proposes actions only; deterministic guardrails classify
them, the bounded executor can apply only the six native actions, and only the
Recovery Gate can declare recovery verified.
