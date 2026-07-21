/* Normalises the generated bundles into the view model the surfaces render.
 *
 * Rule enforced here and nowhere else: every status and every verdict is
 * COPIED from the core artifacts. This module has no branch that can turn a
 * FAILED or UNKNOWN run into a passing one. */

import { BUNDLES } from "../data/bundles.js";
import { decodeBase64 } from "./hash.js";

const PASS_WORDS = new Set(["pass", "passed", "ok", "verified", "true"]);
const FAIL_WORDS = new Set(["fail", "failed", "error", "violated", "false"]);

/** Map a core status string to a state class. Anything unrecognised is unknown. */
export function stateOf(status) {
  const value = String(status ?? "").toLowerCase();
  if (PASS_WORDS.has(value)) return "pass";
  if (FAIL_WORDS.has(value)) return "fail";
  return "unknown";
}

export function verdictState(verdict) {
  const value = String(verdict ?? "").toUpperCase();
  if (value === "VERIFIED" || value === "PASS" || value === "PASSED") return "pass";
  if (value === "FAILED" || value === "FAIL") return "fail";
  return "unknown";
}

function firstDivergence(a, b) {
  if (!Array.isArray(a) || !Array.isArray(b)) return null;
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i += 1) {
    if (a[i] !== b[i]) return i;
  }
  if (a.length !== b.length) return n;
  return null;
}

function normaliseChecks(raw) {
  const checks = Array.isArray(raw) ? raw : [];
  return checks.map((c) => ({
    id: c.check_id ?? c.id ?? "unknown",
    label: c.label ?? c.summary ?? c.check_id ?? "unnamed requirement",
    category: c.category ?? (c.check_id ?? "").split(".")[0] ?? "other",
    expected: c.expected ?? null,
    actual: c.actual ?? null,
    status: String(c.status ?? "unknown").toUpperCase(),
    state: stateOf(c.status),
  }));
}

/**
 * Different core commands emit different result schemas. This adapter maps each
 * one onto the same view shape; it selects fields, it never derives new ones.
 */
function shapeOf(raw) {
  const result = raw.result ?? {};
  if (result.schema_version === "repair-loop-result-v1") {
    const repaired = result.repaired_run ?? {};
    return {
      gate: repaired.gate ?? {},
      beforeGate: result.initial_failure?.gate ?? null,
      control: repaired.control ?? {},
      recovery: repaired.recovery?.final ?? {},
      controlProcess: null,
      crashProcess: repaired.crash ?? null,
      recoveryProcess: repaired.recovery_process ?? null,
      framework: "native pytorch",
      profile: result.profile ? `repair · ${result.profile}` : "repair",
      scenario: repaired.strategy ?? null,
      faultScenario: repaired.crash?.termination_method ?? null,
      gpt: {
        analysis: result.proposed_analysis ?? null,
        validation: result.plan_validation ?? null,
        execution: result.repair_execution ?? null,
        metadata: result.captured_live_failure_metadata ?? result.replay_call_metadata ?? null,
      },
    };
  }
  if (result.schema_version === "flashpilot-static-audit-v1") {
    return {
      gate: { checks: result.checks ?? [], passed: null },
      beforeGate: null,
      control: {},
      recovery: {},
      controlProcess: null,
      crashProcess: null,
      recoveryProcess: null,
      framework: result.framework ?? "unknown",
      profile: result.qualification_profile ?? "—",
      scenario: null,
      faultScenario: null,
      gpt: null,
    };
  }
  return {
    gate: result.gate ?? {},
    beforeGate: null,
    control: result.control ?? {},
    recovery: result.recovery ?? {},
    controlProcess: result.control_process ?? null,
    crashProcess: result.crash_process ?? null,
    recoveryProcess: result.recovery_process ?? null,
    framework: result.framework ?? "—",
    profile: result.qualification_profile ?? "—",
    scenario: result.scenario ?? result.checkpoint_event?.scenario ?? null,
    faultScenario: result.fault_scenario ?? null,
    gpt: null,
  };
}

function digestPairs(control, recovery) {
  const spec = [
    ["Trainable state", "trainable_state_sha256"],
    ["Evaluation", "evaluation_sha256"],
    ["Optimizer", "optimizer_sha256"],
    ["Scheduler", "scheduler_sha256"],
  ];
  return spec
    .filter(([, key]) => control[key] || recovery[key])
    .map(([label, key]) => ({
      label,
      control: control[key] ?? null,
      recovery: recovery[key] ?? null,
      match: Boolean(control[key]) && control[key] === recovery[key],
    }));
}

function decodeEvidence(files) {
  const out = Object.create(null);
  for (const [path, b64] of Object.entries(files ?? {})) {
    try {
      out[path] = decodeBase64(b64);
    } catch {
      // Undecodable payload stays absent; the verifier reports MISSING, never pass.
    }
  }
  return out;
}

function buildRun(raw) {
  const result = raw.result ?? {};
  const shape = shapeOf(raw);
  const gate = shape.gate;
  const checks = normaliseChecks(gate.checks);
  const controlLoss = shape.control?.loss_history ?? null;
  const recoveryLoss = shape.recovery?.loss_history ?? null;

  return {
    id: raw.id,
    title: raw.title,
    subtitle: raw.subtitle,
    kind: raw.kind,
    sourceRun: raw.source_run,
    verdict: raw.verdict,
    state: verdictState(raw.verdict),

    adapter: result.adapter ?? raw.attestation?.adapter ?? shape.framework,
    framework: shape.framework,
    frameworkVersion:
      result.control?.transformers_version ??
      result.control?.torch_version ??
      raw.attestation?.framework_version ??
      null,
    profile: shape.profile,
    scenario: shape.scenario,
    runId: result.run_id ?? raw.attestation?.run_id ?? null,
    createdAt: result.created_at ?? raw.attestation?.issued_at ?? null,
    staticOnly: Boolean(result.static_only),

    gate: {
      passed: gate.passed ?? null,
      checks,
      failedIds: gate.failed_check_ids ?? [],
      total: checks.length,
      passedCount: checks.filter((c) => c.state === "pass").length,
      failedCount: checks.filter((c) => c.state === "fail").length,
      unknownCount: checks.filter((c) => c.state === "unknown").length,
      rpo: gate.achieved_rpo_steps ?? raw.attestation?.rpo_steps ?? null,
      maxRpo: gate.max_rpo_steps ?? raw.attestation?.max_rpo_steps ?? null,
      atol: gate.atol ?? raw.attestation?.atol ?? null,
      rtol: gate.rtol ?? raw.attestation?.rtol ?? null,
    },

    trajectory: {
      control: controlLoss,
      recovery: recoveryLoss,
      divergenceStep: firstDivergence(controlLoss, recoveryLoss),
      controlStep: shape.control?.trainer_global_step ?? shape.control?.global_step ?? null,
      recoveryStep: shape.recovery?.trainer_global_step ?? shape.recovery?.global_step ?? null,
      checkpointStep: shape.recovery?.checkpoint_step ?? null,
    },

    processes: {
      control: shape.controlProcess,
      crash: shape.crashProcess,
      recovery: shape.recoveryProcess,
      faultScenario: shape.faultScenario ?? raw.attestation?.fault_scenario ?? null,
    },

    gpt: shape.gpt,
    beforeGate: shape.beforeGate
      ? {
          checks: normaliseChecks(shape.beforeGate.checks),
          failedIds: shape.beforeGate.failed_check_ids ?? [],
          passed: shape.beforeGate.passed ?? null,
        }
      : null,

    digests: digestPairs(shape.control ?? {}, shape.recovery ?? {}),
    limitations: result.limitations ?? raw.attestation?.limitations ?? [],
    inventory: result.checkpoint_inventory ?? [],
    checkpointEvent: result.checkpoint_event ?? null,

    attestation: raw.attestation,
    signature: raw.signature ?? null,
    attestationBytes: raw.attestation_raw ? decodeBase64(raw.attestation_raw) : null,
    manifest: raw.manifest,
    manifestBytes: raw.manifest_raw ? decodeBase64(raw.manifest_raw) : null,
    contract: raw.contract,
    environment: raw.environment,
    policyEvaluation: raw.policy_evaluation ?? null,
    policyJunit: raw.policy_junit ?? null,
    junit: raw.junit,
    attestationJunit: raw.attestation_junit,
    jobSummary: raw.job_summary,

    evidence: decodeEvidence(raw.evidence_files),
    evidenceMissing: raw.evidence_missing ?? [],
    rawResult: result,
  };
}

export const RUNS = BUNDLES.map(buildRun);
export const RUNS_BY_ID = new Map(RUNS.map((r) => [r.id, r]));

export function getRun(id) {
  return RUNS_BY_ID.get(id) ?? null;
}

/** The hero pair: the same framework, one checkpoint that resumes and one that does not. */
export const HERO_PAIR = ["hf-model-only", "hf-complete"];
