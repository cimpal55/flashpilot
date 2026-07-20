// GENERATED FILE — do not edit by hand.
// Produced by tools/build_samples.py from the real run directories in
// samples/. Every value here is copied; none is computed by the UI.
export const BUNDLES = [
 {
  "attestation": null,
  "attestation_junit": null,
  "contract": null,
  "environment": null,
  "evidence_files": {},
  "evidence_missing": [],
  "id": "hf-model-only",
  "job_summary": "# FlashPilot CI summary\n\n- Outcome: **FAILED**\n- Evidence kind: `hf-qualification`\n- Framework: `huggingface-trainer`\n- Qualification profile: `exact-training-resume`\n- Checks: `5/13` non-failing\n- RPO: `0` steps\n- RTO: `6.757010` seconds\n\n## Exact failed requirements\n\n- `checkpoint.optimizer` — Optimizer state is present\n- `checkpoint.scheduler` — Scheduler state is present\n- `checkpoint.rng` — RNG state is present\n- `trajectory.loss-history` — Loss history exactly matches control\n- `state.trainable` — Trainable state digest exactly matches control\n- `state.evaluation` — Evaluation digest exactly matches control\n- `state.optimizer` — Optimizer digest exactly matches control\n- `state.scheduler` — Scheduler digest exactly matches control\n\nThis summary is derived from the same typed evidence used by the local CLI.\n",
  "junit": "<?xml version='1.0' encoding='utf-8'?>\n<testsuite name=\"flashpilot.hf-qualification\" tests=\"13\" failures=\"8\" errors=\"0\" skipped=\"0\">\n  <properties>\n    <property name=\"status\" value=\"FAILED\" />\n    <property name=\"framework\" value=\"huggingface-trainer\" />\n    <property name=\"qualification_profile\" value=\"exact-training-resume\" />\n    <property name=\"rpo_steps\" value=\"0\" />\n    <property name=\"rto_seconds\" value=\"6.75701\" />\n  </properties>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"checkpoint.model\">\n    <system-out>Model state is present Expected=present; actual=present.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"checkpoint.trainer-state\">\n    <system-out>Trainer state is present Expected=present; actual=present.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"checkpoint.optimizer\">\n    <failure message=\"Optimizer state is present\" type=\"qualification-requirement\">Optimizer state is present Expected=present; actual=missing.</failure>\n    <system-out>Optimizer state is present Expected=present; actual=missing.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"checkpoint.scheduler\">\n    <failure message=\"Scheduler state is present\" type=\"qualification-requirement\">Scheduler state is present Expected=present; actual=missing.</failure>\n    <system-out>Scheduler state is present Expected=present; actual=missing.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"checkpoint.rng\">\n    <failure message=\"RNG state is present\" type=\"qualification-requirement\">RNG state is present Expected=present; actual=missing.</failure>\n    <system-out>RNG state is present Expected=present; actual=missing.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"process.real-termination\">\n    <system-out>Checkpoint worker was really terminated Expected=verified nonzero exit; actual=verified=True, exit=1.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"process.distinct-recovery\">\n    <system-out>Recovery ran in a new process Expected=distinct PIDs; actual=29604 -&gt; 28232.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"progress.global-step\">\n    <system-out>Recovered global step matches control Expected=8; actual=8.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"trajectory.loss-history\">\n    <failure message=\"Loss history exactly matches control\" type=\"qualification-requirement\">Loss history exactly matches control Expected=exact control loss history; actual=different.</failure>\n    <system-out>Loss history exactly matches control Expected=exact control loss history; actual=different.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"state.trainable\">\n    <failure message=\"Trainable state digest exactly matches control\" type=\"qualification-requirement\">Trainable state digest exactly matches control Expected=834764124dbded98a265dfc56aa6b0f3489d55cb121bc3f870c35aa0ec7f1cc3; actual=8bd5001c874e89bbb60af70bc002e290c84aeeec0918d5d804f3a4ec151a5dfc.</failure>\n    <system-out>Trainable state digest exactly matches control Expected=834764124dbded98a265dfc56aa6b0f3489d55cb121bc3f870c35aa0ec7f1cc3; actual=8bd5001c874e89bbb60af70bc002e290c84aeeec0918d5d804f3a4ec151a5dfc.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"state.evaluation\">\n    <failure message=\"Evaluation digest exactly matches control\" type=\"qualification-requirement\">Evaluation digest exactly matches control Expected=0e2baf1f2c06964cc38cbfd3b4278dd50423475af83bb435195c815174ec63c9; actual=0349f7a7c042b0ea978bb895f8ea0593a2a1e0b9cb3f7236f6c609b8649ffcee.</failure>\n    <system-out>Evaluation digest exactly matches control Expected=0e2baf1f2c06964cc38cbfd3b4278dd50423475af83bb435195c815174ec63c9; actual=0349f7a7c042b0ea978bb895f8ea0593a2a1e0b9cb3f7236f6c609b8649ffcee.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"state.optimizer\">\n    <failure message=\"Optimizer digest exactly matches control\" type=\"qualification-requirement\">Optimizer digest exactly matches control Expected=6973dbbf26f14b71755dfa998029c9895283c450703c9fd4827fc2b351beaa63; actual=b45b313281ecb221ac2e4371fe2adb6ff4018b9782c3a6de3104ba73d77d98fa.</failure>\n    <system-out>Optimizer digest exactly matches control Expected=6973dbbf26f14b71755dfa998029c9895283c450703c9fd4827fc2b351beaa63; actual=b45b313281ecb221ac2e4371fe2adb6ff4018b9782c3a6de3104ba73d77d98fa.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"state.scheduler\">\n    <failure message=\"Scheduler digest exactly matches control\" type=\"qualification-requirement\">Scheduler digest exactly matches control Expected=7b9e523d685a2faf6a45c0c4ff59aa618d900ddfa1255f1d4cf934a8dd733d41; actual=c0e1339157199be3a4c601c4b001608fbef42875cf7d29d0211554a96ded2826.</failure>\n    <system-out>Scheduler digest exactly matches control Expected=7b9e523d685a2faf6a45c0c4ff59aa618d900ddfa1255f1d4cf934a8dd733d41; actual=c0e1339157199be3a4c601c4b001608fbef42875cf7d29d0211554a96ded2826.</system-out>\n  </testcase>\n</testsuite>\n",
  "kind": "qualification",
  "manifest": null,
  "result": {
   "adapter": "huggingface-trainer",
   "checkpoint_event": {
    "checkpoint_path": "crash/checkpoints/checkpoint-4",
    "emitted_at": "2026-07-20T01:36:28.656247Z",
    "event": "checkpoint_committed",
    "global_step": 4,
    "model_present": true,
    "optimizer_present": false,
    "rng_state_present": false,
    "scenario": "model-only",
    "scheduler_present": false,
    "schema_version": "flashpilot-hf-checkpoint-event-v1",
    "trainer_state_present": true,
    "worker_pid": 29604
   },
   "checkpoint_inventory": [
    "config.json",
    "flashpilot-callback.json",
    "model.safetensors",
    "trainer_state.json",
    "training_args.bin",
    "training_args.json"
   ],
   "control": {
    "checkpoint_step": 0,
    "evaluation_sha256": "0e2baf1f2c06964cc38cbfd3b4278dd50423475af83bb435195c815174ec63c9",
    "loss_history": [
     1.6094427108764648,
     1.6116161346435547,
     1.6185109615325928,
     1.6071336269378662,
     1.5965160131454468,
     1.591310739517212,
     1.5910385847091675,
     1.5895633697509766
    ],
    "mode": "control",
    "model_loaded_from_checkpoint": false,
    "offline_environment": true,
    "optimizer_sha256": "6973dbbf26f14b71755dfa998029c9895283c450703c9fd4827fc2b351beaa63",
    "scenario": "model-only",
    "scheduler_sha256": "7b9e523d685a2faf6a45c0c4ff59aa618d900ddfa1255f1d4cf934a8dd733d41",
    "schema_version": "flashpilot-hf-run-summary-v1",
    "semantic_global_step": 8,
    "torch_version": "2.13.0+cpu",
    "trainable_state_sha256": "834764124dbded98a265dfc56aa6b0f3489d55cb121bc3f870c35aa0ec7f1cc3",
    "trainer_global_step": 8,
    "transformers_version": "5.14.1",
    "worker_pid": 21448
   },
   "control_process": {
    "completed_at": "2026-07-20T01:36:21.934079Z",
    "exit_code": 0,
    "exit_verified": true,
    "started_at": "2026-07-20T01:36:09.187745Z",
    "worker_pid": 21448
   },
   "crash_process": {
    "completed_at": "2026-07-20T01:36:28.688732Z",
    "exit_code": 1,
    "exit_verified": true,
    "started_at": "2026-07-20T01:36:21.967916Z",
    "worker_pid": 29604
   },
   "created_at": "2026-07-20T01:36:35.520100Z",
   "fault_scenario": "process-kill",
   "final_verdict": "FAILED",
   "forwarded_arguments": [],
   "framework": "transformers",
   "gate": {
    "achieved_rpo_steps": 0,
    "atol": 0.0,
    "checks": [
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.model",
      "expected": "present",
      "label": "Model state is present",
      "status": "pass"
     },
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.trainer-state",
      "expected": "present",
      "label": "Trainer state is present",
      "status": "pass"
     },
     {
      "actual": "missing",
      "category": "checkpoint",
      "check_id": "checkpoint.optimizer",
      "expected": "present",
      "label": "Optimizer state is present",
      "status": "fail"
     },
     {
      "actual": "missing",
      "category": "checkpoint",
      "check_id": "checkpoint.scheduler",
      "expected": "present",
      "label": "Scheduler state is present",
      "status": "fail"
     },
     {
      "actual": "missing",
      "category": "checkpoint",
      "check_id": "checkpoint.rng",
      "expected": "present",
      "label": "RNG state is present",
      "status": "fail"
     },
     {
      "actual": "verified=True, exit=1",
      "category": "process",
      "check_id": "process.real-termination",
      "expected": "verified nonzero exit",
      "label": "Checkpoint worker was really terminated",
      "status": "pass"
     },
     {
      "actual": "29604 -> 28232",
      "category": "process",
      "check_id": "process.distinct-recovery",
      "expected": "distinct PIDs",
      "label": "Recovery ran in a new process",
      "status": "pass"
     },
     {
      "actual": "8",
      "category": "trajectory",
      "check_id": "progress.global-step",
      "expected": "8",
      "label": "Recovered global step matches control",
      "status": "pass"
     },
     {
      "actual": "different",
      "category": "trajectory",
      "check_id": "trajectory.loss-history",
      "expected": "exact control loss history",
      "label": "Loss history exactly matches control",
      "status": "fail"
     },
     {
      "actual": "8bd5001c874e89bbb60af70bc002e290c84aeeec0918d5d804f3a4ec151a5dfc",
      "category": "state",
      "check_id": "state.trainable",
      "expected": "834764124dbded98a265dfc56aa6b0f3489d55cb121bc3f870c35aa0ec7f1cc3",
      "label": "Trainable state digest exactly matches control",
      "status": "fail"
     },
     {
      "actual": "0349f7a7c042b0ea978bb895f8ea0593a2a1e0b9cb3f7236f6c609b8649ffcee",
      "category": "state",
      "check_id": "state.evaluation",
      "expected": "0e2baf1f2c06964cc38cbfd3b4278dd50423475af83bb435195c815174ec63c9",
      "label": "Evaluation digest exactly matches control",
      "status": "fail"
     },
     {
      "actual": "b45b313281ecb221ac2e4371fe2adb6ff4018b9782c3a6de3104ba73d77d98fa",
      "category": "state",
      "check_id": "state.optimizer",
      "expected": "6973dbbf26f14b71755dfa998029c9895283c450703c9fd4827fc2b351beaa63",
      "label": "Optimizer digest exactly matches control",
      "status": "fail"
     },
     {
      "actual": "c0e1339157199be3a4c601c4b001608fbef42875cf7d29d0211554a96ded2826",
      "category": "state",
      "check_id": "state.scheduler",
      "expected": "7b9e523d685a2faf6a45c0c4ff59aa618d900ddfa1255f1d4cf934a8dd733d41",
      "label": "Scheduler digest exactly matches control",
      "status": "fail"
     }
    ],
    "failed_check_ids": [
     "checkpoint.optimizer",
     "checkpoint.scheduler",
     "checkpoint.rng",
     "trajectory.loss-history",
     "state.trainable",
     "state.evaluation",
     "state.optimizer",
     "state.scheduler"
    ],
    "max_rpo_steps": 0,
    "passed": false,
    "rtol": 0.0,
    "schema_version": "flashpilot-hf-recovery-gate-v1"
   },
   "html_report_path": "report.html",
   "limitations": [
    "Qualification covers the included local CPU Trainer contract, not arbitrary scripts.",
    "Offline environment controls prevent library-mediated Hub access; this is not an OS network sandbox.",
    "The attestation is unsigned and provides integrity, not publisher authentication."
   ],
   "model_checkpoint_load_succeeded": true,
   "model_only_diverged": true,
   "qualification_profile": "exact-training-resume",
   "recovery": {
    "checkpoint_step": 4,
    "evaluation_sha256": "0349f7a7c042b0ea978bb895f8ea0593a2a1e0b9cb3f7236f6c609b8649ffcee",
    "loss_history": [
     1.6094427108764648,
     1.6116161346435547,
     1.6185109615325928,
     1.6071336269378662,
     1.5961759090423584,
     1.5867186784744263,
     1.5831108093261719,
     1.5598859786987305
    ],
    "mode": "recover",
    "model_loaded_from_checkpoint": true,
    "offline_environment": true,
    "optimizer_sha256": "b45b313281ecb221ac2e4371fe2adb6ff4018b9782c3a6de3104ba73d77d98fa",
    "scenario": "model-only",
    "scheduler_sha256": "c0e1339157199be3a4c601c4b001608fbef42875cf7d29d0211554a96ded2826",
    "schema_version": "flashpilot-hf-run-summary-v1",
    "semantic_global_step": 8,
    "torch_version": "2.13.0+cpu",
    "trainable_state_sha256": "8bd5001c874e89bbb60af70bc002e290c84aeeec0918d5d804f3a4ec151a5dfc",
    "trainer_global_step": 8,
    "transformers_version": "5.14.1",
    "worker_pid": 28232
   },
   "recovery_process": {
    "completed_at": "2026-07-20T01:36:35.482644Z",
    "exit_code": 0,
    "exit_verified": true,
    "started_at": "2026-07-20T01:36:28.725634Z",
    "worker_pid": 28232
   },
   "report_path": "report.md",
   "result_path": "result.json",
   "run_id": "5e498f4ba3ca45868cfe5413c56bde6b",
   "scenario": "model-only",
   "schema_version": "flashpilot-hf-qualification-v1",
   "script_path": "inputs/train.py",
   "verified_persisted_bytes": null
  },
  "source_run": "milestone13-hf-model-only",
  "subtitle": "Loads without error. Provably cannot resume the same run.",
  "title": "Hugging Face — model-only checkpoint",
  "verdict": "FAILED"
 },
 {
  "attestation": {
   "adapter": "huggingface-trainer",
   "atol": 0.0,
   "checkpoint_file_count": 9,
   "checkpoint_logical_bytes": 41635,
   "checkpoint_path": "crash/checkpoints/checkpoint-4",
   "checkpoint_sha256": "8638d9d6df58869746ed389ba60fb6522cb9cb893da17bac89e52a57c58053ab",
   "checks_passed": 13,
   "checks_total": 13,
   "code_commit": "97267a3515c9b9add31a63487149d5757a758f0d",
   "control_digest": "834764124dbded98a265dfc56aa6b0f3489d55cb121bc3f870c35aa0ec7f1cc3",
   "control_evaluation_digest": "0e2baf1f2c06964cc38cbfd3b4278dd50423475af83bb435195c815174ec63c9",
   "dependency_environment_path": "environment.json",
   "dependency_environment_sha256": "f6b3797371937e4e01747a8ef7441c90177cc16841220fa8f3cdbe7fab15746f",
   "evidence_manifest_path": "evidence-manifest.json",
   "evidence_manifest_sha256": "d19f746b68ef6f95edd7f27fd37ae726243e9534f90796ed8856e6cf8019a487",
   "fault_scenario": "process_termination",
   "framework": "transformers",
   "framework_version": "5.14.1",
   "html_report_path": "report.html",
   "issued_at": "2026-07-20T01:29:53.947653Z",
   "limitations": [
    "Qualification covers the included local CPU Trainer contract, not arbitrary scripts.",
    "Offline environment controls prevent library-mediated Hub access; this is not an OS network sandbox.",
    "The attestation is unsigned and provides integrity, not publisher authentication."
   ],
   "max_rpo_steps": 0,
   "original_worker_pid": 32392,
   "persistence_contract_path": "persistence-contract.json",
   "persistence_contract_sha256": "28e849aef4e39c02bc14e6a7e2d8aa83985e6f97dcf45a3893417e7adf412399",
   "qualification_profile": "exact-training-resume",
   "recovery_worker_pid": 17736,
   "report_path": "report.md",
   "result_path": "result.json",
   "resumed_digest": "834764124dbded98a265dfc56aa6b0f3489d55cb121bc3f870c35aa0ec7f1cc3",
   "resumed_evaluation_digest": "0e2baf1f2c06964cc38cbfd3b4278dd50423475af83bb435195c815174ec63c9",
   "rpo_steps": 0,
   "rto_seconds": 6.887749,
   "rtol": 0.0,
   "run_id": "30498446481a4d779ccc9c84417daf76",
   "schema_version": "flashpilot-attestation-v1",
   "signature_status": "unsigned",
   "source_tree_state": "dirty",
   "verdict": "verified",
   "verified_persisted_bytes": 41635
  },
  "attestation_junit": "<?xml version='1.0' encoding='utf-8'?>\n<testsuite name=\"flashpilot.attestation-verification\" tests=\"8\" failures=\"0\" errors=\"0\" skipped=\"0\">\n  <properties>\n    <property name=\"verdict\" value=\"VERIFIED\" />\n    <property name=\"attestation_sha256\" value=\"74391573ea31cc8c35dfe479540d4212a2c235661a2dde5253882477047e1fac\" />\n  </properties>\n  <testcase classname=\"flashpilot.attestation\" name=\"schema.attestation\">\n    <system-out>RecoveryAttestationV1 schema is valid.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"integrity.evidence-manifest\">\n    <system-out>Evidence manifest schema and SHA-256 passed.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"integrity.evidence-files\">\n    <system-out>Closed inventory verified 25 evidence artifacts.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"integrity.environment\">\n    <system-out>Dependency environment identity is consistent.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"consistency.contract\">\n    <system-out>Contract hash and deterministic minimum agree.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"consistency.result\">\n    <system-out>HF result, exact gate, process, trajectory, and RPO agree.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"consistency.reports\">\n    <system-out>HF reports are exact result-derived views.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"integrity.checkpoint\">\n    <system-out>HF checkpoint hash and state files agree.</system-out>\n  </testcase>\n</testsuite>\n",
  "contract": {
   "adapter": "huggingface-trainer",
   "assumptions": [
    "CPU-only included local Trainer workload",
    "Sequential deterministic synthetic dataset",
    "Transformers and Accelerate versions recorded in environment evidence"
   ],
   "framework": "transformers",
   "items": [
    {
     "evidence_ids": [
      "trainer_state.json"
     ],
     "exactness": "exact",
     "identity_controls": [],
     "reason": "Resume the exact next batch.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "batch_position"
    },
    {
     "evidence_ids": [
      "trainer_state.json"
     ],
     "exactness": "exact",
     "identity_controls": [],
     "reason": "Preserve completed progress.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "global_step"
    },
    {
     "evidence_ids": [
      "model.safetensors"
     ],
     "exactness": "exact",
     "identity_controls": [],
     "reason": "Restore all trained parameters.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "model"
    },
    {
     "evidence_ids": [
      "rng_state.pth"
     ],
     "exactness": "exact",
     "identity_controls": [],
     "reason": "Restore NumPy stochastic state.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "numpy_rng"
    },
    {
     "evidence_ids": [
      "optimizer.pt"
     ],
     "exactness": "exact",
     "identity_controls": [],
     "reason": "Preserve optimizer trajectory state.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "optimizer"
    },
    {
     "evidence_ids": [
      "rng_state.pth"
     ],
     "exactness": "exact",
     "identity_controls": [],
     "reason": "Restore Python stochastic state.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "python_rng"
    },
    {
     "evidence_ids": [
      "scheduler.pt"
     ],
     "exactness": "exact",
     "identity_controls": [],
     "reason": "Preserve the learning-rate phase.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "scheduler"
    },
    {
     "evidence_ids": [
      "rng_state.pth"
     ],
     "exactness": "exact",
     "identity_controls": [],
     "reason": "Restore dropout stochastic state.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "torch_rng"
    },
    {
     "evidence_ids": [
      "trainer_state.json"
     ],
     "exactness": "exact",
     "identity_controls": [],
     "reason": "Restore Trainer progress and log history.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "trainer_state"
    }
   ],
   "max_rpo_steps": 0,
   "qualification_profile": "exact-training-resume",
   "schema_version": "flashpilot-persistence-contract-v1",
   "warnings": [
    "Only the deterministic exact-trajectory gate can verify recovery.",
    "This contract does not claim compatibility with arbitrary Trainer scripts."
   ]
  },
  "environment": {
   "code_commit": "97267a3515c9b9add31a63487149d5757a758f0d",
   "cpu_only": true,
   "dependencies": [
    {
     "name": "accelerate",
     "version": "1.14.0"
    },
    {
     "name": "flashpilot",
     "version": "0.1.0"
    },
    {
     "name": "numpy",
     "version": "2.5.1"
    },
    {
     "name": "openai",
     "version": "2.46.0"
    },
    {
     "name": "pydantic",
     "version": "2.13.4"
    },
    {
     "name": "rich",
     "version": "14.3.4"
    },
    {
     "name": "torch",
     "version": "2.13.0+cpu"
    },
    {
     "name": "transformers",
     "version": "5.14.1"
    },
    {
     "name": "typer",
     "version": "0.27.0"
    }
   ],
   "deterministic_algorithms": false,
   "platform": "Windows-11-10.0.26200-SP0",
   "python_version": "3.12.13",
   "schema_version": "flashpilot-dependency-environment-v1",
   "source_tree_state": "dirty",
   "torch_threads": 6
  },
  "evidence_files": {
   "control/result.json": "ewogICJjaGVja3BvaW50X3N0ZXAiOiAwLAogICJldmFsdWF0aW9uX3NoYTI1NiI6ICIwZTJiYWYxZjJjMDY5NjRjYzM4Y2JmZDNiNDI3OGRkNTA0MjM0NzVhZjgzYmI0MzUxOTVjODE1MTc0ZWM2M2M5IiwKICAibG9zc19oaXN0b3J5IjogWwogICAgMS42MDk0NDI3MTA4NzY0NjQ4LAogICAgMS42MTE2MTYxMzQ2NDM1NTQ3LAogICAgMS42MTg1MTA5NjE1MzI1OTI4LAogICAgMS42MDcxMzM2MjY5Mzc4NjYyLAogICAgMS41OTY1MTYwMTMxNDU0NDY4LAogICAgMS41OTEzMTA3Mzk1MTcyMTIsCiAgICAxLjU5MTAzODU4NDcwOTE2NzUsCiAgICAxLjU4OTU2MzM2OTc1MDk3NjYKICBdLAogICJtb2RlIjogImNvbnRyb2wiLAogICJtb2RlbF9sb2FkZWRfZnJvbV9jaGVja3BvaW50IjogZmFsc2UsCiAgIm9mZmxpbmVfZW52aXJvbm1lbnQiOiB0cnVlLAogICJvcHRpbWl6ZXJfc2hhMjU2IjogIjY5NzNkYmJmMjZmMTRiNzE3NTVkZmE5OTgwMjljOTg5NTI4M2M0NTA3MDNjOWZkNDgyN2ZjMmIzNTFiZWFhNjMiLAogICJzY2VuYXJpbyI6ICJjb21wbGV0ZSIsCiAgInNjaGVkdWxlcl9zaGEyNTYiOiAiN2I5ZTUyM2Q2ODVhMmZhZjZhNDVjMGM0ZmY1OWFhNjE4ZDkwMGRkZmExMjU1ZjFkNGNmOTM0YThkZDczM2Q0MSIsCiAgInNjaGVtYV92ZXJzaW9uIjogImZsYXNocGlsb3QtaGYtcnVuLXN1bW1hcnktdjEiLAogICJzZW1hbnRpY19nbG9iYWxfc3RlcCI6IDgsCiAgInRvcmNoX3ZlcnNpb24iOiAiMi4xMy4wK2NwdSIsCiAgInRyYWluYWJsZV9zdGF0ZV9zaGEyNTYiOiAiODM0NzY0MTI0ZGJkZWQ5OGEyNjVkZmM1NmFhNmIwZjM0ODlkNTVjYjEyMWJjM2Y4NzBjMzVhYTBlYzdmMWNjMyIsCiAgInRyYWluZXJfZ2xvYmFsX3N0ZXAiOiA4LAogICJ0cmFuc2Zvcm1lcnNfdmVyc2lvbiI6ICI1LjE0LjEiLAogICJ3b3JrZXJfcGlkIjogMzEzODAKfQo=",
   "crash/checkpoints/checkpoint-4/config.json": "ew0KICAiYXJjaGl0ZWN0dXJlcyI6IFsNCiAgICAiRmxhc2hQaWxvdFRpbnlDbGFzc2lmaWVyIg0KICBdLA0KICAiZHJvcG91dCI6IDAuMjUsDQogICJkdHlwZSI6ICJmbG9hdDMyIiwNCiAgImlkMmxhYmVsIjogew0KICAgICIwIjogIkxBQkVMXzAiLA0KICAgICIxIjogIkxBQkVMXzEiLA0KICAgICIyIjogIkxBQkVMXzIiLA0KICAgICIzIjogIkxBQkVMXzMiLA0KICAgICI0IjogIkxBQkVMXzQiDQogIH0sDQogICJsYWJlbDJpZCI6IHsNCiAgICAiTEFCRUxfMCI6IDAsDQogICAgIkxBQkVMXzEiOiAxLA0KICAgICJMQUJFTF8yIjogMiwNCiAgICAiTEFCRUxfMyI6IDMsDQogICAgIkxBQkVMXzQiOiA0DQogIH0sDQogICJsYWJlbF9jb3VudCI6IDUsDQogICJtb2RlbF90eXBlIjogImZsYXNocGlsb3QtaGYtdGlueSIsDQogICJtb2RlbF93aWR0aCI6IDE2LA0KICAidHJhbnNmb3JtZXJzX3ZlcnNpb24iOiAiNS4xNC4xIiwNCiAgInVzZV9jYWNoZSI6IGZhbHNlLA0KICAidm9jYWJ1bGFyeV9zaXplIjogNDENCn0NCg==",
   "crash/checkpoints/checkpoint-4/flashpilot-callback.json": "ewogICJjaGVja3BvaW50X3BhdGgiOiAiY3Jhc2gvY2hlY2twb2ludHMvY2hlY2twb2ludC00IiwKICAiZW1pdHRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjQ2Ljk3MzQyNFoiLAogICJldmVudCI6ICJjaGVja3BvaW50X2NvbW1pdHRlZCIsCiAgImdsb2JhbF9zdGVwIjogNCwKICAibW9kZWxfcHJlc2VudCI6IHRydWUsCiAgIm9wdGltaXplcl9wcmVzZW50IjogdHJ1ZSwKICAicm5nX3N0YXRlX3ByZXNlbnQiOiB0cnVlLAogICJzY2VuYXJpbyI6ICJjb21wbGV0ZSIsCiAgInNjaGVkdWxlcl9wcmVzZW50IjogdHJ1ZSwKICAic2NoZW1hX3ZlcnNpb24iOiAiZmxhc2hwaWxvdC1oZi1jaGVja3BvaW50LWV2ZW50LXYxIiwKICAidHJhaW5lcl9zdGF0ZV9wcmVzZW50IjogdHJ1ZSwKICAid29ya2VyX3BpZCI6IDMyMzkyCn0K",
   "crash/checkpoints/checkpoint-4/model.safetensors": "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",
   "crash/checkpoints/checkpoint-4/optimizer.pt": "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",
   "crash/checkpoints/checkpoint-4/rng_state.pth": "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",
   "crash/checkpoints/checkpoint-4/scheduler.pt": "UEsDBAAACAgAAAAAAAAAAAAAAAAAAAAAAAASABAAc2NoZWR1bGVyL2RhdGEucGtsRkIMAFpaWlpaWlpaWlpaWoACfXEAKFgIAAAAYmFzZV9scnNxAV1xAihHP4R64UeuFHtHP4R64UeuFHtlWAoAAABsYXN0X2Vwb2NocQNLBFgLAAAAX3N0ZXBfY291bnRxBEsFWAsAAABfaXNfaW5pdGlhbHEFiVgaAAAAX2dldF9scl9jYWxsZWRfd2l0aGluX3N0ZXBxBolYCAAAAF9sYXN0X2xycQddcQgoRz90euFHrhR7Rz90euFHrhR7ZVgKAAAAbHJfbGFtYmRhc3EJXXEKKH1xC31xDGV1LlBLBwjTB00pzAAAAMwAAABQSwMEAAAICAAAAAAAAAAAAAAAAAAAAAAAABkALQBzY2hlZHVsZXIvLmZvcm1hdF92ZXJzaW9uRkIpAFpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaMVBLBwi379yDAQAAAAEAAABQSwMEAAAICAAAAAAAAAAAAAAAAAAAAAAAABwANQBzY2hlZHVsZXIvLnN0b3JhZ2VfYWxpZ25tZW50RkIxAFpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlo2NFBLBwg/d3HpAgAAAAIAAABQSwMEAAAICAAAAAAAAAAAAAAAAAAAAAAAABMAPQBzY2hlZHVsZXIvYnl0ZW9yZGVyRkI5AFpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWmxpdHRsZVBLBwiFPeMZBgAAAAYAAABQSwMEAAAICAAAAAAAAAAAAAAAAAAAAAAAABEAOwBzY2hlZHVsZXIvdmVyc2lvbkZCNwBaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaMwpQSwcI0Z5nVQIAAAACAAAAUEsDBAAACAgAAAAAAAAAAAAAAAAAAAAAAAAgADAAc2NoZWR1bGVyLy5kYXRhL3NlcmlhbGl6YXRpb25faWRGQiwAWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlowOTk1ODc1MTc0OTQ5MTkzMjc0MjAwMDYxNzQyMTQ1NjE3Njc1MDAwUEsHCDZMJcsoAAAAKAAAAFBLAQIAAAAACAgAAAAAAADTB00pzAAAAMwAAAASAAAAAAAAAAAAAAAAAAAAAABzY2hlZHVsZXIvZGF0YS5wa2xQSwECAAAAAAgIAAAAAAAAt+/cgwEAAAABAAAAGQAAAAAAAAAAAAAAAAAcAQAAc2NoZWR1bGVyLy5mb3JtYXRfdmVyc2lvblBLAQIAAAAACAgAAAAAAAA/d3HpAgAAAAIAAAAcAAAAAAAAAAAAAAAAAJEBAABzY2hlZHVsZXIvLnN0b3JhZ2VfYWxpZ25tZW50UEsBAgAAAAAICAAAAAAAAIU94xkGAAAABgAAABMAAAAAAAAAAAAAAAAAEgIAAHNjaGVkdWxlci9ieXRlb3JkZXJQSwECAAAAAAgIAAAAAAAA0Z5nVQIAAAACAAAAEQAAAAAAAAAAAAAAAACWAgAAc2NoZWR1bGVyL3ZlcnNpb25QSwECAAAAAAgIAAAAAAAANkwlyygAAAAoAAAAIAAAAAAAAAAAAAAAAAASAwAAc2NoZWR1bGVyLy5kYXRhL3NlcmlhbGl6YXRpb25faWRQSwYGLAAAAAAAAAAeAy0AAAAAAAAAAAAGAAAAAAAAAAYAAAAAAAAAnwEAAAAAAAC4AwAAAAAAAFBLBgcAAAAAVwUAAAAAAAABAAAAUEsFBgAAAAAGAAYAnwEAALgDAAAAAA==",
   "crash/checkpoints/checkpoint-4/trainer_state.json": "ew0KICAiYmVzdF9nbG9iYWxfc3RlcCI6IG51bGwsDQogICJiZXN0X21ldHJpYyI6IG51bGwsDQogICJiZXN0X21vZGVsX2NoZWNrcG9pbnQiOiBudWxsLA0KICAiZXBvY2giOiAwLjUsDQogICJldmFsX3N0ZXBzIjogNTAwLA0KICAiZ2xvYmFsX3N0ZXAiOiA0LA0KICAiaXNfaHlwZXJfcGFyYW1fc2VhcmNoIjogZmFsc2UsDQogICJpc19sb2NhbF9wcm9jZXNzX3plcm8iOiB0cnVlLA0KICAiaXNfd29ybGRfcHJvY2Vzc196ZXJvIjogdHJ1ZSwNCiAgImxvZ19oaXN0b3J5IjogWw0KICAgIHsNCiAgICAgICJlcG9jaCI6IDAuMTI1LA0KICAgICAgImdyYWRfbm9ybSI6IDAuNDE5NDI4MTEwMTIyNjgwNjYsDQogICAgICAibGVhcm5pbmdfcmF0ZSI6IDAuMDEsDQogICAgICAibG9zcyI6IDEuNjA5NDQyNzEwODc2NDY0OCwNCiAgICAgICJzdGVwIjogMQ0KICAgIH0sDQogICAgew0KICAgICAgImVwb2NoIjogMC4yNSwNCiAgICAgICJncmFkX25vcm0iOiAwLjQyMDY5MjgzMTI3Nzg0NzMsDQogICAgICAibGVhcm5pbmdfcmF0ZSI6IDAuMDA4NzUsDQogICAgICAibG9zcyI6IDEuNjExNjE2MTM0NjQzNTU0NywNCiAgICAgICJzdGVwIjogMg0KICAgIH0sDQogICAgew0KICAgICAgImVwb2NoIjogMC4zNzUsDQogICAgICAiZ3JhZF9ub3JtIjogMC40MjgwMTY4MTE2MDkyNjgyLA0KICAgICAgImxlYXJuaW5nX3JhdGUiOiAwLjAwNzUsDQogICAgICAibG9zcyI6IDEuNjE4NTEwOTYxNTMyNTkyOCwNCiAgICAgICJzdGVwIjogMw0KICAgIH0sDQogICAgew0KICAgICAgImVwb2NoIjogMC41LA0KICAgICAgImdyYWRfbm9ybSI6IDAuNDIxMTQ3NzMzOTI2NzczMDcsDQogICAgICAibGVhcm5pbmdfcmF0ZSI6IDAuMDA2MjUsDQogICAgICAibG9zcyI6IDEuNjA3MTMzNjI2OTM3ODY2MiwNCiAgICAgICJzdGVwIjogNA0KICAgIH0NCiAgXSwNCiAgImxvZ2dpbmdfc3RlcHMiOiAxLA0KICAibWF4X3N0ZXBzIjogOCwNCiAgIm51bV9pbnB1dF90b2tlbnNfc2VlbiI6IDAsDQogICJudW1fdHJhaW5fZXBvY2hzIjogMSwNCiAgInNhdmVfc3RlcHMiOiA0LA0KICAic3RhdGVmdWxfY2FsbGJhY2tzIjogew0KICAgICJUcmFpbmVyQ29udHJvbCI6IHsNCiAgICAgICJhcmdzIjogew0KICAgICAgICAic2hvdWxkX2Vwb2NoX3N0b3AiOiBmYWxzZSwNCiAgICAgICAgInNob3VsZF9ldmFsdWF0ZSI6IGZhbHNlLA0KICAgICAgICAic2hvdWxkX2xvZyI6IGZhbHNlLA0KICAgICAgICAic2hvdWxkX3NhdmUiOiB0cnVlLA0KICAgICAgICAic2hvdWxkX3RyYWluaW5nX3N0b3AiOiBmYWxzZQ0KICAgICAgfSwNCiAgICAgICJhdHRyaWJ1dGVzIjoge30NCiAgICB9DQogIH0sDQogICJ0b3RhbF9mbG9zIjogMjc0MTc2LjAsDQogICJ0cmFpbl9iYXRjaF9zaXplIjogNCwNCiAgInRyaWFsX25hbWUiOiBudWxsLA0KICAidHJpYWxfcGFyYW1zIjogbnVsbA0KfQ0K",
   "crash/checkpoints/checkpoint-4/training_args.bin": "UEsDBAAACAgAAAAAAAAAAAAAAAAAAAAAAAAWAAwAdHJhaW5pbmdfYXJncy9kYXRhLnBrbEZCCABaWlpaWlpaWoACY3RyYW5zZm9ybWVycy50cmFpbmluZ19hcmdzClRyYWluaW5nQXJndW1lbnRzCnEAKYFxAX1xAihYCgAAAG91dHB1dF9kaXJxA1hRAAAAQzpcUHJvZ3JhbW1pbmdcYnVzaW5lc3NcZmxhc2hwaWxvdFxydW5zXG1pbGVzdG9uZTEzLWhmLWNvbXBsZXRlXGNyYXNoXGNoZWNrcG9pbnRzcQRYGwAAAHBlcl9kZXZpY2VfdHJhaW5fYmF0Y2hfc2l6ZXEFSwRYEAAAAG51bV90cmFpbl9lcG9jaHNxBkdACAAAAAAAAFgJAAAAbWF4X3N0ZXBzcQdLCFgNAAAAbGVhcm5pbmdfcmF0ZXEIRz+EeuFHrhR7WBEAAABscl9zY2hlZHVsZXJfdHlwZXEJY3RyYW5zZm9ybWVycy50cmFpbmVyX3V0aWxzClNjaGVkdWxlclR5cGUKcQpYBgAAAGxpbmVhcnELhXEMUnENWBMAAABscl9zY2hlZHVsZXJfa3dhcmdzcQ5OWAwAAAB3YXJtdXBfc3RlcHNxD0sAWAUAAABvcHRpbXEQY3RyYW5zZm9ybWVycy50cmFpbmluZ19hcmdzCk9wdGltaXplck5hbWVzCnERWAsAAABhZGFtd190b3JjaHEShXETUnEUWAoAAABvcHRpbV9hcmdzcRVOWAwAAAB3ZWlnaHRfZGVjYXlxFkcAAAAAAAAAAFgKAAAAYWRhbV9iZXRhMXEXRz/szMzMzMzNWAoAAABhZGFtX2JldGEycRhHP+/3ztkWhytYDAAAAGFkYW1fZXBzaWxvbnEZRz5FeY7iMIw6WBQAAABvcHRpbV90YXJnZXRfbW9kdWxlc3EaTlgbAAAAZ3JhZGllbnRfYWNjdW11bGF0aW9uX3N0ZXBzcRtLAVgdAAAAYXZlcmFnZV90b2tlbnNfYWNyb3NzX2RldmljZXNxHIhYDQAAAG1heF9ncmFkX25vcm1xHUc/8AAAAAAAAFgWAAAAbGFiZWxfc21vb3RoaW5nX2ZhY3RvcnEeRwAAAAAAAAAAWAQAAABiZjE2cR+JWAQAAABmcDE2cSCJWA4AAABiZjE2X2Z1bGxfZXZhbHEhiVgOAAAAZnAxNl9mdWxsX2V2YWxxIolYBAAAAHRmMzJxI05YFgAAAGdyYWRpZW50X2NoZWNrcG9pbnRpbmdxJIlYHQAAAGdyYWRpZW50X2NoZWNrcG9pbnRpbmdfa3dhcmdzcSVOWA0AAAB0b3JjaF9jb21waWxlcSaJWBUAAAB0b3JjaF9jb21waWxlX2JhY2tlbmRxJ05YEgAAAHRvcmNoX2NvbXBpbGVfbW9kZXEoTlgQAAAAdXNlX2xpZ2VyX2tlcm5lbHEpiVgTAAAAbGlnZXJfa2VybmVsX2NvbmZpZ3EqTlgJAAAAdXNlX2NhY2hlcSuJWBMAAABuZWZ0dW5lX25vaXNlX2FscGhhcSxOWBcAAAB0b3JjaF9lbXB0eV9jYWNoZV9zdGVwc3EtTlgUAAAAYXV0b19maW5kX2JhdGNoX3NpemVxLolYEAAAAGxvZ2dpbmdfc3RyYXRlZ3lxL2N0cmFuc2Zvcm1lcnMudHJhaW5lcl91dGlscwpJbnRlcnZhbFN0cmF0ZWd5CnEwWAUAAABzdGVwc3ExhXEyUnEzWA0AAABsb2dnaW5nX3N0ZXBzcTRLAVgSAAAAbG9nZ2luZ19maXJzdF9zdGVwcTWIWBAAAABsb2dfb25fZWFjaF9ub2RlcTaIWBYAAABsb2dnaW5nX25hbl9pbmZfZmlsdGVycTeIWB0AAABpbmNsdWRlX251bV9pbnB1dF90b2tlbnNfc2VlbnE4WAIAAABub3E5WAkAAABsb2dfbGV2ZWxxOlgHAAAAcGFzc2l2ZXE7WBEAAABsb2dfbGV2ZWxfcmVwbGljYXE8WAcAAAB3YXJuaW5ncT1YDAAAAGRpc2FibGVfdHFkbXE+iFgJAAAAcmVwb3J0X3RvcT9dcUBYCAAAAHJ1bl9uYW1lcUFOWAcAAABwcm9qZWN0cUJYCwAAAGh1Z2dpbmdmYWNlcUNYEAAAAHRyYWNraW9fc3BhY2VfaWRxRE5YEQAAAHRyYWNraW9fYnVja2V0X2lkcUVOWBcAAAB0cmFja2lvX3N0YXRpY19zcGFjZV9pZHFGTlgNAAAAZXZhbF9zdHJhdGVneXFHaDBoOYVxSFJxSVgKAAAAZXZhbF9zdGVwc3FKTlgKAAAAZXZhbF9kZWxheXFLSwBYGgAAAHBlcl9kZXZpY2VfZXZhbF9iYXRjaF9zaXplcUxLCFgUAAAAcHJlZGljdGlvbl9sb3NzX29ubHlxTYlYDQAAAGV2YWxfb25fc3RhcnRxTolYFgAAAGV2YWxfZG9fY29uY2F0X2JhdGNoZXNxT4hYFgAAAGV2YWxfdXNlX2dhdGhlcl9vYmplY3RxUIlYFwAAAGV2YWxfYWNjdW11bGF0aW9uX3N0ZXBzcVFOWBMAAABpbmNsdWRlX2Zvcl9tZXRyaWNzcVJdcVNYEgAAAGJhdGNoX2V2YWxfbWV0cmljc3FUiVgPAAAAc2F2ZV9vbmx5X21vZGVscVWJWA0AAABzYXZlX3N0cmF0ZWd5cVZjdHJhbnNmb3JtZXJzLnRyYWluZXJfdXRpbHMKU2F2ZVN0cmF0ZWd5CnFXaDGFcVhScVlYCgAAAHNhdmVfc3RlcHNxWksEWBEAAABzYXZlX29uX2VhY2hfbm9kZXFbiVgQAAAAc2F2ZV90b3RhbF9saW1pdHFcSwFYFQAAAGVuYWJsZV9qaXRfY2hlY2twb2ludHFdiVgLAAAAcHVzaF90b19odWJxXolYCQAAAGh1Yl90b2tlbnFfTlgQAAAAaHViX3ByaXZhdGVfcmVwb3FgTlgMAAAAaHViX21vZGVsX2lkcWFOWAwAAABodWJfc3RyYXRlZ3lxYmN0cmFuc2Zvcm1lcnMudHJhaW5lcl91dGlscwpIdWJTdHJhdGVneQpxY1gKAAAAZXZlcnlfc2F2ZXFkhXFlUnFmWA8AAABodWJfYWx3YXlzX3B1c2hxZ4lYDAAAAGh1Yl9yZXZpc2lvbnFoTlgWAAAAbG9hZF9iZXN0X21vZGVsX2F0X2VuZHFpiVgVAAAAbWV0cmljX2Zvcl9iZXN0X21vZGVscWpOWBEAAABncmVhdGVyX2lzX2JldHRlcnFrTlgQAAAAaWdub3JlX2RhdGFfc2tpcHFsiVgnAAAAcmVzdG9yZV9jYWxsYmFja19zdGF0ZXNfZnJvbV9jaGVja3BvaW50cW2JWBAAAABmdWxsX2RldGVybWluaXNtcW6IWAQAAABzZWVkcW9KcCc1AVgJAAAAZGF0YV9zZWVkcXBKcCc1AVgHAAAAdXNlX2NwdXFxiFgSAAAAYWNjZWxlcmF0b3JfY29uZmlncXJjdHJhbnNmb3JtZXJzLnRyYWluZXJfcHRfdXRpbHMKQWNjZWxlcmF0b3JDb25maWcKcXMpgXF0fXF1KFgNAAAAc3BsaXRfYmF0Y2hlc3F2iVgQAAAAZGlzcGF0Y2hfYmF0Y2hlc3F3TlgMAAAAZXZlbl9iYXRjaGVzcXiIWBQAAAB1c2Vfc2VlZGFibGVfc2FtcGxlcnF5iFgMAAAAbm9uX2Jsb2NraW5ncXqJWBwAAABncmFkaWVudF9hY2N1bXVsYXRpb25fa3dhcmdzcXtOdWJYEgAAAHBhcmFsbGVsaXNtX2NvbmZpZ3F8TlgUAAAAZGF0YWxvYWRlcl9kcm9wX2xhc3RxfYhYFgAAAGRhdGFsb2FkZXJfbnVtX3dvcmtlcnNxfksAWBUAAABkYXRhbG9hZGVyX3Bpbl9tZW1vcnlxf4lYHQAAAGRhdGFsb2FkZXJfcGVyc2lzdGVudF93b3JrZXJzcYCJWBoAAABkYXRhbG9hZGVyX3ByZWZldGNoX2ZhY3RvcnGBTlgVAAAAcmVtb3ZlX3VudXNlZF9jb2x1bW5zcYKJWAsAAABsYWJlbF9uYW1lc3GDTlgXAAAAdHJhaW5fc2FtcGxpbmdfc3RyYXRlZ3lxhFgKAAAAc2VxdWVudGlhbHGFWBIAAABsZW5ndGhfY29sdW1uX25hbWVxhlgGAAAAbGVuZ3RocYdYGgAAAGRkcF9maW5kX3VudXNlZF9wYXJhbWV0ZXJzcYhOWBEAAABkZHBfYnVja2V0X2NhcF9tYnGJTlgVAAAAZGRwX2Jyb2FkY2FzdF9idWZmZXJzcYpOWBAAAABkZHBfc3RhdGljX2dyYXBocYtOWAsAAABkZHBfYmFja2VuZHGMTlgLAAAAZGRwX3RpbWVvdXRxjU0IB1gEAAAAZnNkcHGOTlgLAAAAZnNkcF9jb25maWdxj05YCQAAAGRlZXBzcGVlZHGQTlgFAAAAZGVidWdxkV1xklgTAAAAc2tpcF9tZW1vcnlfbWV0cmljc3GTiFgIAAAAZG9fdHJhaW5xlIlYBwAAAGRvX2V2YWxxlYlYCgAAAGRvX3ByZWRpY3RxlolYFgAAAHJlc3VtZV9mcm9tX2NoZWNrcG9pbnRxl05YDAAAAHdhcm11cF9yYXRpb3GYTlgLAAAAbG9nZ2luZ19kaXJxmU5YCgAAAGxvY2FsX3Jhbmtxmkr/////WA8AAABtaXhlZF9wcmVjaXNpb25xm2g5WBEAAABkaXN0cmlidXRlZF9zdGF0ZXGcY2FjY2VsZXJhdGUuc3RhdGUKUGFydGlhbFN0YXRlCnGdKYFxnn1xnyhYBAAAAF9jcHVxoIhYBwAAAGJhY2tlbmRxoU5YBgAAAGRldmljZXGiY3RvcmNoCmRldmljZQpxo1gDAAAAY3B1caSFcaVScaZokYlYEAAAAGRpc3RyaWJ1dGVkX3R5cGVxp2NhY2NlbGVyYXRlLnV0aWxzLmRhdGFjbGFzc2VzCkRpc3RyaWJ1dGVkVHlwZQpxqFgCAAAATk9xqYVxqlJxq1gNAAAAbnVtX3Byb2Nlc3Nlc3GsSwFYDQAAAHByb2Nlc3NfaW5kZXhxrUsAWBMAAABsb2NhbF9wcm9jZXNzX2luZGV4ca5LAFgNAAAAZm9ya19sYXVuY2hlZHGviXViWAYAAABfbl9ncHVxsEsAWA4AAABfc2V0dXBfZGV2aWNlc3GxaKNYAwAAAGNwdXGyhXGzUnG0WBAAAABmc2RwX3BsdWdpbl9hcmdzcbVOWBAAAABkZWVwc3BlZWRfcGx1Z2lucbZOdWIuUEsHCEFaDO9rDwAAaw8AAFBLAwQAAAgIAAAAAAAAAAAAAAAAAAAAAAAAHQAKAHRyYWluaW5nX2FyZ3MvLmZvcm1hdF92ZXJzaW9uRkIGAFpaWlpaWjFQSwcIt+/cgwEAAAABAAAAUEsDBAAACAgAAAAAAAAAAAAAAAAAAAAAAAAgADEAdHJhaW5pbmdfYXJncy8uc3RvcmFnZV9hbGlnbm1lbnRGQi0AWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaNjRQSwcIP3dx6QIAAAACAAAAUEsDBAAACAgAAAAAAAAAAAAAAAAAAAAAAAAXADkAdHJhaW5pbmdfYXJncy9ieXRlb3JkZXJGQjUAWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpsaXR0bGVQSwcIhT3jGQYAAAAGAAAAUEsDBAAACAgAAAAAAAAAAAAAAAAAAAAAAAAVADcAdHJhaW5pbmdfYXJncy92ZXJzaW9uRkIzAFpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWjMKUEsHCNGeZ1UCAAAAAgAAAFBLAwQAAAgIAAAAAAAAAAAAAAAAAAAAAAAAJAAsAHRyYWluaW5nX2FyZ3MvLmRhdGEvc2VyaWFsaXphdGlvbl9pZEZCKABaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaMDk5NTg3NTE3NDk0OTE5MzI3NDIwMDExMjcwNzA2OTM4MDQxNDYzNVBLBwick9pFKAAAACgAAABQSwECAAAAAAgIAAAAAAAAQVoM72sPAABrDwAAFgAAAAAAAAAAAAAAAAAAAAAAdHJhaW5pbmdfYXJncy9kYXRhLnBrbFBLAQIAAAAACAgAAAAAAAC379yDAQAAAAEAAAAdAAAAAAAAAAAAAAAAALsPAAB0cmFpbmluZ19hcmdzLy5mb3JtYXRfdmVyc2lvblBLAQIAAAAACAgAAAAAAAA/d3HpAgAAAAIAAAAgAAAAAAAAAAAAAAAAABEQAAB0cmFpbmluZ19hcmdzLy5zdG9yYWdlX2FsaWdubWVudFBLAQIAAAAACAgAAAAAAACFPeMZBgAAAAYAAAAXAAAAAAAAAAAAAAAAAJIQAAB0cmFpbmluZ19hcmdzL2J5dGVvcmRlclBLAQIAAAAACAgAAAAAAADRnmdVAgAAAAIAAAAVAAAAAAAAAAAAAAAAABYRAAB0cmFpbmluZ19hcmdzL3ZlcnNpb25QSwECAAAAAAgIAAAAAAAAnJPaRSgAAAAoAAAAJAAAAAAAAAAAAAAAAACSEQAAdHJhaW5pbmdfYXJncy8uZGF0YS9zZXJpYWxpemF0aW9uX2lkUEsGBiwAAAAAAAAAHgMtAAAAAAAAAAAABgAAAAAAAAAGAAAAAAAAALcBAAAAAAAAOBIAAAAAAABQSwYHAAAAAO8TAAAAAAAAAQAAAFBLBQYAAAAABgAGALcBAAA4EgAAAAA=",
   "crash/checkpoints/checkpoint-4/training_args.json": "ewogICJkYXRhX3NlZWQiOiAyMDI2MDcyMCwKICAiZ3JhZGllbnRfYWNjdW11bGF0aW9uX3N0ZXBzIjogMSwKICAibWF4X3N0ZXBzIjogOCwKICAicGVyX2RldmljZV90cmFpbl9iYXRjaF9zaXplIjogNCwKICAic2F2ZV9vbmx5X21vZGVsIjogZmFsc2UsCiAgInNlZWQiOiAyMDI2MDcyMCwKICAidHJhaW5fc2FtcGxpbmdfc3RyYXRlZ3kiOiAic2VxdWVudGlhbCIKfQo=",
   "environment.json": "ewogICJjb2RlX2NvbW1pdCI6ICI5NzI2N2EzNTE1YzliOWFkZDMxYTYzNDg3MTQ5ZDU3NTdhNzU4ZjBkIiwKICAiY3B1X29ubHkiOiB0cnVlLAogICJkZXBlbmRlbmNpZXMiOiBbCiAgICB7CiAgICAgICJuYW1lIjogImFjY2VsZXJhdGUiLAogICAgICAidmVyc2lvbiI6ICIxLjE0LjAiCiAgICB9LAogICAgewogICAgICAibmFtZSI6ICJmbGFzaHBpbG90IiwKICAgICAgInZlcnNpb24iOiAiMC4xLjAiCiAgICB9LAogICAgewogICAgICAibmFtZSI6ICJudW1weSIsCiAgICAgICJ2ZXJzaW9uIjogIjIuNS4xIgogICAgfSwKICAgIHsKICAgICAgIm5hbWUiOiAib3BlbmFpIiwKICAgICAgInZlcnNpb24iOiAiMi40Ni4wIgogICAgfSwKICAgIHsKICAgICAgIm5hbWUiOiAicHlkYW50aWMiLAogICAgICAidmVyc2lvbiI6ICIyLjEzLjQiCiAgICB9LAogICAgewogICAgICAibmFtZSI6ICJyaWNoIiwKICAgICAgInZlcnNpb24iOiAiMTQuMy40IgogICAgfSwKICAgIHsKICAgICAgIm5hbWUiOiAidG9yY2giLAogICAgICAidmVyc2lvbiI6ICIyLjEzLjArY3B1IgogICAgfSwKICAgIHsKICAgICAgIm5hbWUiOiAidHJhbnNmb3JtZXJzIiwKICAgICAgInZlcnNpb24iOiAiNS4xNC4xIgogICAgfSwKICAgIHsKICAgICAgIm5hbWUiOiAidHlwZXIiLAogICAgICAidmVyc2lvbiI6ICIwLjI3LjAiCiAgICB9CiAgXSwKICAiZGV0ZXJtaW5pc3RpY19hbGdvcml0aG1zIjogZmFsc2UsCiAgInBsYXRmb3JtIjogIldpbmRvd3MtMTEtMTAuMC4yNjIwMC1TUDAiLAogICJweXRob25fdmVyc2lvbiI6ICIzLjEyLjEzIiwKICAic2NoZW1hX3ZlcnNpb24iOiAiZmxhc2hwaWxvdC1kZXBlbmRlbmN5LWVudmlyb25tZW50LXYxIiwKICAic291cmNlX3RyZWVfc3RhdGUiOiAiZGlydHkiLAogICJ0b3JjaF90aHJlYWRzIjogNgp9Cg==",
   "inputs/train.py": "IiIiRG9jdW1lbnRlZCBsb2NhbCBDUFUtb25seSBIdWdnaW5nIEZhY2UgVHJhaW5lciBlbnRyeSBwb2ludCBmb3IgRmxhc2hQaWxvdC4iIiIKCmZyb20gZmxhc2hwaWxvdC5oZi53b3JrZXIgaW1wb3J0IG1haW4KCmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CiAgICBtYWluKCkK",
   "job-summary.md": "IyBGbGFzaFBpbG90IENJIHN1bW1hcnkKCi0gT3V0Y29tZTogKipWRVJJRklFRCoqCi0gRXZpZGVuY2Uga2luZDogYGhmLXF1YWxpZmljYXRpb25gCi0gRnJhbWV3b3JrOiBgaHVnZ2luZ2ZhY2UtdHJhaW5lcmAKLSBRdWFsaWZpY2F0aW9uIHByb2ZpbGU6IGBleGFjdC10cmFpbmluZy1yZXN1bWVgCi0gQ2hlY2tzOiBgMTMvMTNgIG5vbi1mYWlsaW5nCi0gUlBPOiBgMGAgc3RlcHMKLSBSVE86IGA2Ljg4Nzc0OWAgc2Vjb25kcwoKIyMgRXhhY3QgZmFpbGVkIHJlcXVpcmVtZW50cwoKLSBOb25lCgpUaGlzIHN1bW1hcnkgaXMgZGVyaXZlZCBmcm9tIHRoZSBzYW1lIHR5cGVkIGV2aWRlbmNlIHVzZWQgYnkgdGhlIGxvY2FsIENMSS4K",
   "junit.xml": "PD94bWwgdmVyc2lvbj0nMS4wJyBlbmNvZGluZz0ndXRmLTgnPz4KPHRlc3RzdWl0ZSBuYW1lPSJmbGFzaHBpbG90LmhmLXF1YWxpZmljYXRpb24iIHRlc3RzPSIxMyIgZmFpbHVyZXM9IjAiIGVycm9ycz0iMCIgc2tpcHBlZD0iMCI+CiAgPHByb3BlcnRpZXM+CiAgICA8cHJvcGVydHkgbmFtZT0ic3RhdHVzIiB2YWx1ZT0iVkVSSUZJRUQiIC8+CiAgICA8cHJvcGVydHkgbmFtZT0iZnJhbWV3b3JrIiB2YWx1ZT0iaHVnZ2luZ2ZhY2UtdHJhaW5lciIgLz4KICAgIDxwcm9wZXJ0eSBuYW1lPSJxdWFsaWZpY2F0aW9uX3Byb2ZpbGUiIHZhbHVlPSJleGFjdC10cmFpbmluZy1yZXN1bWUiIC8+CiAgICA8cHJvcGVydHkgbmFtZT0icnBvX3N0ZXBzIiB2YWx1ZT0iMCIgLz4KICAgIDxwcm9wZXJ0eSBuYW1lPSJydG9fc2Vjb25kcyIgdmFsdWU9IjYuODg3NzQ5IiAvPgogIDwvcHJvcGVydGllcz4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lmh1Z2dpbmdmYWNlLXRyYWluZXIiIG5hbWU9ImNoZWNrcG9pbnQubW9kZWwiPgogICAgPHN5c3RlbS1vdXQ+TW9kZWwgc3RhdGUgaXMgcHJlc2VudCBFeHBlY3RlZD1wcmVzZW50OyBhY3R1YWw9cHJlc2VudC48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lmh1Z2dpbmdmYWNlLXRyYWluZXIiIG5hbWU9ImNoZWNrcG9pbnQudHJhaW5lci1zdGF0ZSI+CiAgICA8c3lzdGVtLW91dD5UcmFpbmVyIHN0YXRlIGlzIHByZXNlbnQgRXhwZWN0ZWQ9cHJlc2VudDsgYWN0dWFsPXByZXNlbnQuPC9zeXN0ZW0tb3V0PgogIDwvdGVzdGNhc2U+CiAgPHRlc3RjYXNlIGNsYXNzbmFtZT0iZmxhc2hwaWxvdC5odWdnaW5nZmFjZS10cmFpbmVyIiBuYW1lPSJjaGVja3BvaW50Lm9wdGltaXplciI+CiAgICA8c3lzdGVtLW91dD5PcHRpbWl6ZXIgc3RhdGUgaXMgcHJlc2VudCBFeHBlY3RlZD1wcmVzZW50OyBhY3R1YWw9cHJlc2VudC48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lmh1Z2dpbmdmYWNlLXRyYWluZXIiIG5hbWU9ImNoZWNrcG9pbnQuc2NoZWR1bGVyIj4KICAgIDxzeXN0ZW0tb3V0PlNjaGVkdWxlciBzdGF0ZSBpcyBwcmVzZW50IEV4cGVjdGVkPXByZXNlbnQ7IGFjdHVhbD1wcmVzZW50Ljwvc3lzdGVtLW91dD4KICA8L3Rlc3RjYXNlPgogIDx0ZXN0Y2FzZSBjbGFzc25hbWU9ImZsYXNocGlsb3QuaHVnZ2luZ2ZhY2UtdHJhaW5lciIgbmFtZT0iY2hlY2twb2ludC5ybmciPgogICAgPHN5c3RlbS1vdXQ+Uk5HIHN0YXRlIGlzIHByZXNlbnQgRXhwZWN0ZWQ9cHJlc2VudDsgYWN0dWFsPXByZXNlbnQuPC9zeXN0ZW0tb3V0PgogIDwvdGVzdGNhc2U+CiAgPHRlc3RjYXNlIGNsYXNzbmFtZT0iZmxhc2hwaWxvdC5odWdnaW5nZmFjZS10cmFpbmVyIiBuYW1lPSJwcm9jZXNzLnJlYWwtdGVybWluYXRpb24iPgogICAgPHN5c3RlbS1vdXQ+Q2hlY2twb2ludCB3b3JrZXIgd2FzIHJlYWxseSB0ZXJtaW5hdGVkIEV4cGVjdGVkPXZlcmlmaWVkIG5vbnplcm8gZXhpdDsgYWN0dWFsPXZlcmlmaWVkPVRydWUsIGV4aXQ9MS48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lmh1Z2dpbmdmYWNlLXRyYWluZXIiIG5hbWU9InByb2Nlc3MuZGlzdGluY3QtcmVjb3ZlcnkiPgogICAgPHN5c3RlbS1vdXQ+UmVjb3ZlcnkgcmFuIGluIGEgbmV3IHByb2Nlc3MgRXhwZWN0ZWQ9ZGlzdGluY3QgUElEczsgYWN0dWFsPTMyMzkyIC0mZ3Q7IDE3NzM2Ljwvc3lzdGVtLW91dD4KICA8L3Rlc3RjYXNlPgogIDx0ZXN0Y2FzZSBjbGFzc25hbWU9ImZsYXNocGlsb3QuaHVnZ2luZ2ZhY2UtdHJhaW5lciIgbmFtZT0icHJvZ3Jlc3MuZ2xvYmFsLXN0ZXAiPgogICAgPHN5c3RlbS1vdXQ+UmVjb3ZlcmVkIGdsb2JhbCBzdGVwIG1hdGNoZXMgY29udHJvbCBFeHBlY3RlZD04OyBhY3R1YWw9OC48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lmh1Z2dpbmdmYWNlLXRyYWluZXIiIG5hbWU9InRyYWplY3RvcnkubG9zcy1oaXN0b3J5Ij4KICAgIDxzeXN0ZW0tb3V0Pkxvc3MgaGlzdG9yeSBleGFjdGx5IG1hdGNoZXMgY29udHJvbCBFeHBlY3RlZD1leGFjdCBjb250cm9sIGxvc3MgaGlzdG9yeTsgYWN0dWFsPWV4YWN0IG1hdGNoLjwvc3lzdGVtLW91dD4KICA8L3Rlc3RjYXNlPgogIDx0ZXN0Y2FzZSBjbGFzc25hbWU9ImZsYXNocGlsb3QuaHVnZ2luZ2ZhY2UtdHJhaW5lciIgbmFtZT0ic3RhdGUudHJhaW5hYmxlIj4KICAgIDxzeXN0ZW0tb3V0PlRyYWluYWJsZSBzdGF0ZSBkaWdlc3QgZXhhY3RseSBtYXRjaGVzIGNvbnRyb2wgRXhwZWN0ZWQ9ODM0NzY0MTI0ZGJkZWQ5OGEyNjVkZmM1NmFhNmIwZjM0ODlkNTVjYjEyMWJjM2Y4NzBjMzVhYTBlYzdmMWNjMzsgYWN0dWFsPTgzNDc2NDEyNGRiZGVkOThhMjY1ZGZjNTZhYTZiMGYzNDg5ZDU1Y2IxMjFiYzNmODcwYzM1YWEwZWM3ZjFjYzMuPC9zeXN0ZW0tb3V0PgogIDwvdGVzdGNhc2U+CiAgPHRlc3RjYXNlIGNsYXNzbmFtZT0iZmxhc2hwaWxvdC5odWdnaW5nZmFjZS10cmFpbmVyIiBuYW1lPSJzdGF0ZS5ldmFsdWF0aW9uIj4KICAgIDxzeXN0ZW0tb3V0PkV2YWx1YXRpb24gZGlnZXN0IGV4YWN0bHkgbWF0Y2hlcyBjb250cm9sIEV4cGVjdGVkPTBlMmJhZjFmMmMwNjk2NGNjMzhjYmZkM2I0Mjc4ZGQ1MDQyMzQ3NWFmODNiYjQzNTE5NWM4MTUxNzRlYzYzYzk7IGFjdHVhbD0wZTJiYWYxZjJjMDY5NjRjYzM4Y2JmZDNiNDI3OGRkNTA0MjM0NzVhZjgzYmI0MzUxOTVjODE1MTc0ZWM2M2M5Ljwvc3lzdGVtLW91dD4KICA8L3Rlc3RjYXNlPgogIDx0ZXN0Y2FzZSBjbGFzc25hbWU9ImZsYXNocGlsb3QuaHVnZ2luZ2ZhY2UtdHJhaW5lciIgbmFtZT0ic3RhdGUub3B0aW1pemVyIj4KICAgIDxzeXN0ZW0tb3V0Pk9wdGltaXplciBkaWdlc3QgZXhhY3RseSBtYXRjaGVzIGNvbnRyb2wgRXhwZWN0ZWQ9Njk3M2RiYmYyNmYxNGI3MTc1NWRmYTk5ODAyOWM5ODk1MjgzYzQ1MDcwM2M5ZmQ0ODI3ZmMyYjM1MWJlYWE2MzsgYWN0dWFsPTY5NzNkYmJmMjZmMTRiNzE3NTVkZmE5OTgwMjljOTg5NTI4M2M0NTA3MDNjOWZkNDgyN2ZjMmIzNTFiZWFhNjMuPC9zeXN0ZW0tb3V0PgogIDwvdGVzdGNhc2U+CiAgPHRlc3RjYXNlIGNsYXNzbmFtZT0iZmxhc2hwaWxvdC5odWdnaW5nZmFjZS10cmFpbmVyIiBuYW1lPSJzdGF0ZS5zY2hlZHVsZXIiPgogICAgPHN5c3RlbS1vdXQ+U2NoZWR1bGVyIGRpZ2VzdCBleGFjdGx5IG1hdGNoZXMgY29udHJvbCBFeHBlY3RlZD03YjllNTIzZDY4NWEyZmFmNmE0NWMwYzRmZjU5YWE2MThkOTAwZGRmYTEyNTVmMWQ0Y2Y5MzRhOGRkNzMzZDQxOyBhY3R1YWw9N2I5ZTUyM2Q2ODVhMmZhZjZhNDVjMGM0ZmY1OWFhNjE4ZDkwMGRkZmExMjU1ZjFkNGNmOTM0YThkZDczM2Q0MS48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KPC90ZXN0c3VpdGU+Cg==",
   "logs/control.stderr.log": "",
   "logs/control.stdout.log": "eydsb3NzJzogJzEuNjA5JywgJ2dyYWRfbm9ybSc6ICcwLjQxOTQnLCAnbGVhcm5pbmdfcmF0ZSc6ICcwLjAxJywgJ2Vwb2NoJzogJzAuMTI1J30Keydsb3NzJzogJzEuNjEyJywgJ2dyYWRfbm9ybSc6ICcwLjQyMDcnLCAnbGVhcm5pbmdfcmF0ZSc6ICcwLjAwODc1JywgJ2Vwb2NoJzogJzAuMjUnfQp7J2xvc3MnOiAnMS42MTknLCAnZ3JhZF9ub3JtJzogJzAuNDI4JywgJ2xlYXJuaW5nX3JhdGUnOiAnMC4wMDc1JywgJ2Vwb2NoJzogJzAuMzc1J30Keydsb3NzJzogJzEuNjA3JywgJ2dyYWRfbm9ybSc6ICcwLjQyMTEnLCAnbGVhcm5pbmdfcmF0ZSc6ICcwLjAwNjI1JywgJ2Vwb2NoJzogJzAuNSd9CnsnbG9zcyc6ICcxLjU5NycsICdncmFkX25vcm0nOiAnMC40MTY5JywgJ2xlYXJuaW5nX3JhdGUnOiAnMC4wMDUnLCAnZXBvY2gnOiAnMC42MjUnfQp7J2xvc3MnOiAnMS41OTEnLCAnZ3JhZF9ub3JtJzogJzAuNDEzJywgJ2xlYXJuaW5nX3JhdGUnOiAnMC4wMDM3NScsICdlcG9jaCc6ICcwLjc1J30Keydsb3NzJzogJzEuNTkxJywgJ2dyYWRfbm9ybSc6ICcwLjQxNTUnLCAnbGVhcm5pbmdfcmF0ZSc6ICcwLjAwMjUnLCAnZXBvY2gnOiAnMC44NzUnfQp7J2xvc3MnOiAnMS41OScsICdncmFkX25vcm0nOiAnMC41NDI5JywgJ2xlYXJuaW5nX3JhdGUnOiAnMC4wMDEyNScsICdlcG9jaCc6ICcxJ30Keyd0cmFpbl9ydW50aW1lJzogJzAuMDU0NycsICd0cmFpbl9zYW1wbGVzX3Blcl9zZWNvbmQnOiAnNTg0LjUnLCAndHJhaW5fc3RlcHNfcGVyX3NlY29uZCc6ICcxNDYuMScsICd0cmFpbl9sb3NzJzogJzEuNjAyJywgJ2Vwb2NoJzogJzEnfQo=",
   "logs/crash.stderr.log": "CldyaXRpbmcgbW9kZWwgc2hhcmRzOiAgIDAlfCAgICAgICAgICB8IDAvMSBbMDA6MDA8PywgP2l0L3NdCldyaXRpbmcgbW9kZWwgc2hhcmRzOiAxMDAlfCMjIyMjIyMjIyN8IDEvMSBbMDA6MDA8PywgP2l0L3NdCg==",
   "logs/crash.stdout.log": "eydsb3NzJzogJzEuNjA5JywgJ2dyYWRfbm9ybSc6ICcwLjQxOTQnLCAnbGVhcm5pbmdfcmF0ZSc6ICcwLjAxJywgJ2Vwb2NoJzogJzAuMTI1J30Keydsb3NzJzogJzEuNjEyJywgJ2dyYWRfbm9ybSc6ICcwLjQyMDcnLCAnbGVhcm5pbmdfcmF0ZSc6ICcwLjAwODc1JywgJ2Vwb2NoJzogJzAuMjUnfQp7J2xvc3MnOiAnMS42MTknLCAnZ3JhZF9ub3JtJzogJzAuNDI4JywgJ2xlYXJuaW5nX3JhdGUnOiAnMC4wMDc1JywgJ2Vwb2NoJzogJzAuMzc1J30Keydsb3NzJzogJzEuNjA3JywgJ2dyYWRfbm9ybSc6ICcwLjQyMTEnLCAnbGVhcm5pbmdfcmF0ZSc6ICcwLjAwNjI1JywgJ2Vwb2NoJzogJzAuNSd9Cnsic2NoZW1hX3ZlcnNpb24iOiJmbGFzaHBpbG90LWhmLWNoZWNrcG9pbnQtZXZlbnQtdjEiLCJldmVudCI6ImNoZWNrcG9pbnRfY29tbWl0dGVkIiwid29ya2VyX3BpZCI6MzIzOTIsImdsb2JhbF9zdGVwIjo0LCJjaGVja3BvaW50X3BhdGgiOiJjcmFzaC9jaGVja3BvaW50cy9jaGVja3BvaW50LTQiLCJzY2VuYXJpbyI6ImNvbXBsZXRlIiwibW9kZWxfcHJlc2VudCI6dHJ1ZSwidHJhaW5lcl9zdGF0ZV9wcmVzZW50Ijp0cnVlLCJvcHRpbWl6ZXJfcHJlc2VudCI6dHJ1ZSwic2NoZWR1bGVyX3ByZXNlbnQiOnRydWUsInJuZ19zdGF0ZV9wcmVzZW50Ijp0cnVlLCJlbWl0dGVkX2F0IjoiMjAyNi0wNy0yMFQwMToyOTo0Ni45NzM0MjRaIn0K",
   "logs/recovery.stderr.log": "",
   "logs/recovery.stdout.log": "eydsb3NzJzogJzEuNTk3JywgJ2dyYWRfbm9ybSc6ICcwLjQxNjknLCAnbGVhcm5pbmdfcmF0ZSc6ICcwLjAwNScsICdlcG9jaCc6ICcwLjYyNSd9CnsnbG9zcyc6ICcxLjU5MScsICdncmFkX25vcm0nOiAnMC40MTMnLCAnbGVhcm5pbmdfcmF0ZSc6ICcwLjAwMzc1JywgJ2Vwb2NoJzogJzAuNzUnfQp7J2xvc3MnOiAnMS41OTEnLCAnZ3JhZF9ub3JtJzogJzAuNDE1NScsICdsZWFybmluZ19yYXRlJzogJzAuMDAyNScsICdlcG9jaCc6ICcwLjg3NSd9CnsnbG9zcyc6ICcxLjU5JywgJ2dyYWRfbm9ybSc6ICcwLjU0MjknLCAnbGVhcm5pbmdfcmF0ZSc6ICcwLjAwMTI1JywgJ2Vwb2NoJzogJzEnfQp7J3RyYWluX3J1bnRpbWUnOiAnMC4wMzE3JywgJ3RyYWluX3NhbXBsZXNfcGVyX3NlY29uZCc6ICcxMDExJywgJ3RyYWluX3N0ZXBzX3Blcl9zZWNvbmQnOiAnMjUyLjYnLCAndHJhaW5fbG9zcyc6ICcwLjc5NjEnLCAnZXBvY2gnOiAnMSd9Cg==",
   "persistence-contract.json": "eyJhZGFwdGVyIjoiaHVnZ2luZ2ZhY2UtdHJhaW5lciIsImFzc3VtcHRpb25zIjpbIkNQVS1vbmx5IGluY2x1ZGVkIGxvY2FsIFRyYWluZXIgd29ya2xvYWQiLCJTZXF1ZW50aWFsIGRldGVybWluaXN0aWMgc3ludGhldGljIGRhdGFzZXQiLCJUcmFuc2Zvcm1lcnMgYW5kIEFjY2VsZXJhdGUgdmVyc2lvbnMgcmVjb3JkZWQgaW4gZW52aXJvbm1lbnQgZXZpZGVuY2UiXSwiZnJhbWV3b3JrIjoidHJhbnNmb3JtZXJzIiwiaXRlbXMiOlt7ImV2aWRlbmNlX2lkcyI6WyJ0cmFpbmVyX3N0YXRlLmpzb24iXSwiZXhhY3RuZXNzIjoiZXhhY3QiLCJpZGVudGl0eV9jb250cm9scyI6W10sInJlYXNvbiI6IlJlc3VtZSB0aGUgZXhhY3QgbmV4dCBiYXRjaC4iLCJyZWNvdmVyeV9zb3VyY2UiOiJjaGVja3BvaW50IiwicmVxdWlyZW1lbnQiOiJyZXF1aXJlZCIsInN0YXRlX2lkIjoiYmF0Y2hfcG9zaXRpb24ifSx7ImV2aWRlbmNlX2lkcyI6WyJ0cmFpbmVyX3N0YXRlLmpzb24iXSwiZXhhY3RuZXNzIjoiZXhhY3QiLCJpZGVudGl0eV9jb250cm9scyI6W10sInJlYXNvbiI6IlByZXNlcnZlIGNvbXBsZXRlZCBwcm9ncmVzcy4iLCJyZWNvdmVyeV9zb3VyY2UiOiJjaGVja3BvaW50IiwicmVxdWlyZW1lbnQiOiJyZXF1aXJlZCIsInN0YXRlX2lkIjoiZ2xvYmFsX3N0ZXAifSx7ImV2aWRlbmNlX2lkcyI6WyJtb2RlbC5zYWZldGVuc29ycyJdLCJleGFjdG5lc3MiOiJleGFjdCIsImlkZW50aXR5X2NvbnRyb2xzIjpbXSwicmVhc29uIjoiUmVzdG9yZSBhbGwgdHJhaW5lZCBwYXJhbWV0ZXJzLiIsInJlY292ZXJ5X3NvdXJjZSI6ImNoZWNrcG9pbnQiLCJyZXF1aXJlbWVudCI6InJlcXVpcmVkIiwic3RhdGVfaWQiOiJtb2RlbCJ9LHsiZXZpZGVuY2VfaWRzIjpbInJuZ19zdGF0ZS5wdGgiXSwiZXhhY3RuZXNzIjoiZXhhY3QiLCJpZGVudGl0eV9jb250cm9scyI6W10sInJlYXNvbiI6IlJlc3RvcmUgTnVtUHkgc3RvY2hhc3RpYyBzdGF0ZS4iLCJyZWNvdmVyeV9zb3VyY2UiOiJjaGVja3BvaW50IiwicmVxdWlyZW1lbnQiOiJyZXF1aXJlZCIsInN0YXRlX2lkIjoibnVtcHlfcm5nIn0seyJldmlkZW5jZV9pZHMiOlsib3B0aW1pemVyLnB0Il0sImV4YWN0bmVzcyI6ImV4YWN0IiwiaWRlbnRpdHlfY29udHJvbHMiOltdLCJyZWFzb24iOiJQcmVzZXJ2ZSBvcHRpbWl6ZXIgdHJhamVjdG9yeSBzdGF0ZS4iLCJyZWNvdmVyeV9zb3VyY2UiOiJjaGVja3BvaW50IiwicmVxdWlyZW1lbnQiOiJyZXF1aXJlZCIsInN0YXRlX2lkIjoib3B0aW1pemVyIn0seyJldmlkZW5jZV9pZHMiOlsicm5nX3N0YXRlLnB0aCJdLCJleGFjdG5lc3MiOiJleGFjdCIsImlkZW50aXR5X2NvbnRyb2xzIjpbXSwicmVhc29uIjoiUmVzdG9yZSBQeXRob24gc3RvY2hhc3RpYyBzdGF0ZS4iLCJyZWNvdmVyeV9zb3VyY2UiOiJjaGVja3BvaW50IiwicmVxdWlyZW1lbnQiOiJyZXF1aXJlZCIsInN0YXRlX2lkIjoicHl0aG9uX3JuZyJ9LHsiZXZpZGVuY2VfaWRzIjpbInNjaGVkdWxlci5wdCJdLCJleGFjdG5lc3MiOiJleGFjdCIsImlkZW50aXR5X2NvbnRyb2xzIjpbXSwicmVhc29uIjoiUHJlc2VydmUgdGhlIGxlYXJuaW5nLXJhdGUgcGhhc2UuIiwicmVjb3Zlcnlfc291cmNlIjoiY2hlY2twb2ludCIsInJlcXVpcmVtZW50IjoicmVxdWlyZWQiLCJzdGF0ZV9pZCI6InNjaGVkdWxlciJ9LHsiZXZpZGVuY2VfaWRzIjpbInJuZ19zdGF0ZS5wdGgiXSwiZXhhY3RuZXNzIjoiZXhhY3QiLCJpZGVudGl0eV9jb250cm9scyI6W10sInJlYXNvbiI6IlJlc3RvcmUgZHJvcG91dCBzdG9jaGFzdGljIHN0YXRlLiIsInJlY292ZXJ5X3NvdXJjZSI6ImNoZWNrcG9pbnQiLCJyZXF1aXJlbWVudCI6InJlcXVpcmVkIiwic3RhdGVfaWQiOiJ0b3JjaF9ybmcifSx7ImV2aWRlbmNlX2lkcyI6WyJ0cmFpbmVyX3N0YXRlLmpzb24iXSwiZXhhY3RuZXNzIjoiZXhhY3QiLCJpZGVudGl0eV9jb250cm9scyI6W10sInJlYXNvbiI6IlJlc3RvcmUgVHJhaW5lciBwcm9ncmVzcyBhbmQgbG9nIGhpc3RvcnkuIiwicmVjb3Zlcnlfc291cmNlIjoiY2hlY2twb2ludCIsInJlcXVpcmVtZW50IjoicmVxdWlyZWQiLCJzdGF0ZV9pZCI6InRyYWluZXJfc3RhdGUifV0sIm1heF9ycG9fc3RlcHMiOjAsInF1YWxpZmljYXRpb25fcHJvZmlsZSI6ImV4YWN0LXRyYWluaW5nLXJlc3VtZSIsInNjaGVtYV92ZXJzaW9uIjoiZmxhc2hwaWxvdC1wZXJzaXN0ZW5jZS1jb250cmFjdC12MSIsIndhcm5pbmdzIjpbIk9ubHkgdGhlIGRldGVybWluaXN0aWMgZXhhY3QtdHJhamVjdG9yeSBnYXRlIGNhbiB2ZXJpZnkgcmVjb3ZlcnkuIiwiVGhpcyBjb250cmFjdCBkb2VzIG5vdCBjbGFpbSBjb21wYXRpYmlsaXR5IHdpdGggYXJiaXRyYXJ5IFRyYWluZXIgc2NyaXB0cy4iXX0K",
   "recovery/result.json": "ewogICJjaGVja3BvaW50X3N0ZXAiOiA0LAogICJldmFsdWF0aW9uX3NoYTI1NiI6ICIwZTJiYWYxZjJjMDY5NjRjYzM4Y2JmZDNiNDI3OGRkNTA0MjM0NzVhZjgzYmI0MzUxOTVjODE1MTc0ZWM2M2M5IiwKICAibG9zc19oaXN0b3J5IjogWwogICAgMS42MDk0NDI3MTA4NzY0NjQ4LAogICAgMS42MTE2MTYxMzQ2NDM1NTQ3LAogICAgMS42MTg1MTA5NjE1MzI1OTI4LAogICAgMS42MDcxMzM2MjY5Mzc4NjYyLAogICAgMS41OTY1MTYwMTMxNDU0NDY4LAogICAgMS41OTEzMTA3Mzk1MTcyMTIsCiAgICAxLjU5MTAzODU4NDcwOTE2NzUsCiAgICAxLjU4OTU2MzM2OTc1MDk3NjYKICBdLAogICJtb2RlIjogInJlY292ZXIiLAogICJtb2RlbF9sb2FkZWRfZnJvbV9jaGVja3BvaW50IjogdHJ1ZSwKICAib2ZmbGluZV9lbnZpcm9ubWVudCI6IHRydWUsCiAgIm9wdGltaXplcl9zaGEyNTYiOiAiNjk3M2RiYmYyNmYxNGI3MTc1NWRmYTk5ODAyOWM5ODk1MjgzYzQ1MDcwM2M5ZmQ0ODI3ZmMyYjM1MWJlYWE2MyIsCiAgInNjZW5hcmlvIjogImNvbXBsZXRlIiwKICAic2NoZWR1bGVyX3NoYTI1NiI6ICI3YjllNTIzZDY4NWEyZmFmNmE0NWMwYzRmZjU5YWE2MThkOTAwZGRmYTEyNTVmMWQ0Y2Y5MzRhOGRkNzMzZDQxIiwKICAic2NoZW1hX3ZlcnNpb24iOiAiZmxhc2hwaWxvdC1oZi1ydW4tc3VtbWFyeS12MSIsCiAgInNlbWFudGljX2dsb2JhbF9zdGVwIjogOCwKICAidG9yY2hfdmVyc2lvbiI6ICIyLjEzLjArY3B1IiwKICAidHJhaW5hYmxlX3N0YXRlX3NoYTI1NiI6ICI4MzQ3NjQxMjRkYmRlZDk4YTI2NWRmYzU2YWE2YjBmMzQ4OWQ1NWNiMTIxYmMzZjg3MGMzNWFhMGVjN2YxY2MzIiwKICAidHJhaW5lcl9nbG9iYWxfc3RlcCI6IDgsCiAgInRyYW5zZm9ybWVyc192ZXJzaW9uIjogIjUuMTQuMSIsCiAgIndvcmtlcl9waWQiOiAxNzczNgp9Cg==",
   "report.html": "PCFkb2N0eXBlIGh0bWw+CjxodG1sIGxhbmc9ImVuIj48aGVhZD48bWV0YSBjaGFyc2V0PSJ1dGYtOCI+PHRpdGxlPkZsYXNoUGlsb3QgSEYgcXVhbGlmaWNhdGlvbjwvdGl0bGU+PC9oZWFkPjxib2R5PjxoMT5IdWdnaW5nIEZhY2UgVHJhaW5lciBxdWFsaWZpY2F0aW9uPC9oMT48cD48c3Ryb25nPlZlcmRpY3Q6IFZFUklGSUVEPC9zdHJvbmc+PC9wPjxwPlNjZW5hcmlvOiA8Y29kZT5jb21wbGV0ZTwvY29kZT48L3A+PHA+UElEczogMzEzODAgLyAzMjM5MiAvIDE3NzM2PC9wPjxwPkV4YWN0IGNvbXBhcmlzb246IDxjb2RlPmF0b2w9MC4wLCBydG9sPTAuMDwvY29kZT48L3A+PHA+VmVyaWZpZWQgcGVyc2lzdGVkIGJ5dGVzOiA0MTYzNSBieXRlczwvcD48aDI+RGV0ZXJtaW5pc3RpYyBnYXRlPC9oMj48dWw+PGxpPjxjb2RlPmNoZWNrcG9pbnQubW9kZWw8L2NvZGU+OiA8c3Ryb25nPlBBU1M8L3N0cm9uZz4g4oCUIE1vZGVsIHN0YXRlIGlzIHByZXNlbnQ8L2xpPjxsaT48Y29kZT5jaGVja3BvaW50LnRyYWluZXItc3RhdGU8L2NvZGU+OiA8c3Ryb25nPlBBU1M8L3N0cm9uZz4g4oCUIFRyYWluZXIgc3RhdGUgaXMgcHJlc2VudDwvbGk+PGxpPjxjb2RlPmNoZWNrcG9pbnQub3B0aW1pemVyPC9jb2RlPjogPHN0cm9uZz5QQVNTPC9zdHJvbmc+IOKAlCBPcHRpbWl6ZXIgc3RhdGUgaXMgcHJlc2VudDwvbGk+PGxpPjxjb2RlPmNoZWNrcG9pbnQuc2NoZWR1bGVyPC9jb2RlPjogPHN0cm9uZz5QQVNTPC9zdHJvbmc+IOKAlCBTY2hlZHVsZXIgc3RhdGUgaXMgcHJlc2VudDwvbGk+PGxpPjxjb2RlPmNoZWNrcG9pbnQucm5nPC9jb2RlPjogPHN0cm9uZz5QQVNTPC9zdHJvbmc+IOKAlCBSTkcgc3RhdGUgaXMgcHJlc2VudDwvbGk+PGxpPjxjb2RlPnByb2Nlc3MucmVhbC10ZXJtaW5hdGlvbjwvY29kZT46IDxzdHJvbmc+UEFTUzwvc3Ryb25nPiDigJQgQ2hlY2twb2ludCB3b3JrZXIgd2FzIHJlYWxseSB0ZXJtaW5hdGVkPC9saT48bGk+PGNvZGU+cHJvY2Vzcy5kaXN0aW5jdC1yZWNvdmVyeTwvY29kZT46IDxzdHJvbmc+UEFTUzwvc3Ryb25nPiDigJQgUmVjb3ZlcnkgcmFuIGluIGEgbmV3IHByb2Nlc3M8L2xpPjxsaT48Y29kZT5wcm9ncmVzcy5nbG9iYWwtc3RlcDwvY29kZT46IDxzdHJvbmc+UEFTUzwvc3Ryb25nPiDigJQgUmVjb3ZlcmVkIGdsb2JhbCBzdGVwIG1hdGNoZXMgY29udHJvbDwvbGk+PGxpPjxjb2RlPnRyYWplY3RvcnkubG9zcy1oaXN0b3J5PC9jb2RlPjogPHN0cm9uZz5QQVNTPC9zdHJvbmc+IOKAlCBMb3NzIGhpc3RvcnkgZXhhY3RseSBtYXRjaGVzIGNvbnRyb2w8L2xpPjxsaT48Y29kZT5zdGF0ZS50cmFpbmFibGU8L2NvZGU+OiA8c3Ryb25nPlBBU1M8L3N0cm9uZz4g4oCUIFRyYWluYWJsZSBzdGF0ZSBkaWdlc3QgZXhhY3RseSBtYXRjaGVzIGNvbnRyb2w8L2xpPjxsaT48Y29kZT5zdGF0ZS5ldmFsdWF0aW9uPC9jb2RlPjogPHN0cm9uZz5QQVNTPC9zdHJvbmc+IOKAlCBFdmFsdWF0aW9uIGRpZ2VzdCBleGFjdGx5IG1hdGNoZXMgY29udHJvbDwvbGk+PGxpPjxjb2RlPnN0YXRlLm9wdGltaXplcjwvY29kZT46IDxzdHJvbmc+UEFTUzwvc3Ryb25nPiDigJQgT3B0aW1pemVyIGRpZ2VzdCBleGFjdGx5IG1hdGNoZXMgY29udHJvbDwvbGk+PGxpPjxjb2RlPnN0YXRlLnNjaGVkdWxlcjwvY29kZT46IDxzdHJvbmc+UEFTUzwvc3Ryb25nPiDigJQgU2NoZWR1bGVyIGRpZ2VzdCBleGFjdGx5IG1hdGNoZXMgY29udHJvbDwvbGk+PC91bD48aDI+TGltaXRhdGlvbnM8L2gyPjx1bD48bGk+UXVhbGlmaWNhdGlvbiBjb3ZlcnMgdGhlIGluY2x1ZGVkIGxvY2FsIENQVSBUcmFpbmVyIGNvbnRyYWN0LCBub3QgYXJiaXRyYXJ5IHNjcmlwdHMuPC9saT48bGk+T2ZmbGluZSBlbnZpcm9ubWVudCBjb250cm9scyBwcmV2ZW50IGxpYnJhcnktbWVkaWF0ZWQgSHViIGFjY2VzczsgdGhpcyBpcyBub3QgYW4gT1MgbmV0d29yayBzYW5kYm94LjwvbGk+PGxpPlRoZSBhdHRlc3RhdGlvbiBpcyB1bnNpZ25lZCBhbmQgcHJvdmlkZXMgaW50ZWdyaXR5LCBub3QgcHVibGlzaGVyIGF1dGhlbnRpY2F0aW9uLjwvbGk+PC91bD48L2JvZHk+PC9odG1sPgo=",
   "report.md": "IyBIdWdnaW5nIEZhY2UgVHJhaW5lciBxdWFsaWZpY2F0aW9uCgotIFZlcmRpY3Q6ICoqVkVSSUZJRUQqKgotIFNjZW5hcmlvOiBgY29tcGxldGVgCi0gQWRhcHRlcjogYGh1Z2dpbmdmYWNlLXRyYWluZXJgCi0gQ29udHJvbCBQSUQ6IGAzMTM4MGAKLSBUZXJtaW5hdGVkIFBJRDogYDMyMzkyYAotIFJlY292ZXJ5IFBJRDogYDE3NzM2YAotIEV4YWN0IGNvbXBhcmlzb246IGBhdG9sPTAuMGAsIGBydG9sPTAuMGAKLSBWZXJpZmllZCBwZXJzaXN0ZWQgYnl0ZXM6IDQxNjM1IGJ5dGVzCgojIyBEZXRlcm1pbmlzdGljIGdhdGUKCi0gYGNoZWNrcG9pbnQubW9kZWxgOiAqKlBBU1MqKiDigJQgTW9kZWwgc3RhdGUgaXMgcHJlc2VudAotIGBjaGVja3BvaW50LnRyYWluZXItc3RhdGVgOiAqKlBBU1MqKiDigJQgVHJhaW5lciBzdGF0ZSBpcyBwcmVzZW50Ci0gYGNoZWNrcG9pbnQub3B0aW1pemVyYDogKipQQVNTKiog4oCUIE9wdGltaXplciBzdGF0ZSBpcyBwcmVzZW50Ci0gYGNoZWNrcG9pbnQuc2NoZWR1bGVyYDogKipQQVNTKiog4oCUIFNjaGVkdWxlciBzdGF0ZSBpcyBwcmVzZW50Ci0gYGNoZWNrcG9pbnQucm5nYDogKipQQVNTKiog4oCUIFJORyBzdGF0ZSBpcyBwcmVzZW50Ci0gYHByb2Nlc3MucmVhbC10ZXJtaW5hdGlvbmA6ICoqUEFTUyoqIOKAlCBDaGVja3BvaW50IHdvcmtlciB3YXMgcmVhbGx5IHRlcm1pbmF0ZWQKLSBgcHJvY2Vzcy5kaXN0aW5jdC1yZWNvdmVyeWA6ICoqUEFTUyoqIOKAlCBSZWNvdmVyeSByYW4gaW4gYSBuZXcgcHJvY2VzcwotIGBwcm9ncmVzcy5nbG9iYWwtc3RlcGA6ICoqUEFTUyoqIOKAlCBSZWNvdmVyZWQgZ2xvYmFsIHN0ZXAgbWF0Y2hlcyBjb250cm9sCi0gYHRyYWplY3RvcnkubG9zcy1oaXN0b3J5YDogKipQQVNTKiog4oCUIExvc3MgaGlzdG9yeSBleGFjdGx5IG1hdGNoZXMgY29udHJvbAotIGBzdGF0ZS50cmFpbmFibGVgOiAqKlBBU1MqKiDigJQgVHJhaW5hYmxlIHN0YXRlIGRpZ2VzdCBleGFjdGx5IG1hdGNoZXMgY29udHJvbAotIGBzdGF0ZS5ldmFsdWF0aW9uYDogKipQQVNTKiog4oCUIEV2YWx1YXRpb24gZGlnZXN0IGV4YWN0bHkgbWF0Y2hlcyBjb250cm9sCi0gYHN0YXRlLm9wdGltaXplcmA6ICoqUEFTUyoqIOKAlCBPcHRpbWl6ZXIgZGlnZXN0IGV4YWN0bHkgbWF0Y2hlcyBjb250cm9sCi0gYHN0YXRlLnNjaGVkdWxlcmA6ICoqUEFTUyoqIOKAlCBTY2hlZHVsZXIgZGlnZXN0IGV4YWN0bHkgbWF0Y2hlcyBjb250cm9sCgojIyBMaW1pdGF0aW9ucwoKLSBRdWFsaWZpY2F0aW9uIGNvdmVycyB0aGUgaW5jbHVkZWQgbG9jYWwgQ1BVIFRyYWluZXIgY29udHJhY3QsIG5vdCBhcmJpdHJhcnkgc2NyaXB0cy4KLSBPZmZsaW5lIGVudmlyb25tZW50IGNvbnRyb2xzIHByZXZlbnQgbGlicmFyeS1tZWRpYXRlZCBIdWIgYWNjZXNzOyB0aGlzIGlzIG5vdCBhbiBPUyBuZXR3b3JrIHNhbmRib3guCi0gVGhlIGF0dGVzdGF0aW9uIGlzIHVuc2lnbmVkIGFuZCBwcm92aWRlcyBpbnRlZ3JpdHksIG5vdCBwdWJsaXNoZXIgYXV0aGVudGljYXRpb24uCg==",
   "result.json": "ewogICJhZGFwdGVyIjogImh1Z2dpbmdmYWNlLXRyYWluZXIiLAogICJjaGVja3BvaW50X2V2ZW50IjogewogICAgImNoZWNrcG9pbnRfcGF0aCI6ICJjcmFzaC9jaGVja3BvaW50cy9jaGVja3BvaW50LTQiLAogICAgImVtaXR0ZWRfYXQiOiAiMjAyNi0wNy0yMFQwMToyOTo0Ni45NzM0MjRaIiwKICAgICJldmVudCI6ICJjaGVja3BvaW50X2NvbW1pdHRlZCIsCiAgICAiZ2xvYmFsX3N0ZXAiOiA0LAogICAgIm1vZGVsX3ByZXNlbnQiOiB0cnVlLAogICAgIm9wdGltaXplcl9wcmVzZW50IjogdHJ1ZSwKICAgICJybmdfc3RhdGVfcHJlc2VudCI6IHRydWUsCiAgICAic2NlbmFyaW8iOiAiY29tcGxldGUiLAogICAgInNjaGVkdWxlcl9wcmVzZW50IjogdHJ1ZSwKICAgICJzY2hlbWFfdmVyc2lvbiI6ICJmbGFzaHBpbG90LWhmLWNoZWNrcG9pbnQtZXZlbnQtdjEiLAogICAgInRyYWluZXJfc3RhdGVfcHJlc2VudCI6IHRydWUsCiAgICAid29ya2VyX3BpZCI6IDMyMzkyCiAgfSwKICAiY2hlY2twb2ludF9pbnZlbnRvcnkiOiBbCiAgICAiY29uZmlnLmpzb24iLAogICAgImZsYXNocGlsb3QtY2FsbGJhY2suanNvbiIsCiAgICAibW9kZWwuc2FmZXRlbnNvcnMiLAogICAgIm9wdGltaXplci5wdCIsCiAgICAicm5nX3N0YXRlLnB0aCIsCiAgICAic2NoZWR1bGVyLnB0IiwKICAgICJ0cmFpbmVyX3N0YXRlLmpzb24iLAogICAgInRyYWluaW5nX2FyZ3MuYmluIiwKICAgICJ0cmFpbmluZ19hcmdzLmpzb24iCiAgXSwKICAiY29udHJvbCI6IHsKICAgICJjaGVja3BvaW50X3N0ZXAiOiAwLAogICAgImV2YWx1YXRpb25fc2hhMjU2IjogIjBlMmJhZjFmMmMwNjk2NGNjMzhjYmZkM2I0Mjc4ZGQ1MDQyMzQ3NWFmODNiYjQzNTE5NWM4MTUxNzRlYzYzYzkiLAogICAgImxvc3NfaGlzdG9yeSI6IFsKICAgICAgMS42MDk0NDI3MTA4NzY0NjQ4LAogICAgICAxLjYxMTYxNjEzNDY0MzU1NDcsCiAgICAgIDEuNjE4NTEwOTYxNTMyNTkyOCwKICAgICAgMS42MDcxMzM2MjY5Mzc4NjYyLAogICAgICAxLjU5NjUxNjAxMzE0NTQ0NjgsCiAgICAgIDEuNTkxMzEwNzM5NTE3MjEyLAogICAgICAxLjU5MTAzODU4NDcwOTE2NzUsCiAgICAgIDEuNTg5NTYzMzY5NzUwOTc2NgogICAgXSwKICAgICJtb2RlIjogImNvbnRyb2wiLAogICAgIm1vZGVsX2xvYWRlZF9mcm9tX2NoZWNrcG9pbnQiOiBmYWxzZSwKICAgICJvZmZsaW5lX2Vudmlyb25tZW50IjogdHJ1ZSwKICAgICJvcHRpbWl6ZXJfc2hhMjU2IjogIjY5NzNkYmJmMjZmMTRiNzE3NTVkZmE5OTgwMjljOTg5NTI4M2M0NTA3MDNjOWZkNDgyN2ZjMmIzNTFiZWFhNjMiLAogICAgInNjZW5hcmlvIjogImNvbXBsZXRlIiwKICAgICJzY2hlZHVsZXJfc2hhMjU2IjogIjdiOWU1MjNkNjg1YTJmYWY2YTQ1YzBjNGZmNTlhYTYxOGQ5MDBkZGZhMTI1NWYxZDRjZjkzNGE4ZGQ3MzNkNDEiLAogICAgInNjaGVtYV92ZXJzaW9uIjogImZsYXNocGlsb3QtaGYtcnVuLXN1bW1hcnktdjEiLAogICAgInNlbWFudGljX2dsb2JhbF9zdGVwIjogOCwKICAgICJ0b3JjaF92ZXJzaW9uIjogIjIuMTMuMCtjcHUiLAogICAgInRyYWluYWJsZV9zdGF0ZV9zaGEyNTYiOiAiODM0NzY0MTI0ZGJkZWQ5OGEyNjVkZmM1NmFhNmIwZjM0ODlkNTVjYjEyMWJjM2Y4NzBjMzVhYTBlYzdmMWNjMyIsCiAgICAidHJhaW5lcl9nbG9iYWxfc3RlcCI6IDgsCiAgICAidHJhbnNmb3JtZXJzX3ZlcnNpb24iOiAiNS4xNC4xIiwKICAgICJ3b3JrZXJfcGlkIjogMzEzODAKICB9LAogICJjb250cm9sX3Byb2Nlc3MiOiB7CiAgICAiY29tcGxldGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjk6MzkuOTkwNDU4WiIsCiAgICAiZXhpdF9jb2RlIjogMCwKICAgICJleGl0X3ZlcmlmaWVkIjogdHJ1ZSwKICAgICJzdGFydGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjk6MjguMTUwMDE1WiIsCiAgICAid29ya2VyX3BpZCI6IDMxMzgwCiAgfSwKICAiY3Jhc2hfcHJvY2VzcyI6IHsKICAgICJjb21wbGV0ZWRfYXQiOiAiMjAyNi0wNy0yMFQwMToyOTo0Ny4wMjEyOTlaIiwKICAgICJleGl0X2NvZGUiOiAxLAogICAgImV4aXRfdmVyaWZpZWQiOiB0cnVlLAogICAgInN0YXJ0ZWRfYXQiOiAiMjAyNi0wNy0yMFQwMToyOTo0MC4wMjUwNTdaIiwKICAgICJ3b3JrZXJfcGlkIjogMzIzOTIKICB9LAogICJjcmVhdGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjk6NTMuOTQ3NjUzWiIsCiAgImZhdWx0X3NjZW5hcmlvIjogInByb2Nlc3Mta2lsbCIsCiAgImZpbmFsX3ZlcmRpY3QiOiAiVkVSSUZJRUQiLAogICJmb3J3YXJkZWRfYXJndW1lbnRzIjogW10sCiAgImZyYW1ld29yayI6ICJ0cmFuc2Zvcm1lcnMiLAogICJnYXRlIjogewogICAgImFjaGlldmVkX3Jwb19zdGVwcyI6IDAsCiAgICAiYXRvbCI6IDAuMCwKICAgICJjaGVja3MiOiBbCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogInByZXNlbnQiLAogICAgICAgICJjYXRlZ29yeSI6ICJjaGVja3BvaW50IiwKICAgICAgICAiY2hlY2tfaWQiOiAiY2hlY2twb2ludC5tb2RlbCIsCiAgICAgICAgImV4cGVjdGVkIjogInByZXNlbnQiLAogICAgICAgICJsYWJlbCI6ICJNb2RlbCBzdGF0ZSBpcyBwcmVzZW50IiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogInByZXNlbnQiLAogICAgICAgICJjYXRlZ29yeSI6ICJjaGVja3BvaW50IiwKICAgICAgICAiY2hlY2tfaWQiOiAiY2hlY2twb2ludC50cmFpbmVyLXN0YXRlIiwKICAgICAgICAiZXhwZWN0ZWQiOiAicHJlc2VudCIsCiAgICAgICAgImxhYmVsIjogIlRyYWluZXIgc3RhdGUgaXMgcHJlc2VudCIsCiAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICJwcmVzZW50IiwKICAgICAgICAiY2F0ZWdvcnkiOiAiY2hlY2twb2ludCIsCiAgICAgICAgImNoZWNrX2lkIjogImNoZWNrcG9pbnQub3B0aW1pemVyIiwKICAgICAgICAiZXhwZWN0ZWQiOiAicHJlc2VudCIsCiAgICAgICAgImxhYmVsIjogIk9wdGltaXplciBzdGF0ZSBpcyBwcmVzZW50IiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogInByZXNlbnQiLAogICAgICAgICJjYXRlZ29yeSI6ICJjaGVja3BvaW50IiwKICAgICAgICAiY2hlY2tfaWQiOiAiY2hlY2twb2ludC5zY2hlZHVsZXIiLAogICAgICAgICJleHBlY3RlZCI6ICJwcmVzZW50IiwKICAgICAgICAibGFiZWwiOiAiU2NoZWR1bGVyIHN0YXRlIGlzIHByZXNlbnQiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAicHJlc2VudCIsCiAgICAgICAgImNhdGVnb3J5IjogImNoZWNrcG9pbnQiLAogICAgICAgICJjaGVja19pZCI6ICJjaGVja3BvaW50LnJuZyIsCiAgICAgICAgImV4cGVjdGVkIjogInByZXNlbnQiLAogICAgICAgICJsYWJlbCI6ICJSTkcgc3RhdGUgaXMgcHJlc2VudCIsCiAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICJ2ZXJpZmllZD1UcnVlLCBleGl0PTEiLAogICAgICAgICJjYXRlZ29yeSI6ICJwcm9jZXNzIiwKICAgICAgICAiY2hlY2tfaWQiOiAicHJvY2Vzcy5yZWFsLXRlcm1pbmF0aW9uIiwKICAgICAgICAiZXhwZWN0ZWQiOiAidmVyaWZpZWQgbm9uemVybyBleGl0IiwKICAgICAgICAibGFiZWwiOiAiQ2hlY2twb2ludCB3b3JrZXIgd2FzIHJlYWxseSB0ZXJtaW5hdGVkIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogIjMyMzkyIC0+IDE3NzM2IiwKICAgICAgICAiY2F0ZWdvcnkiOiAicHJvY2VzcyIsCiAgICAgICAgImNoZWNrX2lkIjogInByb2Nlc3MuZGlzdGluY3QtcmVjb3ZlcnkiLAogICAgICAgICJleHBlY3RlZCI6ICJkaXN0aW5jdCBQSURzIiwKICAgICAgICAibGFiZWwiOiAiUmVjb3ZlcnkgcmFuIGluIGEgbmV3IHByb2Nlc3MiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAiOCIsCiAgICAgICAgImNhdGVnb3J5IjogInRyYWplY3RvcnkiLAogICAgICAgICJjaGVja19pZCI6ICJwcm9ncmVzcy5nbG9iYWwtc3RlcCIsCiAgICAgICAgImV4cGVjdGVkIjogIjgiLAogICAgICAgICJsYWJlbCI6ICJSZWNvdmVyZWQgZ2xvYmFsIHN0ZXAgbWF0Y2hlcyBjb250cm9sIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogImV4YWN0IG1hdGNoIiwKICAgICAgICAiY2F0ZWdvcnkiOiAidHJhamVjdG9yeSIsCiAgICAgICAgImNoZWNrX2lkIjogInRyYWplY3RvcnkubG9zcy1oaXN0b3J5IiwKICAgICAgICAiZXhwZWN0ZWQiOiAiZXhhY3QgY29udHJvbCBsb3NzIGhpc3RvcnkiLAogICAgICAgICJsYWJlbCI6ICJMb3NzIGhpc3RvcnkgZXhhY3RseSBtYXRjaGVzIGNvbnRyb2wiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAiODM0NzY0MTI0ZGJkZWQ5OGEyNjVkZmM1NmFhNmIwZjM0ODlkNTVjYjEyMWJjM2Y4NzBjMzVhYTBlYzdmMWNjMyIsCiAgICAgICAgImNhdGVnb3J5IjogInN0YXRlIiwKICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUudHJhaW5hYmxlIiwKICAgICAgICAiZXhwZWN0ZWQiOiAiODM0NzY0MTI0ZGJkZWQ5OGEyNjVkZmM1NmFhNmIwZjM0ODlkNTVjYjEyMWJjM2Y4NzBjMzVhYTBlYzdmMWNjMyIsCiAgICAgICAgImxhYmVsIjogIlRyYWluYWJsZSBzdGF0ZSBkaWdlc3QgZXhhY3RseSBtYXRjaGVzIGNvbnRyb2wiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAiMGUyYmFmMWYyYzA2OTY0Y2MzOGNiZmQzYjQyNzhkZDUwNDIzNDc1YWY4M2JiNDM1MTk1YzgxNTE3NGVjNjNjOSIsCiAgICAgICAgImNhdGVnb3J5IjogInN0YXRlIiwKICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUuZXZhbHVhdGlvbiIsCiAgICAgICAgImV4cGVjdGVkIjogIjBlMmJhZjFmMmMwNjk2NGNjMzhjYmZkM2I0Mjc4ZGQ1MDQyMzQ3NWFmODNiYjQzNTE5NWM4MTUxNzRlYzYzYzkiLAogICAgICAgICJsYWJlbCI6ICJFdmFsdWF0aW9uIGRpZ2VzdCBleGFjdGx5IG1hdGNoZXMgY29udHJvbCIsCiAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICI2OTczZGJiZjI2ZjE0YjcxNzU1ZGZhOTk4MDI5Yzk4OTUyODNjNDUwNzAzYzlmZDQ4MjdmYzJiMzUxYmVhYTYzIiwKICAgICAgICAiY2F0ZWdvcnkiOiAic3RhdGUiLAogICAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5vcHRpbWl6ZXIiLAogICAgICAgICJleHBlY3RlZCI6ICI2OTczZGJiZjI2ZjE0YjcxNzU1ZGZhOTk4MDI5Yzk4OTUyODNjNDUwNzAzYzlmZDQ4MjdmYzJiMzUxYmVhYTYzIiwKICAgICAgICAibGFiZWwiOiAiT3B0aW1pemVyIGRpZ2VzdCBleGFjdGx5IG1hdGNoZXMgY29udHJvbCIsCiAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICI3YjllNTIzZDY4NWEyZmFmNmE0NWMwYzRmZjU5YWE2MThkOTAwZGRmYTEyNTVmMWQ0Y2Y5MzRhOGRkNzMzZDQxIiwKICAgICAgICAiY2F0ZWdvcnkiOiAic3RhdGUiLAogICAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5zY2hlZHVsZXIiLAogICAgICAgICJleHBlY3RlZCI6ICI3YjllNTIzZDY4NWEyZmFmNmE0NWMwYzRmZjU5YWE2MThkOTAwZGRmYTEyNTVmMWQ0Y2Y5MzRhOGRkNzMzZDQxIiwKICAgICAgICAibGFiZWwiOiAiU2NoZWR1bGVyIGRpZ2VzdCBleGFjdGx5IG1hdGNoZXMgY29udHJvbCIsCiAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICB9CiAgICBdLAogICAgImZhaWxlZF9jaGVja19pZHMiOiBbXSwKICAgICJtYXhfcnBvX3N0ZXBzIjogMCwKICAgICJwYXNzZWQiOiB0cnVlLAogICAgInJ0b2wiOiAwLjAsCiAgICAic2NoZW1hX3ZlcnNpb24iOiAiZmxhc2hwaWxvdC1oZi1yZWNvdmVyeS1nYXRlLXYxIgogIH0sCiAgImh0bWxfcmVwb3J0X3BhdGgiOiAicmVwb3J0Lmh0bWwiLAogICJsaW1pdGF0aW9ucyI6IFsKICAgICJRdWFsaWZpY2F0aW9uIGNvdmVycyB0aGUgaW5jbHVkZWQgbG9jYWwgQ1BVIFRyYWluZXIgY29udHJhY3QsIG5vdCBhcmJpdHJhcnkgc2NyaXB0cy4iLAogICAgIk9mZmxpbmUgZW52aXJvbm1lbnQgY29udHJvbHMgcHJldmVudCBsaWJyYXJ5LW1lZGlhdGVkIEh1YiBhY2Nlc3M7IHRoaXMgaXMgbm90IGFuIE9TIG5ldHdvcmsgc2FuZGJveC4iLAogICAgIlRoZSBhdHRlc3RhdGlvbiBpcyB1bnNpZ25lZCBhbmQgcHJvdmlkZXMgaW50ZWdyaXR5LCBub3QgcHVibGlzaGVyIGF1dGhlbnRpY2F0aW9uLiIKICBdLAogICJtb2RlbF9jaGVja3BvaW50X2xvYWRfc3VjY2VlZGVkIjogdHJ1ZSwKICAibW9kZWxfb25seV9kaXZlcmdlZCI6IGZhbHNlLAogICJxdWFsaWZpY2F0aW9uX3Byb2ZpbGUiOiAiZXhhY3QtdHJhaW5pbmctcmVzdW1lIiwKICAicmVjb3ZlcnkiOiB7CiAgICAiY2hlY2twb2ludF9zdGVwIjogNCwKICAgICJldmFsdWF0aW9uX3NoYTI1NiI6ICIwZTJiYWYxZjJjMDY5NjRjYzM4Y2JmZDNiNDI3OGRkNTA0MjM0NzVhZjgzYmI0MzUxOTVjODE1MTc0ZWM2M2M5IiwKICAgICJsb3NzX2hpc3RvcnkiOiBbCiAgICAgIDEuNjA5NDQyNzEwODc2NDY0OCwKICAgICAgMS42MTE2MTYxMzQ2NDM1NTQ3LAogICAgICAxLjYxODUxMDk2MTUzMjU5MjgsCiAgICAgIDEuNjA3MTMzNjI2OTM3ODY2MiwKICAgICAgMS41OTY1MTYwMTMxNDU0NDY4LAogICAgICAxLjU5MTMxMDczOTUxNzIxMiwKICAgICAgMS41OTEwMzg1ODQ3MDkxNjc1LAogICAgICAxLjU4OTU2MzM2OTc1MDk3NjYKICAgIF0sCiAgICAibW9kZSI6ICJyZWNvdmVyIiwKICAgICJtb2RlbF9sb2FkZWRfZnJvbV9jaGVja3BvaW50IjogdHJ1ZSwKICAgICJvZmZsaW5lX2Vudmlyb25tZW50IjogdHJ1ZSwKICAgICJvcHRpbWl6ZXJfc2hhMjU2IjogIjY5NzNkYmJmMjZmMTRiNzE3NTVkZmE5OTgwMjljOTg5NTI4M2M0NTA3MDNjOWZkNDgyN2ZjMmIzNTFiZWFhNjMiLAogICAgInNjZW5hcmlvIjogImNvbXBsZXRlIiwKICAgICJzY2hlZHVsZXJfc2hhMjU2IjogIjdiOWU1MjNkNjg1YTJmYWY2YTQ1YzBjNGZmNTlhYTYxOGQ5MDBkZGZhMTI1NWYxZDRjZjkzNGE4ZGQ3MzNkNDEiLAogICAgInNjaGVtYV92ZXJzaW9uIjogImZsYXNocGlsb3QtaGYtcnVuLXN1bW1hcnktdjEiLAogICAgInNlbWFudGljX2dsb2JhbF9zdGVwIjogOCwKICAgICJ0b3JjaF92ZXJzaW9uIjogIjIuMTMuMCtjcHUiLAogICAgInRyYWluYWJsZV9zdGF0ZV9zaGEyNTYiOiAiODM0NzY0MTI0ZGJkZWQ5OGEyNjVkZmM1NmFhNmIwZjM0ODlkNTVjYjEyMWJjM2Y4NzBjMzVhYTBlYzdmMWNjMyIsCiAgICAidHJhaW5lcl9nbG9iYWxfc3RlcCI6IDgsCiAgICAidHJhbnNmb3JtZXJzX3ZlcnNpb24iOiAiNS4xNC4xIiwKICAgICJ3b3JrZXJfcGlkIjogMTc3MzYKICB9LAogICJyZWNvdmVyeV9wcm9jZXNzIjogewogICAgImNvbXBsZXRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjUzLjkzMTk2NFoiLAogICAgImV4aXRfY29kZSI6IDAsCiAgICAiZXhpdF92ZXJpZmllZCI6IHRydWUsCiAgICAic3RhcnRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjQ3LjA0NDIxNVoiLAogICAgIndvcmtlcl9waWQiOiAxNzczNgogIH0sCiAgInJlcG9ydF9wYXRoIjogInJlcG9ydC5tZCIsCiAgInJlc3VsdF9wYXRoIjogInJlc3VsdC5qc29uIiwKICAicnVuX2lkIjogIjMwNDk4NDQ2NDgxYTRkNzc5Y2NjOWM4NDQxN2RhZjc2IiwKICAic2NlbmFyaW8iOiAiY29tcGxldGUiLAogICJzY2hlbWFfdmVyc2lvbiI6ICJmbGFzaHBpbG90LWhmLXF1YWxpZmljYXRpb24tdjEiLAogICJzY3JpcHRfcGF0aCI6ICJpbnB1dHMvdHJhaW4ucHkiLAogICJ2ZXJpZmllZF9wZXJzaXN0ZWRfYnl0ZXMiOiA0MTYzNQp9Cg=="
  },
  "evidence_missing": [],
  "id": "hf-complete",
  "job_summary": "# FlashPilot CI summary\n\n- Outcome: **VERIFIED**\n- Evidence kind: `hf-qualification`\n- Framework: `huggingface-trainer`\n- Qualification profile: `exact-training-resume`\n- Checks: `13/13` non-failing\n- RPO: `0` steps\n- RTO: `6.887749` seconds\n\n## Exact failed requirements\n\n- None\n\nThis summary is derived from the same typed evidence used by the local CLI.\n",
  "junit": "<?xml version='1.0' encoding='utf-8'?>\n<testsuite name=\"flashpilot.hf-qualification\" tests=\"13\" failures=\"0\" errors=\"0\" skipped=\"0\">\n  <properties>\n    <property name=\"status\" value=\"VERIFIED\" />\n    <property name=\"framework\" value=\"huggingface-trainer\" />\n    <property name=\"qualification_profile\" value=\"exact-training-resume\" />\n    <property name=\"rpo_steps\" value=\"0\" />\n    <property name=\"rto_seconds\" value=\"6.887749\" />\n  </properties>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"checkpoint.model\">\n    <system-out>Model state is present Expected=present; actual=present.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"checkpoint.trainer-state\">\n    <system-out>Trainer state is present Expected=present; actual=present.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"checkpoint.optimizer\">\n    <system-out>Optimizer state is present Expected=present; actual=present.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"checkpoint.scheduler\">\n    <system-out>Scheduler state is present Expected=present; actual=present.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"checkpoint.rng\">\n    <system-out>RNG state is present Expected=present; actual=present.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"process.real-termination\">\n    <system-out>Checkpoint worker was really terminated Expected=verified nonzero exit; actual=verified=True, exit=1.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"process.distinct-recovery\">\n    <system-out>Recovery ran in a new process Expected=distinct PIDs; actual=32392 -&gt; 17736.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"progress.global-step\">\n    <system-out>Recovered global step matches control Expected=8; actual=8.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"trajectory.loss-history\">\n    <system-out>Loss history exactly matches control Expected=exact control loss history; actual=exact match.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"state.trainable\">\n    <system-out>Trainable state digest exactly matches control Expected=834764124dbded98a265dfc56aa6b0f3489d55cb121bc3f870c35aa0ec7f1cc3; actual=834764124dbded98a265dfc56aa6b0f3489d55cb121bc3f870c35aa0ec7f1cc3.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"state.evaluation\">\n    <system-out>Evaluation digest exactly matches control Expected=0e2baf1f2c06964cc38cbfd3b4278dd50423475af83bb435195c815174ec63c9; actual=0e2baf1f2c06964cc38cbfd3b4278dd50423475af83bb435195c815174ec63c9.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"state.optimizer\">\n    <system-out>Optimizer digest exactly matches control Expected=6973dbbf26f14b71755dfa998029c9895283c450703c9fd4827fc2b351beaa63; actual=6973dbbf26f14b71755dfa998029c9895283c450703c9fd4827fc2b351beaa63.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.huggingface-trainer\" name=\"state.scheduler\">\n    <system-out>Scheduler digest exactly matches control Expected=7b9e523d685a2faf6a45c0c4ff59aa618d900ddfa1255f1d4cf934a8dd733d41; actual=7b9e523d685a2faf6a45c0c4ff59aa618d900ddfa1255f1d4cf934a8dd733d41.</system-out>\n  </testcase>\n</testsuite>\n",
  "kind": "qualification",
  "manifest": {
   "entries": [
    {
     "path": "control/result.json",
     "sha256": "e95c1fcc449c3d2ad4b7f6cfbeeeba8989c96f6489ec5455643720a1664177b3",
     "size_bytes": 929
    },
    {
     "path": "crash/checkpoints/checkpoint-4/config.json",
     "sha256": "79022546312547e56c66fdf41a75b3506e879e6d2ec92f134b88646d53acf6e7",
     "size_bytes": 520
    },
    {
     "path": "crash/checkpoints/checkpoint-4/flashpilot-callback.json",
     "sha256": "01fd157fb4d2399664cd6edf022b698f86ec34b179f7db82482fa783e7cbb23b",
     "size_bytes": 411
    },
    {
     "path": "crash/checkpoints/checkpoint-4/model.safetensors",
     "sha256": "5cd6469c3ca883cceee01dc61fdda32afadacb6adb37405d2fb25292bebf4923",
     "size_bytes": 4468
    },
    {
     "path": "crash/checkpoints/checkpoint-4/optimizer.pt",
     "sha256": "643dc8343f65cb80d8e243ff8d9bc9e83a848dc6498fe4ec0ea30292008da249",
     "size_bytes": 13536
    },
    {
     "path": "crash/checkpoints/checkpoint-4/rng_state.pth",
     "sha256": "fd1ab2990bdb7ce78633b6b1e51b1afc78d29059de4e8af1e8a42f1ff076d795",
     "size_bytes": 14391
    },
    {
     "path": "crash/checkpoints/checkpoint-4/scheduler.pt",
     "sha256": "ab504dd35b81e19ef766aa82b7cf76e21cc60e3214db3527d1ce046baa137779",
     "size_bytes": 1465
    },
    {
     "path": "crash/checkpoints/checkpoint-4/trainer_state.json",
     "sha256": "5ce71797da7b014442879e08ad9d6c600f4dfa581576baf680bd876ed93fd4c3",
     "size_bytes": 1434
    },
    {
     "path": "crash/checkpoints/checkpoint-4/training_args.bin",
     "sha256": "4a05da750bc0fc619e815c3cd0a1ec5e2e02ef5d2094dcdb9ba736d71ae16cd0",
     "size_bytes": 5201
    },
    {
     "path": "crash/checkpoints/checkpoint-4/training_args.json",
     "sha256": "eafd2a1c47ca3aa0c81bd2ac7308dc127a373bfc759dac317baa2e03310937fe",
     "size_bytes": 209
    },
    {
     "path": "environment.json",
     "sha256": "eae21da0cd622432aa2a76b4de6c69dc195b584cdff04b2b8bc68308bca71af0",
     "size_bytes": 913
    },
    {
     "path": "inputs/train.py",
     "sha256": "3d4c303a5894ac145d791fa06e756abc3a54230d44350b0f85940d288f1041dc",
     "size_bytes": 159
    },
    {
     "path": "job-summary.md",
     "sha256": "70ac502bb5dc427bab31a1c70cd3d6d8cd30ef065546033c441c1580b9f5925c",
     "size_bytes": 357
    },
    {
     "path": "junit.xml",
     "sha256": "f464eaf5912da99d0be3cb8f667710f9100f9b59a484e35e9df83f2c4d8650a3",
     "size_bytes": 3490
    },
    {
     "path": "logs/control.stderr.log",
     "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
     "size_bytes": 0
    },
    {
     "path": "logs/control.stdout.log",
     "sha256": "706927d643011725410cc43dabcb7cace60d5abee2a2cc339c107ed8d853b540",
     "size_bytes": 815
    },
    {
     "path": "logs/crash.stderr.log",
     "sha256": "6533ba74765525aa34d53961ae98c977f3b1900e8d31fdb3dc22058dec69267e",
     "size_bytes": 121
    },
    {
     "path": "logs/crash.stdout.log",
     "sha256": "a126ffd8891c6ee25031aa7a164bd44cc94f18db7ec466ff61eba25091669bee",
     "size_bytes": 702
    },
    {
     "path": "logs/recovery.stderr.log",
     "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
     "size_bytes": 0
    },
    {
     "path": "logs/recovery.stdout.log",
     "sha256": "d7837afd05bcb017be75b7f7782a2aea1cab8e07ede909ce8653c61592e54fee",
     "size_bytes": 475
    },
    {
     "path": "persistence-contract.json",
     "sha256": "1a832e1fc13aaaeffe3aef81ae8f056aba7697bafdc2375783c97e21c3884692",
     "size_bytes": 2364
    },
    {
     "path": "recovery/result.json",
     "sha256": "316ecafaad51df90a7c982e94fe511584897e53728d99fe0961edd8a2b0ea07a",
     "size_bytes": 928
    },
    {
     "path": "report.html",
     "sha256": "95894478c0c259b0ffad430d1e3e014c90bf4292fca6006597cc9273669739e9",
     "size_bytes": 2066
    },
    {
     "path": "report.md",
     "sha256": "9075c4decb858d9806c1e752ccbe9ded7f925b1ab303a972098db27bd2659a2f",
     "size_bytes": 1522
    },
    {
     "path": "result.json",
     "sha256": "a7d92c4d72c0a55d8c3104d24a548b27baad49e3e14a77604025e53eadd844c3",
     "size_bytes": 7981
    }
   ],
   "excluded_statement_artifacts": [
    "attestation.junit.xml",
    "evidence-manifest.json",
    "recovery.attestation.json"
   ],
   "root_scope": "attestation-directory",
   "schema_version": "flashpilot-evidence-manifest-v1"
  },
  "result": {
   "adapter": "huggingface-trainer",
   "checkpoint_event": {
    "checkpoint_path": "crash/checkpoints/checkpoint-4",
    "emitted_at": "2026-07-20T01:29:46.973424Z",
    "event": "checkpoint_committed",
    "global_step": 4,
    "model_present": true,
    "optimizer_present": true,
    "rng_state_present": true,
    "scenario": "complete",
    "scheduler_present": true,
    "schema_version": "flashpilot-hf-checkpoint-event-v1",
    "trainer_state_present": true,
    "worker_pid": 32392
   },
   "checkpoint_inventory": [
    "config.json",
    "flashpilot-callback.json",
    "model.safetensors",
    "optimizer.pt",
    "rng_state.pth",
    "scheduler.pt",
    "trainer_state.json",
    "training_args.bin",
    "training_args.json"
   ],
   "control": {
    "checkpoint_step": 0,
    "evaluation_sha256": "0e2baf1f2c06964cc38cbfd3b4278dd50423475af83bb435195c815174ec63c9",
    "loss_history": [
     1.6094427108764648,
     1.6116161346435547,
     1.6185109615325928,
     1.6071336269378662,
     1.5965160131454468,
     1.591310739517212,
     1.5910385847091675,
     1.5895633697509766
    ],
    "mode": "control",
    "model_loaded_from_checkpoint": false,
    "offline_environment": true,
    "optimizer_sha256": "6973dbbf26f14b71755dfa998029c9895283c450703c9fd4827fc2b351beaa63",
    "scenario": "complete",
    "scheduler_sha256": "7b9e523d685a2faf6a45c0c4ff59aa618d900ddfa1255f1d4cf934a8dd733d41",
    "schema_version": "flashpilot-hf-run-summary-v1",
    "semantic_global_step": 8,
    "torch_version": "2.13.0+cpu",
    "trainable_state_sha256": "834764124dbded98a265dfc56aa6b0f3489d55cb121bc3f870c35aa0ec7f1cc3",
    "trainer_global_step": 8,
    "transformers_version": "5.14.1",
    "worker_pid": 31380
   },
   "control_process": {
    "completed_at": "2026-07-20T01:29:39.990458Z",
    "exit_code": 0,
    "exit_verified": true,
    "started_at": "2026-07-20T01:29:28.150015Z",
    "worker_pid": 31380
   },
   "crash_process": {
    "completed_at": "2026-07-20T01:29:47.021299Z",
    "exit_code": 1,
    "exit_verified": true,
    "started_at": "2026-07-20T01:29:40.025057Z",
    "worker_pid": 32392
   },
   "created_at": "2026-07-20T01:29:53.947653Z",
   "fault_scenario": "process-kill",
   "final_verdict": "VERIFIED",
   "forwarded_arguments": [],
   "framework": "transformers",
   "gate": {
    "achieved_rpo_steps": 0,
    "atol": 0.0,
    "checks": [
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.model",
      "expected": "present",
      "label": "Model state is present",
      "status": "pass"
     },
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.trainer-state",
      "expected": "present",
      "label": "Trainer state is present",
      "status": "pass"
     },
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.optimizer",
      "expected": "present",
      "label": "Optimizer state is present",
      "status": "pass"
     },
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.scheduler",
      "expected": "present",
      "label": "Scheduler state is present",
      "status": "pass"
     },
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.rng",
      "expected": "present",
      "label": "RNG state is present",
      "status": "pass"
     },
     {
      "actual": "verified=True, exit=1",
      "category": "process",
      "check_id": "process.real-termination",
      "expected": "verified nonzero exit",
      "label": "Checkpoint worker was really terminated",
      "status": "pass"
     },
     {
      "actual": "32392 -> 17736",
      "category": "process",
      "check_id": "process.distinct-recovery",
      "expected": "distinct PIDs",
      "label": "Recovery ran in a new process",
      "status": "pass"
     },
     {
      "actual": "8",
      "category": "trajectory",
      "check_id": "progress.global-step",
      "expected": "8",
      "label": "Recovered global step matches control",
      "status": "pass"
     },
     {
      "actual": "exact match",
      "category": "trajectory",
      "check_id": "trajectory.loss-history",
      "expected": "exact control loss history",
      "label": "Loss history exactly matches control",
      "status": "pass"
     },
     {
      "actual": "834764124dbded98a265dfc56aa6b0f3489d55cb121bc3f870c35aa0ec7f1cc3",
      "category": "state",
      "check_id": "state.trainable",
      "expected": "834764124dbded98a265dfc56aa6b0f3489d55cb121bc3f870c35aa0ec7f1cc3",
      "label": "Trainable state digest exactly matches control",
      "status": "pass"
     },
     {
      "actual": "0e2baf1f2c06964cc38cbfd3b4278dd50423475af83bb435195c815174ec63c9",
      "category": "state",
      "check_id": "state.evaluation",
      "expected": "0e2baf1f2c06964cc38cbfd3b4278dd50423475af83bb435195c815174ec63c9",
      "label": "Evaluation digest exactly matches control",
      "status": "pass"
     },
     {
      "actual": "6973dbbf26f14b71755dfa998029c9895283c450703c9fd4827fc2b351beaa63",
      "category": "state",
      "check_id": "state.optimizer",
      "expected": "6973dbbf26f14b71755dfa998029c9895283c450703c9fd4827fc2b351beaa63",
      "label": "Optimizer digest exactly matches control",
      "status": "pass"
     },
     {
      "actual": "7b9e523d685a2faf6a45c0c4ff59aa618d900ddfa1255f1d4cf934a8dd733d41",
      "category": "state",
      "check_id": "state.scheduler",
      "expected": "7b9e523d685a2faf6a45c0c4ff59aa618d900ddfa1255f1d4cf934a8dd733d41",
      "label": "Scheduler digest exactly matches control",
      "status": "pass"
     }
    ],
    "failed_check_ids": [],
    "max_rpo_steps": 0,
    "passed": true,
    "rtol": 0.0,
    "schema_version": "flashpilot-hf-recovery-gate-v1"
   },
   "html_report_path": "report.html",
   "limitations": [
    "Qualification covers the included local CPU Trainer contract, not arbitrary scripts.",
    "Offline environment controls prevent library-mediated Hub access; this is not an OS network sandbox.",
    "The attestation is unsigned and provides integrity, not publisher authentication."
   ],
   "model_checkpoint_load_succeeded": true,
   "model_only_diverged": false,
   "qualification_profile": "exact-training-resume",
   "recovery": {
    "checkpoint_step": 4,
    "evaluation_sha256": "0e2baf1f2c06964cc38cbfd3b4278dd50423475af83bb435195c815174ec63c9",
    "loss_history": [
     1.6094427108764648,
     1.6116161346435547,
     1.6185109615325928,
     1.6071336269378662,
     1.5965160131454468,
     1.591310739517212,
     1.5910385847091675,
     1.5895633697509766
    ],
    "mode": "recover",
    "model_loaded_from_checkpoint": true,
    "offline_environment": true,
    "optimizer_sha256": "6973dbbf26f14b71755dfa998029c9895283c450703c9fd4827fc2b351beaa63",
    "scenario": "complete",
    "scheduler_sha256": "7b9e523d685a2faf6a45c0c4ff59aa618d900ddfa1255f1d4cf934a8dd733d41",
    "schema_version": "flashpilot-hf-run-summary-v1",
    "semantic_global_step": 8,
    "torch_version": "2.13.0+cpu",
    "trainable_state_sha256": "834764124dbded98a265dfc56aa6b0f3489d55cb121bc3f870c35aa0ec7f1cc3",
    "trainer_global_step": 8,
    "transformers_version": "5.14.1",
    "worker_pid": 17736
   },
   "recovery_process": {
    "completed_at": "2026-07-20T01:29:53.931964Z",
    "exit_code": 0,
    "exit_verified": true,
    "started_at": "2026-07-20T01:29:47.044215Z",
    "worker_pid": 17736
   },
   "report_path": "report.md",
   "result_path": "result.json",
   "run_id": "30498446481a4d779ccc9c84417daf76",
   "scenario": "complete",
   "schema_version": "flashpilot-hf-qualification-v1",
   "script_path": "inputs/train.py",
   "verified_persisted_bytes": 41635
  },
  "source_run": "milestone13-hf-complete",
  "subtitle": "Real kill, new process, identical trajectory, attestation issued.",
  "title": "Hugging Face — complete checkpoint",
  "verdict": "VERIFIED"
 },
 {
  "attestation": {
   "adapter": "native-pytorch",
   "atol": 0.0,
   "checkpoint_file_count": 8,
   "checkpoint_logical_bytes": 27681,
   "checkpoint_path": "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004",
   "checkpoint_sha256": "6d939aa4a2dc8f2b9b0670dc36e45d2b871c4de395898ba319dca03e12269958",
   "checks_passed": 24,
   "checks_total": 24,
   "code_commit": "97267a3515c9b9add31a63487149d5757a758f0d",
   "control_digest": "1fc72fdf21487afe7b32da833d2300cd9a68f0c0c6f3ce1456910a5102a92997",
   "control_evaluation_digest": "a42a6d25c8aaf6674130ef63439f6fd415824bd23ff9cd6a7c0ca0305be3ef9a",
   "dependency_environment_path": "environment.json",
   "dependency_environment_sha256": "912884832a38948a9fff9afec9f41377e5b27a49d336ff0229a541d28d29677f",
   "evidence_manifest_path": "evidence-manifest.json",
   "evidence_manifest_sha256": "89f18b1451a7f250f1db9422251ff7e040ad20bf7bedc641c55f18d606a69bab",
   "fault_scenario": "process_termination",
   "framework": "native-pytorch",
   "framework_version": "2.13.0+cpu",
   "html_report_path": "report.html",
   "issued_at": "2026-07-20T01:29:13.076645Z",
   "limitations": [
    "This is a machine-verifiable experiment record, not legal certification.",
    "The attestation is unsigned and provides integrity, not publisher authentication.",
    "Physical NAND writes, write amplification, and SSD lifetime were not measured."
   ],
   "max_rpo_steps": 0,
   "original_worker_pid": 27632,
   "persistence_contract_path": "persistence-contract.json",
   "persistence_contract_sha256": "760789d83b39b7e8943254158cbf6202bca2e87790cd560f06a4202c51ff3295",
   "qualification_profile": "exact-training-resume",
   "recovery_worker_pid": 31396,
   "report_path": "report.md",
   "result_path": "result.json",
   "resumed_digest": "1fc72fdf21487afe7b32da833d2300cd9a68f0c0c6f3ce1456910a5102a92997",
   "resumed_evaluation_digest": "a42a6d25c8aaf6674130ef63439f6fd415824bd23ff9cd6a7c0ca0305be3ef9a",
   "rpo_steps": 0,
   "rto_seconds": 3.965455,
   "rtol": 0.0,
   "run_id": "milestone13-native",
   "schema_version": "flashpilot-attestation-v1",
   "signature_status": "unsigned",
   "source_tree_state": "dirty",
   "verdict": "verified",
   "verified_persisted_bytes": 27681
  },
  "attestation_junit": "<?xml version='1.0' encoding='utf-8'?>\n<testsuite name=\"flashpilot.attestation-verification\" tests=\"8\" failures=\"0\" errors=\"0\" skipped=\"0\">\n  <properties>\n    <property name=\"verdict\" value=\"VERIFIED\" />\n    <property name=\"attestation_sha256\" value=\"377663fe94f4abb153d94570b3b8e420f764761788a6820d66b83eb9efd78ce5\" />\n  </properties>\n  <testcase classname=\"flashpilot.attestation\" name=\"schema.attestation\">\n    <system-out>RecoveryAttestationV1 schema is valid.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"integrity.evidence-manifest\">\n    <system-out>Evidence manifest schema and SHA-256 passed.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"integrity.evidence-files\">\n    <system-out>Closed inventory verified 54 evidence artifacts.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"integrity.environment\">\n    <system-out>Dependency environment identity is consistent.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"consistency.contract\">\n    <system-out>Contract hash and deterministic minimum agree.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"consistency.result\">\n    <system-out>Result, gate, process, trajectory, RPO, and RTO agree.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"consistency.reports\">\n    <system-out>Markdown and HTML are exact result-derived views.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.attestation\" name=\"integrity.checkpoint\">\n    <system-out>Referenced checkpoint hash and metrics agree.</system-out>\n  </testcase>\n</testsuite>\n",
  "contract": {
   "adapter": "native-pytorch",
   "assumptions": [
    "CPU-only controlled workload",
    "Only residual-adapter parameters are trainable"
   ],
   "framework": "native-pytorch",
   "items": [
    {
     "evidence_ids": [
      "restore:model-state"
     ],
     "exactness": "exact",
     "identity_controls": [
      "manifest-entry",
      "sha256-checksum"
     ],
     "reason": "The trainable residual adapter must restore exactly.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "adapter"
    },
    {
     "evidence_ids": [
      "base:presence",
      "base:sha256"
     ],
     "exactness": "exact",
     "identity_controls": [
      "base-artifact-identity",
      "base-artifact-sha256"
     ],
     "reason": "The adapter must bind to the exact immutable frozen base.",
     "recovery_source": "immutable_reference",
     "requirement": "required",
     "state_id": "base_model_identity"
    },
    {
     "evidence_ids": [
      "process:next-step"
     ],
     "exactness": "exact",
     "identity_controls": [
      "global-seed",
      "global-step"
     ],
     "reason": "The controlled workload derives the next batch from seed and global step.",
     "recovery_source": "deterministic_recompute",
     "requirement": "required",
     "state_id": "batch_position"
    },
    {
     "evidence_ids": [
      "manifest:global-step"
     ],
     "exactness": "exact",
     "identity_controls": [
      "manifest-entry",
      "sha256-checksum"
     ],
     "reason": "The exact completed-step position must restore.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "global_step"
    },
    {
     "evidence_ids": [
      "restore:numpy-rng"
     ],
     "exactness": "exact",
     "identity_controls": [
      "manifest-entry",
      "sha256-checksum"
     ],
     "reason": "NumPy RNG progression must restore exactly.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "numpy_rng"
    },
    {
     "evidence_ids": [
      "restore:optimizer-state"
     ],
     "exactness": "exact",
     "identity_controls": [
      "manifest-entry",
      "sha256-checksum"
     ],
     "reason": "AdamW continuation state must restore exactly.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "optimizer"
    },
    {
     "evidence_ids": [
      "restore:python-rng"
     ],
     "exactness": "exact",
     "identity_controls": [
      "manifest-entry",
      "sha256-checksum"
     ],
     "reason": "Python RNG progression must restore exactly.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "python_rng"
    },
    {
     "evidence_ids": [
      "restore:scheduler-state"
     ],
     "exactness": "exact",
     "identity_controls": [
      "manifest-entry",
      "sha256-checksum"
     ],
     "reason": "LinearLR continuation state must restore exactly.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "scheduler"
    },
    {
     "evidence_ids": [
      "restore:torch-rng"
     ],
     "exactness": "exact",
     "identity_controls": [
      "manifest-entry",
      "sha256-checksum"
     ],
     "reason": "Torch RNG progression, including dropout, must restore exactly.",
     "recovery_source": "checkpoint",
     "requirement": "required",
     "state_id": "torch_rng"
    }
   ],
   "max_rpo_steps": 0,
   "qualification_profile": "exact-training-resume",
   "schema_version": "flashpilot-persistence-contract-v1",
   "warnings": [
    "Only the deterministic Recovery Gate can verify recovery."
   ]
  },
  "environment": {
   "code_commit": "97267a3515c9b9add31a63487149d5757a758f0d",
   "cpu_only": true,
   "dependencies": [
    {
     "name": "flashpilot",
     "version": "0.1.0"
    },
    {
     "name": "numpy",
     "version": "2.5.1"
    },
    {
     "name": "openai",
     "version": "2.46.0"
    },
    {
     "name": "pydantic",
     "version": "2.13.4"
    },
    {
     "name": "rich",
     "version": "14.3.4"
    },
    {
     "name": "torch",
     "version": "2.13.0+cpu"
    },
    {
     "name": "typer",
     "version": "0.27.0"
    }
   ],
   "deterministic_algorithms": true,
   "platform": "Windows-11-10.0.26200-SP0",
   "python_version": "3.12.13",
   "schema_version": "flashpilot-dependency-environment-v1",
   "source_tree_state": "dirty",
   "torch_threads": 1
  },
  "evidence_files": {
   "agent/failure/captured-live-metadata.json": "ewogICJmaXh0dXJlX3Byb3ZlbmFuY2UiOiAibm90X2FwcGxpY2FibGUiLAogICJsaXZlX29yX2ZpeHR1cmUiOiAibGl2ZSIsCiAgIm1vZGVsIjogImdwdC01LjYiLAogICJvdXRwdXRfc2NoZW1hX3ZlcnNpb24iOiAiZmFpbHVyZS1hbmFseXNpcy12MiIsCiAgInByb21wdF92ZXJzaW9uIjogInYyIiwKICAicHJvdmlkZXIiOiAib3BlbmFpIiwKICAicmVxdWVzdF9zaGEyNTYiOiAiZWFhNmY3ODE4ZWNkYWY0ODI1MjUwODE1MTRkY2NmYmZlNzQ4YWU3OWIwZDE3YzFhNzE5YTVlNjBiZmM1YmEyZSIsCiAgInJlc3BvbnNlX2lkIjogInJlc3BfMGQ3ZTgwOGNkNzIyZjk3ZjAxNmE1YTkwZjAzMDA0ODE5MDhkMjJlN2JlZmExNWUzZmUiLAogICJyb2xlIjogImZhaWx1cmUtYW5hbHlzaXMiLAogICJzY2hlbWFfdmVyc2lvbiI6ICJhZ2VudC1jYWxsLW1ldGFkYXRhLXYxIiwKICAic291cmNlIjogImNhcHR1cmVkX2xpdmVfcmVzcG9uc2UiLAogICJzdG9yZSI6IGZhbHNlLAogICJ0aW1lc3RhbXAiOiAiMjAyNi0wNy0xN1QyMDozMTowOS43NzE4MjBaIiwKICAidmFsaWRhdGlvbl9zdGF0dXMiOiAiYWNjZXB0ZWQiCn0K",
   "agent/failure/metadata.json": "ewogICJmaXh0dXJlX3Byb3ZlbmFuY2UiOiAibGl2ZV9ncHRfNV82X2NhcHR1cmUiLAogICJsaXZlX29yX2ZpeHR1cmUiOiAiZml4dHVyZSIsCiAgIm1vZGVsIjogImdwdC01LjYiLAogICJvdXRwdXRfc2NoZW1hX3ZlcnNpb24iOiAiZmFpbHVyZS1hbmFseXNpcy12MiIsCiAgInByb21wdF92ZXJzaW9uIjogInYyIiwKICAicHJvdmlkZXIiOiAiZml4dHVyZSIsCiAgInJlcXVlc3Rfc2hhMjU2IjogImFlMGFiOWVhNjRkYWQ1ZGQ2OGQzNDM3ZDI3NjQ5OTg3Mjk1NjM3NjMwZDQ3NjQ3ZDliMmYyN2Y5ZGIwNmIxNzgiLAogICJyZXNwb25zZV9pZCI6IG51bGwsCiAgInJvbGUiOiAiZmFpbHVyZS1hbmFseXNpcyIsCiAgInNjaGVtYV92ZXJzaW9uIjogImFnZW50LWNhbGwtbWV0YWRhdGEtdjEiLAogICJzb3VyY2UiOiAiY2FwdHVyZWRfbGl2ZV9yZXNwb25zZV9yZXBsYXkiLAogICJzdG9yZSI6IGZhbHNlLAogICJ0aW1lc3RhbXAiOiAiMjAyNi0wNy0yMFQwMToyOTowNS4xNjAzOTZaIiwKICAidmFsaWRhdGlvbl9zdGF0dXMiOiAiYWNjZXB0ZWQiCn0K",
   "agent/failure/request.redacted.json": "ewogICJjaGVja3BvaW50X2NvbnRyYWN0IjogewogICAgImNvcnJlY3RuZXNzX3ByaW9yaXR5IjogInN0cmljdCIsCiAgICAicmVxdWlyZWRfaW50ZWdyaXR5X2NvbnRyb2xzIjogWwogICAgICAibWFuaWZlc3QiLAogICAgICAiY2hlY2tzdW1zIiwKICAgICAgImNvbXBsZXRpb25fbWFya2VyIiwKICAgICAgImF0b21pY19jb21taXQiLAogICAgICAiYmFzZV9hcnRpZmFjdF9oYXNoIgogICAgXSwKICAgICJyZXF1aXJlZF9zdGF0ZSI6IFsKICAgICAgImFkYXB0ZXIiLAogICAgICAib3B0aW1pemVyIiwKICAgICAgInNjaGVkdWxlciIsCiAgICAgICJnbG9iYWxfc3RlcCIsCiAgICAgICJweXRob25fcm5nIiwKICAgICAgIm51bXB5X3JuZyIsCiAgICAgICJ0b3JjaF9ybmciLAogICAgICAiYmFzZV9tb2RlbF9pZGVudGl0eSIKICAgIF0KICB9LAogICJjcmFzaF9tZXRhZGF0YSI6IHsKICAgICJjaGVja3BvaW50X2lkIjogImNoZWNrcG9pbnQtc3RlcC0wMDAwMDQiLAogICAgImNoZWNrcG9pbnRfc3RlcCI6IDQsCiAgICAibGFzdF9jb21wbGV0ZWRfc3RlcCI6IDQsCiAgICAicmVjb3Zlcnlfd29ya2VyX3BpZCI6IDE2NjAwLAogICAgInRlcm1pbmF0aW9uX2V4aXRfY29kZSI6IDEsCiAgICAidGVybWluYXRpb25fbWV0aG9kIjogIlRlcm1pbmF0ZVByb2Nlc3MgdmlhIHN1YnByb2Nlc3MuUG9wZW4ua2lsbCIsCiAgICAid29ya2VyX3BpZCI6IDMxNDEyCiAgfSwKICAiZXZpZGVuY2VfY2F0YWxvZyI6IHsKICAgICJiYXNlOnByZXNlbmNlIjogIkJhc2UgYXJ0aWZhY3QgcHJlc2VudCB3aGVuIHJlcXVpcmVkIiwKICAgICJiYXNlOnNoYTI1NiI6ICJCYXNlIGFydGlmYWN0IGhhc2ggbWF0Y2hlcyIsCiAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIjogIk5vIG1hbmRhdG9yeSBjb250cmFjdCByZXF1aXJlbWVudCB3YXMgc2lsZW50bHkgb21pdHRlZCIsCiAgICAiaW50ZWdyaXR5OmNvbXBsZXRpb24tbWFya2VyIjogIkNvbXBsZXRpb24gbWFya2VyIHByZXNlbnQiLAogICAgImludGVncml0eTpzaGEyNTYiOiAiQWxsIHBheWxvYWQgY2hlY2tzdW1zIHZhbGlkIiwKICAgICJtYW5pZmVzdDpnbG9iYWwtc3RlcCI6ICJDaGVja3BvaW50IGdsb2JhbCBzdGVwIGlzIHZhbGlkIiwKICAgICJtYW5pZmVzdDpzY2hlbWEiOiAiTWFuaWZlc3Qgc2NoZW1hIHZhbGlkIiwKICAgICJwcm9jZXNzOm5leHQtc3RlcCI6ICJSZXN1bWVkIHJ1biBjb250aW51ZXMgZnJvbSB0aGUgZXhwZWN0ZWQgbmV4dCBzdGVwIiwKICAgICJwcm9jZXNzOm9yaWdpbmFsLXBpZCI6ICJPcmlnaW5hbCB3b3JrZXIgUElEIGlzIHJlY29yZGVkIiwKICAgICJwcm9jZXNzOnJlY292ZXJ5LWV4aXQiOiAiUmVjb3Zlcnkgd29ya2VyIGV4aXRzIHN1Y2Nlc3NmdWxseSIsCiAgICAicHJvY2VzczpyZWNvdmVyeS1waWQiOiAiUmVjb3ZlcnkgdXNlcyBhIGRpZmZlcmVudCBQSUQiLAogICAgInByb2Nlc3M6dGVybWluYXRpb24iOiAiT3JpZ2luYWwgd29ya2VyIHRlcm1pbmF0aW9uIGlzIHZlcmlmaWVkIiwKICAgICJyZXN0b3JlOm1vZGVsLXN0YXRlIjogIk1vZGVsIG9yIGFkYXB0ZXIgc3RhdGUgcmVzdG9yZXMiLAogICAgInJlc3RvcmU6bnVtcHktcm5nIjogIk51bVB5IFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICJyZXN0b3JlOm9wdGltaXplci1zdGF0ZSI6ICJPcHRpbWl6ZXIgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAicmVzdG9yZTpweXRob24tcm5nIjogIlB5dGhvbiBSTkcgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAicmVzdG9yZTpzY2hlZHVsZXItc3RhdGUiOiAiU2NoZWR1bGVyIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgInJlc3RvcmU6dG9yY2gtcm5nIjogIlRvcmNoIFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICJyb2xsYmFjazphY2hpZXZlZCI6ICJBY2hpZXZlZCByb2xsYmFjayBpcyB3aXRoaW4gdGhlIGhhcmQgbGltaXQiLAogICAgInNhZmV0eTpwYXRoLWNvbnRhaW5tZW50IjogIkFsbCBtYW5hZ2VkIHdyaXRlIHBhdGhzIHBhc3NlZCBjb250YWlubWVudCIsCiAgICAidHJhamVjdG9yeTpjaGVja3BvaW50LWV2YWx1YXRpb24iOiAiRml4ZWQgZXZhbHVhdGlvbiBhZnRlciByZXN0b3JlIG1hdGNoZXMiLAogICAgInRyYWplY3Rvcnk6ZmluYWwtZXZhbHVhdGlvbiI6ICJGaW5hbCBldmFsdWF0aW9uIGxvZ2l0cyBtYXRjaCBjb250cm9sIiwKICAgICJ0cmFqZWN0b3J5OmZpbmFsLXRyYWluYWJsZSI6ICJGaW5hbCB0cmFpbmFibGUgcGFyYW1ldGVycyBtYXRjaCBjb250cm9sIiwKICAgICJ0cmFqZWN0b3J5Omxvc3MtaGlzdG9yeSI6ICJDb250aW51ZWQgbG9zcyB0cmFqZWN0b3J5IG1hdGNoZXMgY29udHJvbCIKICB9LAogICJnYXRlX2NoZWNrcyI6IFsKICAgIHsKICAgICAgImFjdHVhbCI6ICJjaGVja3BvaW50LW1hbmlmZXN0LXYxIiwKICAgICAgImNhdGVnb3J5IjogIkludGVncml0eSIsCiAgICAgICJjaGVja19pZCI6ICJpbnRlZ3JpdHkubWFuaWZlc3Rfc2NoZW1hIiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJtYW5pZmVzdDpzY2hlbWEiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJjaGVja3BvaW50LW1hbmlmZXN0LXYxIiwKICAgICAgImxhYmVsIjogIk1hbmlmZXN0IHNjaGVtYSB2YWxpZCIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAicHJlc2VudCIsCiAgICAgICJjYXRlZ29yeSI6ICJJbnRlZ3JpdHkiLAogICAgICAiY2hlY2tfaWQiOiAiaW50ZWdyaXR5LmNvbXBsZXRpb25fbWFya2VyIiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJpbnRlZ3JpdHk6Y29tcGxldGlvbi1tYXJrZXIiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJDT01QTEVURSBwcmVzZW50IGluIGZpbmFsIGNoZWNrcG9pbnQiLAogICAgICAibGFiZWwiOiAiQ29tcGxldGlvbiBtYXJrZXIgcHJlc2VudCIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAiMiBwYXlsb2FkcyB2YWxpZGF0ZWQiLAogICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgImNoZWNrX2lkIjogImludGVncml0eS5jaGVja3N1bXMiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgImludGVncml0eTpzaGEyNTYiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJldmVyeSBtYW5pZmVzdCBwYXlsb2FkIG1hdGNoZXMgU0hBLTI1NiBhbmQgc2l6ZSIsCiAgICAgICJsYWJlbCI6ICJBbGwgcGF5bG9hZCBjaGVja3N1bXMgdmFsaWQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInByZXNlbnQiLAogICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgImNoZWNrX2lkIjogImludGVncml0eS5iYXNlX3ByZXNlbnQiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgImJhc2U6cHJlc2VuY2UiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJjb250YWluZWQgaW1tdXRhYmxlIGJhc2UgYXJ0aWZhY3QiLAogICAgICAibGFiZWwiOiAiQmFzZSBhcnRpZmFjdCBwcmVzZW50IHdoZW4gcmVxdWlyZWQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogImMxN2NjODk5NGM4ZjBmZTZkZWYzMjQyM2IwZTVkOWVmZWRmZmIzY2Q3MWM3ZGU5NjMxZjI2Y2Y1MDU5MjVkODYiLAogICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgImNoZWNrX2lkIjogImludGVncml0eS5iYXNlX2hhc2giLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgImJhc2U6c2hhMjU2IgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAiYzE3Y2M4OTk0YzhmMGZlNmRlZjMyNDIzYjBlNWQ5ZWZlZGZmYjNjZDcxYzdkZTk2MzFmMjZjZjUwNTkyNWQ4NiIsCiAgICAgICJsYWJlbCI6ICJCYXNlIGFydGlmYWN0IGhhc2ggbWF0Y2hlcyIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAibWFuaWZlc3Q9NCwgZXZlbnQ9NCwgcmVzdG9yZWQ9NCIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5nbG9iYWxfc3RlcCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAibWFuaWZlc3Q6Z2xvYmFsLXN0ZXAiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICIwIDwgc3RlcCA8IDgsIGNvbnNpc3RlbnQgYWNyb3NzIHJlc3RvcmUiLAogICAgICAibGFiZWwiOiAiQ2hlY2twb2ludCBnbG9iYWwgc3RlcCBpcyB2YWxpZCIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAic2VyaWFsaXplZD1UcnVlLCBkaWdlc3RfbWF0Y2g9VHJ1ZSIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5tb2RlbF9vcl9hZGFwdGVyIiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJyZXN0b3JlOm1vZGVsLXN0YXRlIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBhZGFwdGVyIGFuZCBleGFjdCB0cmFpbmFibGUtc3RhdGUgZGlnZXN0IiwKICAgICAgImxhYmVsIjogIk1vZGVsIG9yIGFkYXB0ZXIgc3RhdGUgcmVzdG9yZXMiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1GYWxzZSIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5vcHRpbWl6ZXIiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJlc3RvcmU6b3B0aW1pemVyLXN0YXRlIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBvcHRpbWl6ZXIgd2l0aCBleGFjdCBkaWdlc3QiLAogICAgICAibGFiZWwiOiAiT3B0aW1pemVyIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1GYWxzZSIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5zY2hlZHVsZXIiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJlc3RvcmU6c2NoZWR1bGVyLXN0YXRlIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBzY2hlZHVsZXIgd2l0aCBleGFjdCBkaWdlc3QiLAogICAgICAibGFiZWwiOiAiU2NoZWR1bGVyIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1UcnVlIiwKICAgICAgImNhdGVnb3J5IjogIlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlIiwKICAgICAgImNoZWNrX2lkIjogInN0YXRlLnB5dGhvbl9ybmciLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJlc3RvcmU6cHl0aG9uLXJuZyIKICAgICAgXSwKICAgICAgImV4cGVjdGVkIjogInNlcmlhbGl6ZWQgc3RhdGUgd2l0aCBleGFjdCBkaWdlc3QiLAogICAgICAibGFiZWwiOiAiUHl0aG9uIFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICAgInN0YXR1cyI6ICJmYWlsIgogICAgfSwKICAgIHsKICAgICAgImFjdHVhbCI6ICJzZXJpYWxpemVkPUZhbHNlLCBkaWdlc3RfbWF0Y2g9VHJ1ZSIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5udW1weV9ybmciLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJlc3RvcmU6bnVtcHktcm5nIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBzdGF0ZSB3aXRoIGV4YWN0IGRpZ2VzdCIsCiAgICAgICJsYWJlbCI6ICJOdW1QeSBSTkcgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAgICJzdGF0dXMiOiAiZmFpbCIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAic2VyaWFsaXplZD1GYWxzZSwgZGlnZXN0X21hdGNoPUZhbHNlIiwKICAgICAgImNhdGVnb3J5IjogIlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlIiwKICAgICAgImNoZWNrX2lkIjogInN0YXRlLnRvcmNoX3JuZyIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicmVzdG9yZTp0b3JjaC1ybmciCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJzZXJpYWxpemVkIHN0YXRlIHdpdGggZXhhY3QgZGlnZXN0IiwKICAgICAgImxhYmVsIjogIlRvcmNoIFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICAgInN0YXR1cyI6ICJmYWlsIgogICAgfSwKICAgIHsKICAgICAgImFjdHVhbCI6ICJmaXJzdCBiYXRjaCBhdCA0LCBmaXJzdCBjb21wbGV0aW9uIGF0IDUiLAogICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLm5leHRfc3RlcCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicHJvY2VzczpuZXh0LXN0ZXAiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJmaXJzdCBiYXRjaCBhdCA0LCBmaXJzdCBjb21wbGV0aW9uIGF0IDUiLAogICAgICAibGFiZWwiOiAiUmVzdW1lZCBydW4gY29udGludWVzIGZyb20gdGhlIGV4cGVjdGVkIG5leHQgc3RlcCIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAiMzE0MTIiLAogICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLm9yaWdpbmFsX3BpZCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicHJvY2VzczpvcmlnaW5hbC1waWQiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICIzMTQxMiIsCiAgICAgICJsYWJlbCI6ICJPcmlnaW5hbCB3b3JrZXIgUElEIGlzIHJlY29yZGVkIiwKICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgfSwKICAgIHsKICAgICAgImFjdHVhbCI6ICJtZXRob2Q9VGVybWluYXRlUHJvY2VzcyB2aWEgc3VicHJvY2Vzcy5Qb3Blbi5raWxsLCBleGl0PTEsIHZlcmlmaWVkPVRydWUiLAogICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLmV4cGVjdGVkX3Rlcm1pbmF0aW9uIiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJwcm9jZXNzOnRlcm1pbmF0aW9uIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAicGFyZW50IHRlcm1pbmF0aW9uIHdpdGggbm9uemVybyBleGl0IGNvZGUiLAogICAgICAibGFiZWwiOiAiT3JpZ2luYWwgd29ya2VyIHRlcm1pbmF0aW9uIGlzIHZlcmlmaWVkIiwKICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgfSwKICAgIHsKICAgICAgImFjdHVhbCI6ICIxNjYwMCIsCiAgICAgICJjYXRlZ29yeSI6ICJQcm9jZXNzIHJlY292ZXJ5IiwKICAgICAgImNoZWNrX2lkIjogInByb2Nlc3MubmV3X3JlY292ZXJ5X3BpZCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicHJvY2VzczpyZWNvdmVyeS1waWQiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJQSUQgZGlmZmVyZW50IGZyb20gMzE0MTIiLAogICAgICAibGFiZWwiOiAiUmVjb3ZlcnkgdXNlcyBhIGRpZmZlcmVudCBQSUQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogImV4aXQ9MCwgdmVyaWZpZWQ9VHJ1ZSIsCiAgICAgICJjYXRlZ29yeSI6ICJQcm9jZXNzIHJlY292ZXJ5IiwKICAgICAgImNoZWNrX2lkIjogInByb2Nlc3MucmVjb3ZlcnlfZXhpdCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicHJvY2VzczpyZWNvdmVyeS1leGl0IgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAiZXhpdCBjb2RlIDAiLAogICAgICAibGFiZWwiOiAiUmVjb3Zlcnkgd29ya2VyIGV4aXRzIHN1Y2Nlc3NmdWxseSIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAiMCBzdGVwcyIsCiAgICAgICJjYXRlZ29yeSI6ICJTYWZldHkgYW5kIHJvbGxiYWNrIiwKICAgICAgImNoZWNrX2lkIjogInJvbGxiYWNrLmhhcmRfbGltaXQiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJvbGxiYWNrOmFjaGlldmVkIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAiPD0gMCBzdGVwcyIsCiAgICAgICJsYWJlbCI6ICJBY2hpZXZlZCByb2xsYmFjayBpcyB3aXRoaW4gdGhlIGhhcmQgbGltaXQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogImQ2MDU3MmFlYTEyZjkxOTYwZjNmMDAzMGJkZmRjYTU1ZmRhZmUwNTkxNDZjNzIzMGFmOTA5NDkyMzgxMWQzMTIiLAogICAgICAiY2F0ZWdvcnkiOiAiVHJhamVjdG9yeSBjb3JyZWN0bmVzcyIsCiAgICAgICJjaGVja19pZCI6ICJ0cmFqZWN0b3J5LmNoZWNrcG9pbnRfZXZhbHVhdGlvbiIsCiAgICAgICJkZXRhaWxzIjogIkV4YWN0IFNIQS0yNTYgY29tcGFyaXNvbjsgbm8gbnVtZXJpY2FsIHRvbGVyYW5jZSBpcyBhcHBsaWVkLiIsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInRyYWplY3Rvcnk6Y2hlY2twb2ludC1ldmFsdWF0aW9uIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAiZDYwNTcyYWVhMTJmOTE5NjBmM2YwMDMwYmRmZGNhNTVmZGFmZTA1OTE0NmM3MjMwYWY5MDk0OTIzODExZDMxMiIsCiAgICAgICJsYWJlbCI6ICJGaXhlZCBldmFsdWF0aW9uIGFmdGVyIHJlc3RvcmUgbWF0Y2hlcyIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAiZDI4NTQ3ZTgyZGM0MTJkNTgwNjBlOGJlNjRkZWI1MjE5MWI3YjI1ODU2MWJlNDc4NzQ2OTRiMWM1NDZlY2E2NiIsCiAgICAgICJjYXRlZ29yeSI6ICJUcmFqZWN0b3J5IGNvcnJlY3RuZXNzIiwKICAgICAgImNoZWNrX2lkIjogInRyYWplY3RvcnkuZmluYWxfdHJhaW5hYmxlIiwKICAgICAgImRldGFpbHMiOiAiRXhhY3QgU0hBLTI1NiBjb21wYXJpc29uOyBubyBudW1lcmljYWwgdG9sZXJhbmNlIGlzIGFwcGxpZWQuIiwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAidHJhamVjdG9yeTpmaW5hbC10cmFpbmFibGUiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICIxZmM3MmZkZjIxNDg3YWZlN2IzMmRhODMzZDIzMDBjZDlhNjhmMGMwYzZmM2NlMTQ1NjkxMGE1MTAyYTkyOTk3IiwKICAgICAgImxhYmVsIjogIkZpbmFsIHRyYWluYWJsZSBwYXJhbWV0ZXJzIG1hdGNoIGNvbnRyb2wiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogIjQzNDZhMmQ3N2IzNzA3NmI4NTNkNDUyOTk4MTgyNGVkZDU0OTUzOGY5MzhkNDk2NDIyMDg5OTE0OWRkNWI0Y2QiLAogICAgICAiY2F0ZWdvcnkiOiAiVHJhamVjdG9yeSBjb3JyZWN0bmVzcyIsCiAgICAgICJjaGVja19pZCI6ICJ0cmFqZWN0b3J5LmZpbmFsX2V2YWx1YXRpb24iLAogICAgICAiZGV0YWlscyI6ICJFeGFjdCBTSEEtMjU2IGNvbXBhcmlzb247IG5vIG51bWVyaWNhbCB0b2xlcmFuY2UgaXMgYXBwbGllZC4iLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJ0cmFqZWN0b3J5OmZpbmFsLWV2YWx1YXRpb24iCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJhNDJhNmQyNWM4YWFmNjY3NDEzMGVmNjM0MzlmNmZkNDE1ODI0YmQyM2ZmOWNkNmE3YzBjYTAzMDViZTNlZjlhIiwKICAgICAgImxhYmVsIjogIkZpbmFsIGV2YWx1YXRpb24gbG9naXRzIG1hdGNoIGNvbnRyb2wiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInNlcXVlbmNlIGRpZmZlcnMiLAogICAgICAiY2F0ZWdvcnkiOiAiVHJhamVjdG9yeSBjb3JyZWN0bmVzcyIsCiAgICAgICJjaGVja19pZCI6ICJ0cmFqZWN0b3J5Lmxvc3NfaGlzdG9yeSIsCiAgICAgICJkZXRhaWxzIjogIkV4YWN0IGZsb2F0IHNlcXVlbmNlIGNvbXBhcmlzb247IG5vIG51bWVyaWNhbCB0b2xlcmFuY2UgaXMgYXBwbGllZC4iLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJ0cmFqZWN0b3J5Omxvc3MtaGlzdG9yeSIKICAgICAgXSwKICAgICAgImV4cGVjdGVkIjogImV4YWN0IGxvc3Mgc2VxdWVuY2UgZXF1YWxpdHkiLAogICAgICAibGFiZWwiOiAiQ29udGludWVkIGxvc3MgdHJhamVjdG9yeSBtYXRjaGVzIGNvbnRyb2wiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogImNvbnRhaW5lZCIsCiAgICAgICJjYXRlZ29yeSI6ICJTYWZldHkgYW5kIHJvbGxiYWNrIiwKICAgICAgImNoZWNrX2lkIjogInNhZmV0eS5wYXRoX2NvbnRhaW5tZW50IiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJzYWZldHk6cGF0aC1jb250YWlubWVudCIKICAgICAgXSwKICAgICAgImV4cGVjdGVkIjogImFsbCBwYXRocyBjb250YWluZWQ7IHN5bWxpbmsgZXNjYXBlcyByZWplY3RlZCIsCiAgICAgICJsYWJlbCI6ICJBbGwgbWFuYWdlZCB3cml0ZSBwYXRocyBwYXNzZWQgY29udGFpbm1lbnQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogIm1hbmlmZXN0IGxhY2tzOiBudW1weV9ybmcsIG9wdGltaXplciwgcHl0aG9uX3JuZywgc2NoZWR1bGVyLCB0b3JjaF9ybmciLAogICAgICAiY2F0ZWdvcnkiOiAiU2FmZXR5IGFuZCByb2xsYmFjayIsCiAgICAgICJjaGVja19pZCI6ICJjb250cmFjdC5ub19tYW5kYXRvcnlfb21pc3Npb24iLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgImNvbnRyYWN0Om1hbmRhdG9yeS1zdGF0ZSIKICAgICAgXSwKICAgICAgImV4cGVjdGVkIjogImFsbCBtYW5kYXRvcnkgY29udGludWF0aW9uIHN0YXRlIGRlY2xhcmVkIiwKICAgICAgImxhYmVsIjogIk5vIG1hbmRhdG9yeSBjb250cmFjdCByZXF1aXJlbWVudCB3YXMgc2lsZW50bHkgb21pdHRlZCIsCiAgICAgICJzdGF0dXMiOiAiZmFpbCIKICAgIH0KICBdLAogICJpbnRlZ3JpdHlfc3VtbWFyeSI6IHsKICAgICJjaGVja3BvaW50X2xvYWRfc3VjY2VlZGVkIjogdHJ1ZSwKICAgICJjaGVja3N1bXNfdmFsaWQiOiB0cnVlLAogICAgImNvbXBsZXRpb25fbWFya2VyX3ByZXNlbnQiOiB0cnVlLAogICAgIm1hbmlmZXN0X3ZhbGlkIjogdHJ1ZQogIH0sCiAgIm1hbmlmZXN0X3N1bW1hcnkiOiB7CiAgICAiZ2xvYmFsX3N0ZXAiOiA0LAogICAgImhhc19iYXNlX3JlZmVyZW5jZSI6IHRydWUsCiAgICAicGF5bG9hZF9yb2xlcyI6IFsKICAgICAgImFkYXB0ZXIiLAogICAgICAic3RhdGUiCiAgICBdLAogICAgInByb2ZpbGUiOiAiY2kiLAogICAgInNjaGVtYV92ZXJzaW9uIjogImNoZWNrcG9pbnQtbWFuaWZlc3QtdjEiLAogICAgInNlcmlhbGl6ZWRfc3RhdGUiOiBbCiAgICAgICJhZGFwdGVyIiwKICAgICAgImdsb2JhbF9zdGVwIiwKICAgICAgImNvbmZpZyIsCiAgICAgICJiYXNlX21vZGVsX2lkZW50aXR5IgogICAgXQogIH0sCiAgInJlc3RvcmVfb3JkZXIiOiBbCiAgICAidmFsaWRhdGUgY2hlY2twb2ludCBtZXRhZGF0YSBhbmQgcGF5bG9hZCBjaGVja3N1bXMiLAogICAgInZhbGlkYXRlIGltbXV0YWJsZSBiYXNlIGlkZW50aXR5IHdoZW4gcmVmZXJlbmNlZCIsCiAgICAibG9hZCBkZWNsYXJlZCBtb2RlbCBzdGF0ZSIsCiAgICAicmVzdW1lIGZyb20gdGhlIHJlc3RvcmVkIGdsb2JhbCBzdGVwIgogIF0sCiAgInNhdmVfcmVzdG9yZV9zdW1tYXJ5IjogewogICAgImludGVncml0eV9jb250cm9scyI6IFsKICAgICAgIm1hbmlmZXN0IiwKICAgICAgIlNIQS0yNTYgY2hlY2tzdW1zIiwKICAgICAgImNvbXBsZXRpb24gbWFya2VyIiwKICAgICAgImF0b21pYyBkaXJlY3RvcnkgY29tbWl0IiwKICAgICAgImJhc2UgYXJ0aWZhY3QgU0hBLTI1NiIKICAgIF0sCiAgICAicmVzdG9yZWRfZ2xvYmFsX3N0ZXAiOiA0LAogICAgInNlcmlhbGl6ZWRfc3RhdGUiOiBbCiAgICAgICJhZGFwdGVyIiwKICAgICAgImdsb2JhbF9zdGVwIiwKICAgICAgImNvbmZpZyIsCiAgICAgICJiYXNlX21vZGVsX2lkZW50aXR5IgogICAgXQogIH0sCiAgInNjaGVtYV92ZXJzaW9uIjogInNhbml0aXplZC1mYWlsdXJlLXYxIiwKICAic3RhdGVfZGlmZmVyZW5jZXMiOiB7CiAgICAiY2hlY2twb2ludF90cmFpbmFibGVfbWF0Y2giOiB0cnVlLAogICAgIm51bXB5X3JuZ19tYXRjaCI6IHRydWUsCiAgICAib3B0aW1pemVyX21hdGNoIjogZmFsc2UsCiAgICAicHl0aG9uX3JuZ19tYXRjaCI6IHRydWUsCiAgICAic2NoZWR1bGVyX21hdGNoIjogZmFsc2UsCiAgICAidG9yY2hfcm5nX21hdGNoIjogZmFsc2UKICB9LAogICJ0cmFqZWN0b3J5X3N1bW1hcnkiOiB7CiAgICAiY2hlY2twb2ludF9zdGVwIjogNCwKICAgICJmaW5hbF9ldmFsdWF0aW9uX21hdGNoIjogZmFsc2UsCiAgICAiZmluYWxfc3RlcCI6IDgsCiAgICAiZmluYWxfdHJhaW5hYmxlX21hdGNoIjogZmFsc2UsCiAgICAibG9zc19oaXN0b3J5X21hdGNoIjogZmFsc2UKICB9LAogICJ1c2VyX29iamVjdGl2ZSI6IHsKICAgICJoYXJkX3JvbGxiYWNrX2xpbWl0X3N0ZXBzIjogMCwKICAgICJyZWNvdmVyeV9jb3JyZWN0bmVzcyI6ICJzdHJpY3QiCiAgfSwKICAid29ya2xvYWRfY2FwYWJpbGl0aWVzIjogewogICAgImFkYXB0ZXJfbmFtZSI6ICJuYXRpdmUtcHl0b3JjaCIsCiAgICAiYXNzdW1wdGlvbnMiOiBbCiAgICAgICJDUFUtb25seSBjb250cm9sbGVkIHdvcmtsb2FkIiwKICAgICAgIk9ubHkgcmVzaWR1YWwtYWRhcHRlciBwYXJhbWV0ZXJzIGFyZSB0cmFpbmFibGUiCiAgICBdLAogICAgImJhdGNoX3Bvc2l0aW9uX2lzX3N0ZXBfZGVyaXZlZCI6IHRydWUsCiAgICAiZnJhbWV3b3JrIjogIm5hdGl2ZS1weXRvcmNoIiwKICAgICJoYXNfZnJvemVuX2Jhc2UiOiB0cnVlLAogICAgImhhc190cmFpbmFibGVfYWRhcHRlciI6IHRydWUsCiAgICAib3B0aW1pemVyX3R5cGUiOiAiQWRhbVciLAogICAgInNjaGVkdWxlcl90eXBlIjogIkxpbmVhckxSIiwKICAgICJzdXBwb3J0ZWRfcmVwYWlyX2FjdGlvbnMiOiBbCiAgICAgICJwZXJzaXN0X29wdGltaXplcl9zdGF0ZSIsCiAgICAgICJwZXJzaXN0X3NjaGVkdWxlcl9zdGF0ZSIsCiAgICAgICJwZXJzaXN0X3B5dGhvbl9ybmdfc3RhdGUiLAogICAgICAicGVyc2lzdF9udW1weV9ybmdfc3RhdGUiLAogICAgICAicGVyc2lzdF90b3JjaF9ybmdfc3RhdGUiLAogICAgICAicmVzdG9yZV9zdGF0ZV9iZWZvcmVfbmV4dF9iYXRjaCIKICAgIF0sCiAgICAic3VwcG9ydGVkX3N0YXRlIjogWwogICAgICAibW9kZWwiLAogICAgICAiYWRhcHRlciIsCiAgICAgICJvcHRpbWl6ZXIiLAogICAgICAic2NoZWR1bGVyIiwKICAgICAgImdsb2JhbF9zdGVwIiwKICAgICAgInB5dGhvbl9ybmciLAogICAgICAibnVtcHlfcm5nIiwKICAgICAgInRvcmNoX3JuZyIsCiAgICAgICJiYXNlX21vZGVsX2lkZW50aXR5IgogICAgXSwKICAgICJ1c2VzX2N1ZGFfcm5nIjogZmFsc2UsCiAgICAidXNlc19kcm9wb3V0IjogdHJ1ZSwKICAgICJ1c2VzX251bXB5X3JuZyI6IHRydWUsCiAgICAidXNlc19weXRob25fcm5nIjogdHJ1ZSwKICAgICJ1c2VzX3RvcmNoX3JuZyI6IHRydWUKICB9Cn0K",
   "agent/failure/response.parsed.json": "ewogICJhZmZlY3RlZF9nYXRlX2NoZWNrcyI6IFsKICAgICJzdGF0ZS5vcHRpbWl6ZXIiLAogICAgInN0YXRlLnNjaGVkdWxlciIsCiAgICAic3RhdGUucHl0aG9uX3JuZyIsCiAgICAic3RhdGUubnVtcHlfcm5nIiwKICAgICJzdGF0ZS50b3JjaF9ybmciLAogICAgInRyYWplY3RvcnkuZmluYWxfdHJhaW5hYmxlIiwKICAgICJ0cmFqZWN0b3J5LmZpbmFsX2V2YWx1YXRpb24iLAogICAgInRyYWplY3RvcnkubG9zc19oaXN0b3J5IiwKICAgICJjb250cmFjdC5ub19tYW5kYXRvcnlfb21pc3Npb24iCiAgXSwKICAiY29uZmlkZW5jZSI6ICJoaWdoIiwKICAiY29uZmlybWluZ19ldmlkZW5jZSI6IFsKICAgICJyZXN0b3JlOm9wdGltaXplci1zdGF0ZSIsCiAgICAicmVzdG9yZTpzY2hlZHVsZXItc3RhdGUiLAogICAgInJlc3RvcmU6cHl0aG9uLXJuZyIsCiAgICAicmVzdG9yZTpudW1weS1ybmciLAogICAgInJlc3RvcmU6dG9yY2gtcm5nIiwKICAgICJ0cmFqZWN0b3J5OmZpbmFsLXRyYWluYWJsZSIsCiAgICAidHJhamVjdG9yeTpmaW5hbC1ldmFsdWF0aW9uIiwKICAgICJ0cmFqZWN0b3J5Omxvc3MtaGlzdG9yeSIsCiAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIgogIF0sCiAgImxpbWl0YXRpb25zIjogWwogICAgIlRoZSBwYWNrYWdlIGRlbW9uc3RyYXRlcyB0aGUgb21pc3Npb25zIGFuZCByZXN1bHRpbmcgZGl2ZXJnZW5jZSBidXQgZG9lcyBub3QgZXN0YWJsaXNoIHRoYXQgYW55IHByb3Bvc2VkIHJlcGFpciBoYXMgYmVlbiBpbXBsZW1lbnRlZCBvciB2YWxpZGF0ZWQuIiwKICAgICJFeGFjdCByZWNvdmVyeSByZW1haW5zIHN1YmplY3QgdG8gZGV0ZXJtaW5pc3RpYyB2YWxpZGF0aW9uIHVzaW5nIGEgbmV3bHkgcHJvZHVjZWQgY2hlY2twb2ludCBjb250YWluaW5nIGFsbCBtYW5kYXRvcnkgc3RhdGUuIiwKICAgICJUaGUgbWF0Y2hpbmcgUHl0aG9uIGFuZCBOdW1QeSBSTkcgZGlnZXN0cyBkbyBub3Qgc2F0aXNmeSB0aGUgc2VyaWFsaXphdGlvbiByZXF1aXJlbWVudCBiZWNhdXNlIHRob3NlIHN0YXRlcyB3ZXJlIG5vdCBwcmVzZW50IGluIHRoZSBjaGVja3BvaW50LiIKICBdLAogICJyZXBhaXJfcGxhbiI6IHsKICAgICJhY3Rpb25zIjogWwogICAgICB7CiAgICAgICAgImFjdGlvbiI6ICJjaGFuZ2Vfc3VwcG9ydGVkX2NoZWNrcG9pbnRfc3RyYXRlZ3kiLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIgogICAgICAgIF0sCiAgICAgICAgInJlYXNvbiI6ICJUaGUgY3VycmVudCBzdHJhdGVneSBhZHZlcnRpc2VzIG5vIHN1cHBvcnRlZCByZXBhaXIgYWN0aW9ucyBhbmQgbXVzdCBiZSByZXBsYWNlZCBvciBleHRlbmRlZCB0byBzdXBwb3J0IGFsbCBtYW5kYXRvcnkgY29udGludWF0aW9uIHN0YXRlLiIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3Rpb24iOiAicGVyc2lzdF9vcHRpbWl6ZXJfc3RhdGUiLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAicmVzdG9yZTpvcHRpbWl6ZXItc3RhdGUiLAogICAgICAgICAgImNvbnRyYWN0Om1hbmRhdG9yeS1zdGF0ZSIsCiAgICAgICAgICAidHJhamVjdG9yeTpmaW5hbC10cmFpbmFibGUiLAogICAgICAgICAgInRyYWplY3Rvcnk6bG9zcy1oaXN0b3J5IgogICAgICAgIF0sCiAgICAgICAgInJlYXNvbiI6ICJTZXJpYWxpemUgdGhlIGNvbXBsZXRlIG9wdGltaXplciBzdGF0ZSByZXF1aXJlZCBmb3IgZXhhY3QgY29udGludWF0aW9uLiIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3Rpb24iOiAicGVyc2lzdF9zY2hlZHVsZXJfc3RhdGUiLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAicmVzdG9yZTpzY2hlZHVsZXItc3RhdGUiLAogICAgICAgICAgImNvbnRyYWN0Om1hbmRhdG9yeS1zdGF0ZSIsCiAgICAgICAgICAidHJhamVjdG9yeTpmaW5hbC10cmFpbmFibGUiLAogICAgICAgICAgInRyYWplY3Rvcnk6bG9zcy1oaXN0b3J5IgogICAgICAgIF0sCiAgICAgICAgInJlYXNvbiI6ICJTZXJpYWxpemUgc2NoZWR1bGVyIHByb2dyZXNzIHNvIHJlc3VtZWQgbGVhcm5pbmctcmF0ZSBiZWhhdmlvciBtYXRjaGVzIHRoZSB1bmludGVycnVwdGVkIHJ1bi4iCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0aW9uIjogInBlcnNpc3RfcHl0aG9uX3JuZ19zdGF0ZSIsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJyZXN0b3JlOnB5dGhvbi1ybmciLAogICAgICAgICAgImNvbnRyYWN0Om1hbmRhdG9yeS1zdGF0ZSIKICAgICAgICBdLAogICAgICAgICJyZWFzb24iOiAiU2VyaWFsaXplIFB5dGhvbiBSTkcgc3RhdGUgYmVjYXVzZSB0aGUgd29ya2xvYWQgcmVxdWlyZXMgaXQgZm9yIHN0cmljdCBjb250aW51YXRpb24uIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdGlvbiI6ICJwZXJzaXN0X251bXB5X3JuZ19zdGF0ZSIsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJyZXN0b3JlOm51bXB5LXJuZyIsCiAgICAgICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIgogICAgICAgIF0sCiAgICAgICAgInJlYXNvbiI6ICJTZXJpYWxpemUgTnVtUHkgUk5HIHN0YXRlIGJlY2F1c2UgdGhlIHdvcmtsb2FkIHVzZXMgTnVtUHkgcmFuZG9tbmVzcy4iCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0aW9uIjogInBlcnNpc3RfdG9yY2hfcm5nX3N0YXRlIiwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgInJlc3RvcmU6dG9yY2gtcm5nIiwKICAgICAgICAgICJjb250cmFjdDptYW5kYXRvcnktc3RhdGUiLAogICAgICAgICAgInRyYWplY3Rvcnk6ZmluYWwtdHJhaW5hYmxlIiwKICAgICAgICAgICJ0cmFqZWN0b3J5OmZpbmFsLWV2YWx1YXRpb24iLAogICAgICAgICAgInRyYWplY3Rvcnk6bG9zcy1oaXN0b3J5IgogICAgICAgIF0sCiAgICAgICAgInJlYXNvbiI6ICJTZXJpYWxpemUgVG9yY2ggUk5HIHN0YXRlIGJlY2F1c2UgdGhlIHdvcmtsb2FkIHVzZXMgVG9yY2ggcmFuZG9tbmVzcyBhbmQgZHJvcG91dC4iCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0aW9uIjogInJlc3RvcmVfc3RhdGVfYmVmb3JlX25leHRfYmF0Y2giLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAicmVzdG9yZTpvcHRpbWl6ZXItc3RhdGUiLAogICAgICAgICAgInJlc3RvcmU6c2NoZWR1bGVyLXN0YXRlIiwKICAgICAgICAgICJyZXN0b3JlOnB5dGhvbi1ybmciLAogICAgICAgICAgInJlc3RvcmU6bnVtcHktcm5nIiwKICAgICAgICAgICJyZXN0b3JlOnRvcmNoLXJuZyIsCiAgICAgICAgICAicHJvY2VzczpuZXh0LXN0ZXAiCiAgICAgICAgXSwKICAgICAgICAicmVhc29uIjogIlJlc3RvcmUgYWxsIHBlcnNpc3RlZCBvcHRpbWl6ZXIsIHNjaGVkdWxlciwgYW5kIFJORyBzdGF0ZSBiZWZvcmUgcHJvY2Vzc2luZyB0aGUgbmV4dCBiYXRjaC4iCiAgICAgIH0KICAgIF0sCiAgICAiYXNzdW1wdGlvbnMiOiBbCiAgICAgICJUaGUgY29udHJvbGxlZCBDUFUtb25seSB3b3JrbG9hZCBhbmQgZGVjbGFyZWQgc3RhdGUgcmVxdWlyZW1lbnRzIHJlbWFpbiB1bmNoYW5nZWQuIiwKICAgICAgIk5vIENVREEgUk5HIHN0YXRlIGlzIHJlcXVpcmVkLiIsCiAgICAgICJCYXRjaCBwb3NpdGlvbiByZW1haW5zIGRlcml2YWJsZSBmcm9tIHRoZSByZXN0b3JlZCBnbG9iYWwgc3RlcC4iCiAgICBdLAogICAgImV4cGVjdGVkX2dhdGVfaW1wcm92ZW1lbnRzIjogWwogICAgICAiTWFuZGF0b3J5IGNvbnRpbnVhdGlvbiBzdGF0ZSBpcyBkZWNsYXJlZCBhbmQgc2VyaWFsaXplZC4iLAogICAgICAiT3B0aW1pemVyLCBzY2hlZHVsZXIsIGFuZCByZXF1aXJlZCBSTkcgc3RhdGVzIGJlY29tZSByZXN0b3JhYmxlIHdpdGggZXhhY3QgZGlnZXN0cy4iLAogICAgICAiQ29udGludWVkIGxvc3NlcywgZmluYWwgdHJhaW5hYmxlIHBhcmFtZXRlcnMsIGFuZCBmaW5hbCBldmFsdWF0aW9uIG91dHB1dHMgY2FuIGJlIHJlLWV2YWx1YXRlZCBmb3IgZXhhY3QgYWdyZWVtZW50LiIKICAgIF0sCiAgICAicmlza3MiOiBbCiAgICAgICJUaGUgY3VycmVudCBjaGVja3BvaW50IHN0cmF0ZWd5IGV4cG9zZXMgbm8gc3VwcG9ydGVkIHJlcGFpciBhY3Rpb25zLCBzbyBhIGNvbXBhdGlibGUgc3RyYXRlZ3kgb3IgaW1wbGVtZW50YXRpb24gY2hhbmdlIGlzIHJlcXVpcmVkIGJlZm9yZSB0aGVzZSBhY3Rpb25zIGNhbiBiZSB2YWxpZGF0ZWQuIiwKICAgICAgIkV4aXN0aW5nIGNoZWNrcG9pbnRzIGxhY2tpbmcgdGhlIG9taXR0ZWQgc3RhdGUgY2Fubm90IHByb3ZpZGUgc3RyaWN0IGNvbnRpbnVhdGlvbiBmcm9tIHRob3NlIGNoZWNrcG9pbnRzLiIsCiAgICAgICJSZXN0b3JhdGlvbiBvcmRlcmluZyBlcnJvcnMgY291bGQgc3RpbGwgcHJvZHVjZSB0cmFqZWN0b3J5IGRpdmVyZ2VuY2UgZXZlbiBhZnRlciBhbGwgc3RhdGUgaXMgc2VyaWFsaXplZC4iCiAgICBdCiAgfSwKICAicm9vdF9jYXVzZV9oeXBvdGhlc2lzIjogIlRoZSBjaGVja3BvaW50IHN0cmF0ZWd5IHNlcmlhbGl6ZWQgdGhlIGFkYXB0ZXIgYW5kIGdsb2JhbCBzdGVwIGJ1dCBvbWl0dGVkIG1hbmRhdG9yeSBvcHRpbWl6ZXIsIHNjaGVkdWxlciwgUHl0aG9uIFJORywgTnVtUHkgUk5HLCBhbmQgVG9yY2ggUk5HIHN0YXRlLiBSZWNvdmVyeSB0aGVyZWZvcmUgcmVzdW1lZCB3aXRoIGluY29tcGxldGUgY29udGludWF0aW9uIHN0YXRlLCBjYXVzaW5nIGRpdmVyZ2VuY2UgaW4gbG9zc2VzLCBmaW5hbCB0cmFpbmFibGUgcGFyYW1ldGVycywgYW5kIGZpbmFsIGV2YWx1YXRpb24gb3V0cHV0cy4iLAogICJzY2hlbWFfdmVyc2lvbiI6ICJmYWlsdXJlLWFuYWx5c2lzLXYyIgp9Cg==",
   "agent/failure/validation.json": "ewogICJhY2NlcHRlZF9hY3Rpb25zIjogWwogICAgInBlcnNpc3Rfb3B0aW1pemVyX3N0YXRlIiwKICAgICJwZXJzaXN0X3NjaGVkdWxlcl9zdGF0ZSIsCiAgICAicGVyc2lzdF9weXRob25fcm5nX3N0YXRlIiwKICAgICJwZXJzaXN0X251bXB5X3JuZ19zdGF0ZSIsCiAgICAicGVyc2lzdF90b3JjaF9ybmdfc3RhdGUiLAogICAgInJlc3RvcmVfc3RhdGVfYmVmb3JlX25leHRfYmF0Y2giCiAgXSwKICAiYXR0ZW1wdF9udW1iZXIiOiAxLAogICJkZWNpc2lvbnMiOiBbCiAgICB7CiAgICAgICJhY3Rpb24iOiAiY2hhbmdlX3N1cHBvcnRlZF9jaGVja3BvaW50X3N0cmF0ZWd5IiwKICAgICAgImRpc3Bvc2l0aW9uIjogInVuc3VwcG9ydGVkIiwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIgogICAgICBdLAogICAgICAicmVhc29uIjogIktub3duIGFjdGlvbiBpcyB1bnN1cHBvcnRlZCBieSBOYXRpdmVQeVRvcmNoQWRhcHRlciBpbiBQMC4iCiAgICB9LAogICAgewogICAgICAiYWN0aW9uIjogInBlcnNpc3Rfb3B0aW1pemVyX3N0YXRlIiwKICAgICAgImRpc3Bvc2l0aW9uIjogImFjY2VwdGVkIiwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicmVzdG9yZTpvcHRpbWl6ZXItc3RhdGUiLAogICAgICAgICJjb250cmFjdDptYW5kYXRvcnktc3RhdGUiLAogICAgICAgICJ0cmFqZWN0b3J5OmZpbmFsLXRyYWluYWJsZSIsCiAgICAgICAgInRyYWplY3Rvcnk6bG9zcy1oaXN0b3J5IgogICAgICBdLAogICAgICAicmVhc29uIjogIlR5cGVkIGFjdGlvbiBpcyBzdXBwb3J0ZWQgYW5kIGxpbmtlZCB0byByZXF1ZXN0IGV2aWRlbmNlLiIKICAgIH0sCiAgICB7CiAgICAgICJhY3Rpb24iOiAicGVyc2lzdF9zY2hlZHVsZXJfc3RhdGUiLAogICAgICAiZGlzcG9zaXRpb24iOiAiYWNjZXB0ZWQiLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJyZXN0b3JlOnNjaGVkdWxlci1zdGF0ZSIsCiAgICAgICAgImNvbnRyYWN0Om1hbmRhdG9yeS1zdGF0ZSIsCiAgICAgICAgInRyYWplY3Rvcnk6ZmluYWwtdHJhaW5hYmxlIiwKICAgICAgICAidHJhamVjdG9yeTpsb3NzLWhpc3RvcnkiCiAgICAgIF0sCiAgICAgICJyZWFzb24iOiAiVHlwZWQgYWN0aW9uIGlzIHN1cHBvcnRlZCBhbmQgbGlua2VkIHRvIHJlcXVlc3QgZXZpZGVuY2UuIgogICAgfSwKICAgIHsKICAgICAgImFjdGlvbiI6ICJwZXJzaXN0X3B5dGhvbl9ybmdfc3RhdGUiLAogICAgICAiZGlzcG9zaXRpb24iOiAiYWNjZXB0ZWQiLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJyZXN0b3JlOnB5dGhvbi1ybmciLAogICAgICAgICJjb250cmFjdDptYW5kYXRvcnktc3RhdGUiCiAgICAgIF0sCiAgICAgICJyZWFzb24iOiAiVHlwZWQgYWN0aW9uIGlzIHN1cHBvcnRlZCBhbmQgbGlua2VkIHRvIHJlcXVlc3QgZXZpZGVuY2UuIgogICAgfSwKICAgIHsKICAgICAgImFjdGlvbiI6ICJwZXJzaXN0X251bXB5X3JuZ19zdGF0ZSIsCiAgICAgICJkaXNwb3NpdGlvbiI6ICJhY2NlcHRlZCIsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJlc3RvcmU6bnVtcHktcm5nIiwKICAgICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIgogICAgICBdLAogICAgICAicmVhc29uIjogIlR5cGVkIGFjdGlvbiBpcyBzdXBwb3J0ZWQgYW5kIGxpbmtlZCB0byByZXF1ZXN0IGV2aWRlbmNlLiIKICAgIH0sCiAgICB7CiAgICAgICJhY3Rpb24iOiAicGVyc2lzdF90b3JjaF9ybmdfc3RhdGUiLAogICAgICAiZGlzcG9zaXRpb24iOiAiYWNjZXB0ZWQiLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJyZXN0b3JlOnRvcmNoLXJuZyIsCiAgICAgICAgImNvbnRyYWN0Om1hbmRhdG9yeS1zdGF0ZSIsCiAgICAgICAgInRyYWplY3Rvcnk6ZmluYWwtdHJhaW5hYmxlIiwKICAgICAgICAidHJhamVjdG9yeTpmaW5hbC1ldmFsdWF0aW9uIiwKICAgICAgICAidHJhamVjdG9yeTpsb3NzLWhpc3RvcnkiCiAgICAgIF0sCiAgICAgICJyZWFzb24iOiAiVHlwZWQgYWN0aW9uIGlzIHN1cHBvcnRlZCBhbmQgbGlua2VkIHRvIHJlcXVlc3QgZXZpZGVuY2UuIgogICAgfSwKICAgIHsKICAgICAgImFjdGlvbiI6ICJyZXN0b3JlX3N0YXRlX2JlZm9yZV9uZXh0X2JhdGNoIiwKICAgICAgImRpc3Bvc2l0aW9uIjogImFjY2VwdGVkIiwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicmVzdG9yZTpvcHRpbWl6ZXItc3RhdGUiLAogICAgICAgICJyZXN0b3JlOnNjaGVkdWxlci1zdGF0ZSIsCiAgICAgICAgInJlc3RvcmU6cHl0aG9uLXJuZyIsCiAgICAgICAgInJlc3RvcmU6bnVtcHktcm5nIiwKICAgICAgICAicmVzdG9yZTp0b3JjaC1ybmciLAogICAgICAgICJwcm9jZXNzOm5leHQtc3RlcCIKICAgICAgXSwKICAgICAgInJlYXNvbiI6ICJUeXBlZCBhY3Rpb24gaXMgc3VwcG9ydGVkIGFuZCBsaW5rZWQgdG8gcmVxdWVzdCBldmlkZW5jZS4iCiAgICB9CiAgXSwKICAiZXhlY3V0aW9uX3BlcmZvcm1lZCI6IGZhbHNlLAogICJyZWplY3RlZF9hY3Rpb25zIjogW10sCiAgInNjaGVtYV92ZXJzaW9uIjogInJlcGFpci1wbGFuLXZhbGlkYXRpb24tdjEiLAogICJ1bnN1cHBvcnRlZF9hY3Rpb25zIjogWwogICAgImNoYW5nZV9zdXBwb3J0ZWRfY2hlY2twb2ludF9zdHJhdGVneSIKICBdCn0K",
   "agent/repair-attempt-admission.json": "ewogICJhZG1pdHRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjA1LjE5MTUwOVoiLAogICJhdHRlbXB0X251bWJlciI6IDEsCiAgImV4ZWN1dGlvbl9wZXJmb3JtZWQiOiBmYWxzZSwKICAic2NoZW1hX3ZlcnNpb24iOiAicmVwYWlyLWF0dGVtcHQtYWRtaXNzaW9uLXYxIgp9Cg==",
   "agent/repair/execution.json": "ewogICJhZG1pdHRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjA1LjE5MTUwOVoiLAogICJhcHBsaWVkX2FjdGlvbnMiOiBbCiAgICAicGVyc2lzdF9vcHRpbWl6ZXJfc3RhdGUiLAogICAgInBlcnNpc3Rfc2NoZWR1bGVyX3N0YXRlIiwKICAgICJwZXJzaXN0X3B5dGhvbl9ybmdfc3RhdGUiLAogICAgInBlcnNpc3RfbnVtcHlfcm5nX3N0YXRlIiwKICAgICJwZXJzaXN0X3RvcmNoX3JuZ19zdGF0ZSIsCiAgICAicmVzdG9yZV9zdGF0ZV9iZWZvcmVfbmV4dF9iYXRjaCIKICBdLAogICJhdHRlbXB0X251bWJlciI6IDEsCiAgImV4ZWN1dGlvbl9wZXJmb3JtZWQiOiB0cnVlLAogICJvcmlnaW5hbF9jb25maWciOiB7CiAgICAiaW5jbHVkZV9udW1weV9ybmciOiBmYWxzZSwKICAgICJpbmNsdWRlX29wdGltaXplciI6IGZhbHNlLAogICAgImluY2x1ZGVfcHl0aG9uX3JuZyI6IGZhbHNlLAogICAgImluY2x1ZGVfc2NoZWR1bGVyIjogZmFsc2UsCiAgICAiaW5jbHVkZV90b3JjaF9ybmciOiBmYWxzZSwKICAgICJyZXN0b3JlX2JlZm9yZV9uZXh0X2JhdGNoIjogZmFsc2UsCiAgICAic2NoZW1hX3ZlcnNpb24iOiAiY2hlY2twb2ludC1zdHJhdGVneS1jb25maWctdjEiLAogICAgInN0cmF0ZWd5X2lkIjogIm5hdGl2ZS1pbmNvbXBsZXRlLXYxIgogIH0sCiAgInJlamVjdGVkX2FjdGlvbnMiOiBbXSwKICAicmVwYWlyZWRfY29uZmlnIjogewogICAgImluY2x1ZGVfbnVtcHlfcm5nIjogdHJ1ZSwKICAgICJpbmNsdWRlX29wdGltaXplciI6IHRydWUsCiAgICAiaW5jbHVkZV9weXRob25fcm5nIjogdHJ1ZSwKICAgICJpbmNsdWRlX3NjaGVkdWxlciI6IHRydWUsCiAgICAiaW5jbHVkZV90b3JjaF9ybmciOiB0cnVlLAogICAgInJlc3RvcmVfYmVmb3JlX25leHRfYmF0Y2giOiB0cnVlLAogICAgInNjaGVtYV92ZXJzaW9uIjogImNoZWNrcG9pbnQtc3RyYXRlZ3ktY29uZmlnLXYxIiwKICAgICJzdHJhdGVneV9pZCI6ICJuYXRpdmUtcmVwYWlyZWQtY29tcGxldGUtdjEiCiAgfSwKICAic2NoZW1hX3ZlcnNpb24iOiAicmVwYWlyLWV4ZWN1dGlvbi12MSIsCiAgInVuc3VwcG9ydGVkX2FjdGlvbnMiOiBbCiAgICAiY2hhbmdlX3N1cHBvcnRlZF9jaGVja3BvaW50X3N0cmF0ZWd5IgogIF0KfQo=",
   "agent/repair/repaired-strategy.json": "ewogICJpbmNsdWRlX251bXB5X3JuZyI6IHRydWUsCiAgImluY2x1ZGVfb3B0aW1pemVyIjogdHJ1ZSwKICAiaW5jbHVkZV9weXRob25fcm5nIjogdHJ1ZSwKICAiaW5jbHVkZV9zY2hlZHVsZXIiOiB0cnVlLAogICJpbmNsdWRlX3RvcmNoX3JuZyI6IHRydWUsCiAgInJlc3RvcmVfYmVmb3JlX25leHRfYmF0Y2giOiB0cnVlLAogICJzY2hlbWFfdmVyc2lvbiI6ICJjaGVja3BvaW50LXN0cmF0ZWd5LWNvbmZpZy12MSIsCiAgInN0cmF0ZWd5X2lkIjogIm5hdGl2ZS1yZXBhaXJlZC1jb21wbGV0ZS12MSIKfQo=",
   "agent/request.redacted.json": "ewogICJjaGVja3BvaW50X2NvbnRyYWN0IjogewogICAgImNvcnJlY3RuZXNzX3ByaW9yaXR5IjogInN0cmljdCIsCiAgICAicmVxdWlyZWRfaW50ZWdyaXR5X2NvbnRyb2xzIjogWwogICAgICAibWFuaWZlc3QiLAogICAgICAiY2hlY2tzdW1zIiwKICAgICAgImNvbXBsZXRpb25fbWFya2VyIiwKICAgICAgImF0b21pY19jb21taXQiLAogICAgICAiYmFzZV9hcnRpZmFjdF9oYXNoIgogICAgXSwKICAgICJyZXF1aXJlZF9zdGF0ZSI6IFsKICAgICAgImFkYXB0ZXIiLAogICAgICAib3B0aW1pemVyIiwKICAgICAgInNjaGVkdWxlciIsCiAgICAgICJnbG9iYWxfc3RlcCIsCiAgICAgICJweXRob25fcm5nIiwKICAgICAgIm51bXB5X3JuZyIsCiAgICAgICJ0b3JjaF9ybmciLAogICAgICAiYmFzZV9tb2RlbF9pZGVudGl0eSIKICAgIF0KICB9LAogICJjcmFzaF9tZXRhZGF0YSI6IHsKICAgICJjaGVja3BvaW50X2lkIjogImNoZWNrcG9pbnQtc3RlcC0wMDAwMDQiLAogICAgImNoZWNrcG9pbnRfc3RlcCI6IDQsCiAgICAibGFzdF9jb21wbGV0ZWRfc3RlcCI6IDQsCiAgICAicmVjb3Zlcnlfd29ya2VyX3BpZCI6IDE2NjAwLAogICAgInRlcm1pbmF0aW9uX2V4aXRfY29kZSI6IDEsCiAgICAidGVybWluYXRpb25fbWV0aG9kIjogIlRlcm1pbmF0ZVByb2Nlc3MgdmlhIHN1YnByb2Nlc3MuUG9wZW4ua2lsbCIsCiAgICAid29ya2VyX3BpZCI6IDMxNDEyCiAgfSwKICAiZXZpZGVuY2VfY2F0YWxvZyI6IHsKICAgICJiYXNlOnByZXNlbmNlIjogIkJhc2UgYXJ0aWZhY3QgcHJlc2VudCB3aGVuIHJlcXVpcmVkIiwKICAgICJiYXNlOnNoYTI1NiI6ICJCYXNlIGFydGlmYWN0IGhhc2ggbWF0Y2hlcyIsCiAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIjogIk5vIG1hbmRhdG9yeSBjb250cmFjdCByZXF1aXJlbWVudCB3YXMgc2lsZW50bHkgb21pdHRlZCIsCiAgICAiaW50ZWdyaXR5OmNvbXBsZXRpb24tbWFya2VyIjogIkNvbXBsZXRpb24gbWFya2VyIHByZXNlbnQiLAogICAgImludGVncml0eTpzaGEyNTYiOiAiQWxsIHBheWxvYWQgY2hlY2tzdW1zIHZhbGlkIiwKICAgICJtYW5pZmVzdDpnbG9iYWwtc3RlcCI6ICJDaGVja3BvaW50IGdsb2JhbCBzdGVwIGlzIHZhbGlkIiwKICAgICJtYW5pZmVzdDpzY2hlbWEiOiAiTWFuaWZlc3Qgc2NoZW1hIHZhbGlkIiwKICAgICJwcm9jZXNzOm5leHQtc3RlcCI6ICJSZXN1bWVkIHJ1biBjb250aW51ZXMgZnJvbSB0aGUgZXhwZWN0ZWQgbmV4dCBzdGVwIiwKICAgICJwcm9jZXNzOm9yaWdpbmFsLXBpZCI6ICJPcmlnaW5hbCB3b3JrZXIgUElEIGlzIHJlY29yZGVkIiwKICAgICJwcm9jZXNzOnJlY292ZXJ5LWV4aXQiOiAiUmVjb3Zlcnkgd29ya2VyIGV4aXRzIHN1Y2Nlc3NmdWxseSIsCiAgICAicHJvY2VzczpyZWNvdmVyeS1waWQiOiAiUmVjb3ZlcnkgdXNlcyBhIGRpZmZlcmVudCBQSUQiLAogICAgInByb2Nlc3M6dGVybWluYXRpb24iOiAiT3JpZ2luYWwgd29ya2VyIHRlcm1pbmF0aW9uIGlzIHZlcmlmaWVkIiwKICAgICJyZXN0b3JlOm1vZGVsLXN0YXRlIjogIk1vZGVsIG9yIGFkYXB0ZXIgc3RhdGUgcmVzdG9yZXMiLAogICAgInJlc3RvcmU6bnVtcHktcm5nIjogIk51bVB5IFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICJyZXN0b3JlOm9wdGltaXplci1zdGF0ZSI6ICJPcHRpbWl6ZXIgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAicmVzdG9yZTpweXRob24tcm5nIjogIlB5dGhvbiBSTkcgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAicmVzdG9yZTpzY2hlZHVsZXItc3RhdGUiOiAiU2NoZWR1bGVyIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgInJlc3RvcmU6dG9yY2gtcm5nIjogIlRvcmNoIFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICJyb2xsYmFjazphY2hpZXZlZCI6ICJBY2hpZXZlZCByb2xsYmFjayBpcyB3aXRoaW4gdGhlIGhhcmQgbGltaXQiLAogICAgInNhZmV0eTpwYXRoLWNvbnRhaW5tZW50IjogIkFsbCBtYW5hZ2VkIHdyaXRlIHBhdGhzIHBhc3NlZCBjb250YWlubWVudCIsCiAgICAidHJhamVjdG9yeTpjaGVja3BvaW50LWV2YWx1YXRpb24iOiAiRml4ZWQgZXZhbHVhdGlvbiBhZnRlciByZXN0b3JlIG1hdGNoZXMiLAogICAgInRyYWplY3Rvcnk6ZmluYWwtZXZhbHVhdGlvbiI6ICJGaW5hbCBldmFsdWF0aW9uIGxvZ2l0cyBtYXRjaCBjb250cm9sIiwKICAgICJ0cmFqZWN0b3J5OmZpbmFsLXRyYWluYWJsZSI6ICJGaW5hbCB0cmFpbmFibGUgcGFyYW1ldGVycyBtYXRjaCBjb250cm9sIiwKICAgICJ0cmFqZWN0b3J5Omxvc3MtaGlzdG9yeSI6ICJDb250aW51ZWQgbG9zcyB0cmFqZWN0b3J5IG1hdGNoZXMgY29udHJvbCIKICB9LAogICJnYXRlX2NoZWNrcyI6IFsKICAgIHsKICAgICAgImFjdHVhbCI6ICJjaGVja3BvaW50LW1hbmlmZXN0LXYxIiwKICAgICAgImNhdGVnb3J5IjogIkludGVncml0eSIsCiAgICAgICJjaGVja19pZCI6ICJpbnRlZ3JpdHkubWFuaWZlc3Rfc2NoZW1hIiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJtYW5pZmVzdDpzY2hlbWEiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJjaGVja3BvaW50LW1hbmlmZXN0LXYxIiwKICAgICAgImxhYmVsIjogIk1hbmlmZXN0IHNjaGVtYSB2YWxpZCIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAicHJlc2VudCIsCiAgICAgICJjYXRlZ29yeSI6ICJJbnRlZ3JpdHkiLAogICAgICAiY2hlY2tfaWQiOiAiaW50ZWdyaXR5LmNvbXBsZXRpb25fbWFya2VyIiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJpbnRlZ3JpdHk6Y29tcGxldGlvbi1tYXJrZXIiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJDT01QTEVURSBwcmVzZW50IGluIGZpbmFsIGNoZWNrcG9pbnQiLAogICAgICAibGFiZWwiOiAiQ29tcGxldGlvbiBtYXJrZXIgcHJlc2VudCIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAiMiBwYXlsb2FkcyB2YWxpZGF0ZWQiLAogICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgImNoZWNrX2lkIjogImludGVncml0eS5jaGVja3N1bXMiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgImludGVncml0eTpzaGEyNTYiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJldmVyeSBtYW5pZmVzdCBwYXlsb2FkIG1hdGNoZXMgU0hBLTI1NiBhbmQgc2l6ZSIsCiAgICAgICJsYWJlbCI6ICJBbGwgcGF5bG9hZCBjaGVja3N1bXMgdmFsaWQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInByZXNlbnQiLAogICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgImNoZWNrX2lkIjogImludGVncml0eS5iYXNlX3ByZXNlbnQiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgImJhc2U6cHJlc2VuY2UiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJjb250YWluZWQgaW1tdXRhYmxlIGJhc2UgYXJ0aWZhY3QiLAogICAgICAibGFiZWwiOiAiQmFzZSBhcnRpZmFjdCBwcmVzZW50IHdoZW4gcmVxdWlyZWQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogImMxN2NjODk5NGM4ZjBmZTZkZWYzMjQyM2IwZTVkOWVmZWRmZmIzY2Q3MWM3ZGU5NjMxZjI2Y2Y1MDU5MjVkODYiLAogICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgImNoZWNrX2lkIjogImludGVncml0eS5iYXNlX2hhc2giLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgImJhc2U6c2hhMjU2IgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAiYzE3Y2M4OTk0YzhmMGZlNmRlZjMyNDIzYjBlNWQ5ZWZlZGZmYjNjZDcxYzdkZTk2MzFmMjZjZjUwNTkyNWQ4NiIsCiAgICAgICJsYWJlbCI6ICJCYXNlIGFydGlmYWN0IGhhc2ggbWF0Y2hlcyIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAibWFuaWZlc3Q9NCwgZXZlbnQ9NCwgcmVzdG9yZWQ9NCIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5nbG9iYWxfc3RlcCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAibWFuaWZlc3Q6Z2xvYmFsLXN0ZXAiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICIwIDwgc3RlcCA8IDgsIGNvbnNpc3RlbnQgYWNyb3NzIHJlc3RvcmUiLAogICAgICAibGFiZWwiOiAiQ2hlY2twb2ludCBnbG9iYWwgc3RlcCBpcyB2YWxpZCIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAic2VyaWFsaXplZD1UcnVlLCBkaWdlc3RfbWF0Y2g9VHJ1ZSIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5tb2RlbF9vcl9hZGFwdGVyIiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJyZXN0b3JlOm1vZGVsLXN0YXRlIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBhZGFwdGVyIGFuZCBleGFjdCB0cmFpbmFibGUtc3RhdGUgZGlnZXN0IiwKICAgICAgImxhYmVsIjogIk1vZGVsIG9yIGFkYXB0ZXIgc3RhdGUgcmVzdG9yZXMiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1GYWxzZSIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5vcHRpbWl6ZXIiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJlc3RvcmU6b3B0aW1pemVyLXN0YXRlIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBvcHRpbWl6ZXIgd2l0aCBleGFjdCBkaWdlc3QiLAogICAgICAibGFiZWwiOiAiT3B0aW1pemVyIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1GYWxzZSIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5zY2hlZHVsZXIiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJlc3RvcmU6c2NoZWR1bGVyLXN0YXRlIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBzY2hlZHVsZXIgd2l0aCBleGFjdCBkaWdlc3QiLAogICAgICAibGFiZWwiOiAiU2NoZWR1bGVyIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1UcnVlIiwKICAgICAgImNhdGVnb3J5IjogIlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlIiwKICAgICAgImNoZWNrX2lkIjogInN0YXRlLnB5dGhvbl9ybmciLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJlc3RvcmU6cHl0aG9uLXJuZyIKICAgICAgXSwKICAgICAgImV4cGVjdGVkIjogInNlcmlhbGl6ZWQgc3RhdGUgd2l0aCBleGFjdCBkaWdlc3QiLAogICAgICAibGFiZWwiOiAiUHl0aG9uIFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICAgInN0YXR1cyI6ICJmYWlsIgogICAgfSwKICAgIHsKICAgICAgImFjdHVhbCI6ICJzZXJpYWxpemVkPUZhbHNlLCBkaWdlc3RfbWF0Y2g9VHJ1ZSIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5udW1weV9ybmciLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJlc3RvcmU6bnVtcHktcm5nIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBzdGF0ZSB3aXRoIGV4YWN0IGRpZ2VzdCIsCiAgICAgICJsYWJlbCI6ICJOdW1QeSBSTkcgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAgICJzdGF0dXMiOiAiZmFpbCIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAic2VyaWFsaXplZD1GYWxzZSwgZGlnZXN0X21hdGNoPUZhbHNlIiwKICAgICAgImNhdGVnb3J5IjogIlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlIiwKICAgICAgImNoZWNrX2lkIjogInN0YXRlLnRvcmNoX3JuZyIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicmVzdG9yZTp0b3JjaC1ybmciCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJzZXJpYWxpemVkIHN0YXRlIHdpdGggZXhhY3QgZGlnZXN0IiwKICAgICAgImxhYmVsIjogIlRvcmNoIFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICAgInN0YXR1cyI6ICJmYWlsIgogICAgfSwKICAgIHsKICAgICAgImFjdHVhbCI6ICJmaXJzdCBiYXRjaCBhdCA0LCBmaXJzdCBjb21wbGV0aW9uIGF0IDUiLAogICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLm5leHRfc3RlcCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicHJvY2VzczpuZXh0LXN0ZXAiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJmaXJzdCBiYXRjaCBhdCA0LCBmaXJzdCBjb21wbGV0aW9uIGF0IDUiLAogICAgICAibGFiZWwiOiAiUmVzdW1lZCBydW4gY29udGludWVzIGZyb20gdGhlIGV4cGVjdGVkIG5leHQgc3RlcCIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAiMzE0MTIiLAogICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLm9yaWdpbmFsX3BpZCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicHJvY2VzczpvcmlnaW5hbC1waWQiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICIzMTQxMiIsCiAgICAgICJsYWJlbCI6ICJPcmlnaW5hbCB3b3JrZXIgUElEIGlzIHJlY29yZGVkIiwKICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgfSwKICAgIHsKICAgICAgImFjdHVhbCI6ICJtZXRob2Q9VGVybWluYXRlUHJvY2VzcyB2aWEgc3VicHJvY2Vzcy5Qb3Blbi5raWxsLCBleGl0PTEsIHZlcmlmaWVkPVRydWUiLAogICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLmV4cGVjdGVkX3Rlcm1pbmF0aW9uIiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJwcm9jZXNzOnRlcm1pbmF0aW9uIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAicGFyZW50IHRlcm1pbmF0aW9uIHdpdGggbm9uemVybyBleGl0IGNvZGUiLAogICAgICAibGFiZWwiOiAiT3JpZ2luYWwgd29ya2VyIHRlcm1pbmF0aW9uIGlzIHZlcmlmaWVkIiwKICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgfSwKICAgIHsKICAgICAgImFjdHVhbCI6ICIxNjYwMCIsCiAgICAgICJjYXRlZ29yeSI6ICJQcm9jZXNzIHJlY292ZXJ5IiwKICAgICAgImNoZWNrX2lkIjogInByb2Nlc3MubmV3X3JlY292ZXJ5X3BpZCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicHJvY2VzczpyZWNvdmVyeS1waWQiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJQSUQgZGlmZmVyZW50IGZyb20gMzE0MTIiLAogICAgICAibGFiZWwiOiAiUmVjb3ZlcnkgdXNlcyBhIGRpZmZlcmVudCBQSUQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogImV4aXQ9MCwgdmVyaWZpZWQ9VHJ1ZSIsCiAgICAgICJjYXRlZ29yeSI6ICJQcm9jZXNzIHJlY292ZXJ5IiwKICAgICAgImNoZWNrX2lkIjogInByb2Nlc3MucmVjb3ZlcnlfZXhpdCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicHJvY2VzczpyZWNvdmVyeS1leGl0IgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAiZXhpdCBjb2RlIDAiLAogICAgICAibGFiZWwiOiAiUmVjb3Zlcnkgd29ya2VyIGV4aXRzIHN1Y2Nlc3NmdWxseSIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAiMCBzdGVwcyIsCiAgICAgICJjYXRlZ29yeSI6ICJTYWZldHkgYW5kIHJvbGxiYWNrIiwKICAgICAgImNoZWNrX2lkIjogInJvbGxiYWNrLmhhcmRfbGltaXQiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJvbGxiYWNrOmFjaGlldmVkIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAiPD0gMCBzdGVwcyIsCiAgICAgICJsYWJlbCI6ICJBY2hpZXZlZCByb2xsYmFjayBpcyB3aXRoaW4gdGhlIGhhcmQgbGltaXQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogImQ2MDU3MmFlYTEyZjkxOTYwZjNmMDAzMGJkZmRjYTU1ZmRhZmUwNTkxNDZjNzIzMGFmOTA5NDkyMzgxMWQzMTIiLAogICAgICAiY2F0ZWdvcnkiOiAiVHJhamVjdG9yeSBjb3JyZWN0bmVzcyIsCiAgICAgICJjaGVja19pZCI6ICJ0cmFqZWN0b3J5LmNoZWNrcG9pbnRfZXZhbHVhdGlvbiIsCiAgICAgICJkZXRhaWxzIjogIkV4YWN0IFNIQS0yNTYgY29tcGFyaXNvbjsgbm8gbnVtZXJpY2FsIHRvbGVyYW5jZSBpcyBhcHBsaWVkLiIsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInRyYWplY3Rvcnk6Y2hlY2twb2ludC1ldmFsdWF0aW9uIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAiZDYwNTcyYWVhMTJmOTE5NjBmM2YwMDMwYmRmZGNhNTVmZGFmZTA1OTE0NmM3MjMwYWY5MDk0OTIzODExZDMxMiIsCiAgICAgICJsYWJlbCI6ICJGaXhlZCBldmFsdWF0aW9uIGFmdGVyIHJlc3RvcmUgbWF0Y2hlcyIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAiZDI4NTQ3ZTgyZGM0MTJkNTgwNjBlOGJlNjRkZWI1MjE5MWI3YjI1ODU2MWJlNDc4NzQ2OTRiMWM1NDZlY2E2NiIsCiAgICAgICJjYXRlZ29yeSI6ICJUcmFqZWN0b3J5IGNvcnJlY3RuZXNzIiwKICAgICAgImNoZWNrX2lkIjogInRyYWplY3RvcnkuZmluYWxfdHJhaW5hYmxlIiwKICAgICAgImRldGFpbHMiOiAiRXhhY3QgU0hBLTI1NiBjb21wYXJpc29uOyBubyBudW1lcmljYWwgdG9sZXJhbmNlIGlzIGFwcGxpZWQuIiwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAidHJhamVjdG9yeTpmaW5hbC10cmFpbmFibGUiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICIxZmM3MmZkZjIxNDg3YWZlN2IzMmRhODMzZDIzMDBjZDlhNjhmMGMwYzZmM2NlMTQ1NjkxMGE1MTAyYTkyOTk3IiwKICAgICAgImxhYmVsIjogIkZpbmFsIHRyYWluYWJsZSBwYXJhbWV0ZXJzIG1hdGNoIGNvbnRyb2wiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogIjQzNDZhMmQ3N2IzNzA3NmI4NTNkNDUyOTk4MTgyNGVkZDU0OTUzOGY5MzhkNDk2NDIyMDg5OTE0OWRkNWI0Y2QiLAogICAgICAiY2F0ZWdvcnkiOiAiVHJhamVjdG9yeSBjb3JyZWN0bmVzcyIsCiAgICAgICJjaGVja19pZCI6ICJ0cmFqZWN0b3J5LmZpbmFsX2V2YWx1YXRpb24iLAogICAgICAiZGV0YWlscyI6ICJFeGFjdCBTSEEtMjU2IGNvbXBhcmlzb247IG5vIG51bWVyaWNhbCB0b2xlcmFuY2UgaXMgYXBwbGllZC4iLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJ0cmFqZWN0b3J5OmZpbmFsLWV2YWx1YXRpb24iCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJhNDJhNmQyNWM4YWFmNjY3NDEzMGVmNjM0MzlmNmZkNDE1ODI0YmQyM2ZmOWNkNmE3YzBjYTAzMDViZTNlZjlhIiwKICAgICAgImxhYmVsIjogIkZpbmFsIGV2YWx1YXRpb24gbG9naXRzIG1hdGNoIGNvbnRyb2wiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInNlcXVlbmNlIGRpZmZlcnMiLAogICAgICAiY2F0ZWdvcnkiOiAiVHJhamVjdG9yeSBjb3JyZWN0bmVzcyIsCiAgICAgICJjaGVja19pZCI6ICJ0cmFqZWN0b3J5Lmxvc3NfaGlzdG9yeSIsCiAgICAgICJkZXRhaWxzIjogIkV4YWN0IGZsb2F0IHNlcXVlbmNlIGNvbXBhcmlzb247IG5vIG51bWVyaWNhbCB0b2xlcmFuY2UgaXMgYXBwbGllZC4iLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJ0cmFqZWN0b3J5Omxvc3MtaGlzdG9yeSIKICAgICAgXSwKICAgICAgImV4cGVjdGVkIjogImV4YWN0IGxvc3Mgc2VxdWVuY2UgZXF1YWxpdHkiLAogICAgICAibGFiZWwiOiAiQ29udGludWVkIGxvc3MgdHJhamVjdG9yeSBtYXRjaGVzIGNvbnRyb2wiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogImNvbnRhaW5lZCIsCiAgICAgICJjYXRlZ29yeSI6ICJTYWZldHkgYW5kIHJvbGxiYWNrIiwKICAgICAgImNoZWNrX2lkIjogInNhZmV0eS5wYXRoX2NvbnRhaW5tZW50IiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJzYWZldHk6cGF0aC1jb250YWlubWVudCIKICAgICAgXSwKICAgICAgImV4cGVjdGVkIjogImFsbCBwYXRocyBjb250YWluZWQ7IHN5bWxpbmsgZXNjYXBlcyByZWplY3RlZCIsCiAgICAgICJsYWJlbCI6ICJBbGwgbWFuYWdlZCB3cml0ZSBwYXRocyBwYXNzZWQgY29udGFpbm1lbnQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogIm1hbmlmZXN0IGxhY2tzOiBudW1weV9ybmcsIG9wdGltaXplciwgcHl0aG9uX3JuZywgc2NoZWR1bGVyLCB0b3JjaF9ybmciLAogICAgICAiY2F0ZWdvcnkiOiAiU2FmZXR5IGFuZCByb2xsYmFjayIsCiAgICAgICJjaGVja19pZCI6ICJjb250cmFjdC5ub19tYW5kYXRvcnlfb21pc3Npb24iLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgImNvbnRyYWN0Om1hbmRhdG9yeS1zdGF0ZSIKICAgICAgXSwKICAgICAgImV4cGVjdGVkIjogImFsbCBtYW5kYXRvcnkgY29udGludWF0aW9uIHN0YXRlIGRlY2xhcmVkIiwKICAgICAgImxhYmVsIjogIk5vIG1hbmRhdG9yeSBjb250cmFjdCByZXF1aXJlbWVudCB3YXMgc2lsZW50bHkgb21pdHRlZCIsCiAgICAgICJzdGF0dXMiOiAiZmFpbCIKICAgIH0KICBdLAogICJpbnRlZ3JpdHlfc3VtbWFyeSI6IHsKICAgICJjaGVja3BvaW50X2xvYWRfc3VjY2VlZGVkIjogdHJ1ZSwKICAgICJjaGVja3N1bXNfdmFsaWQiOiB0cnVlLAogICAgImNvbXBsZXRpb25fbWFya2VyX3ByZXNlbnQiOiB0cnVlLAogICAgIm1hbmlmZXN0X3ZhbGlkIjogdHJ1ZQogIH0sCiAgIm1hbmlmZXN0X3N1bW1hcnkiOiB7CiAgICAiZ2xvYmFsX3N0ZXAiOiA0LAogICAgImhhc19iYXNlX3JlZmVyZW5jZSI6IHRydWUsCiAgICAicGF5bG9hZF9yb2xlcyI6IFsKICAgICAgImFkYXB0ZXIiLAogICAgICAic3RhdGUiCiAgICBdLAogICAgInByb2ZpbGUiOiAiY2kiLAogICAgInNjaGVtYV92ZXJzaW9uIjogImNoZWNrcG9pbnQtbWFuaWZlc3QtdjEiLAogICAgInNlcmlhbGl6ZWRfc3RhdGUiOiBbCiAgICAgICJhZGFwdGVyIiwKICAgICAgImdsb2JhbF9zdGVwIiwKICAgICAgImNvbmZpZyIsCiAgICAgICJiYXNlX21vZGVsX2lkZW50aXR5IgogICAgXQogIH0sCiAgInJlc3RvcmVfb3JkZXIiOiBbCiAgICAidmFsaWRhdGUgY2hlY2twb2ludCBtZXRhZGF0YSBhbmQgcGF5bG9hZCBjaGVja3N1bXMiLAogICAgInZhbGlkYXRlIGltbXV0YWJsZSBiYXNlIGlkZW50aXR5IHdoZW4gcmVmZXJlbmNlZCIsCiAgICAibG9hZCBkZWNsYXJlZCBtb2RlbCBzdGF0ZSIsCiAgICAicmVzdW1lIGZyb20gdGhlIHJlc3RvcmVkIGdsb2JhbCBzdGVwIgogIF0sCiAgInNhdmVfcmVzdG9yZV9zdW1tYXJ5IjogewogICAgImludGVncml0eV9jb250cm9scyI6IFsKICAgICAgIm1hbmlmZXN0IiwKICAgICAgIlNIQS0yNTYgY2hlY2tzdW1zIiwKICAgICAgImNvbXBsZXRpb24gbWFya2VyIiwKICAgICAgImF0b21pYyBkaXJlY3RvcnkgY29tbWl0IiwKICAgICAgImJhc2UgYXJ0aWZhY3QgU0hBLTI1NiIKICAgIF0sCiAgICAicmVzdG9yZWRfZ2xvYmFsX3N0ZXAiOiA0LAogICAgInNlcmlhbGl6ZWRfc3RhdGUiOiBbCiAgICAgICJhZGFwdGVyIiwKICAgICAgImdsb2JhbF9zdGVwIiwKICAgICAgImNvbmZpZyIsCiAgICAgICJiYXNlX21vZGVsX2lkZW50aXR5IgogICAgXQogIH0sCiAgInNjaGVtYV92ZXJzaW9uIjogInNhbml0aXplZC1mYWlsdXJlLXYxIiwKICAic3RhdGVfZGlmZmVyZW5jZXMiOiB7CiAgICAiY2hlY2twb2ludF90cmFpbmFibGVfbWF0Y2giOiB0cnVlLAogICAgIm51bXB5X3JuZ19tYXRjaCI6IHRydWUsCiAgICAib3B0aW1pemVyX21hdGNoIjogZmFsc2UsCiAgICAicHl0aG9uX3JuZ19tYXRjaCI6IHRydWUsCiAgICAic2NoZWR1bGVyX21hdGNoIjogZmFsc2UsCiAgICAidG9yY2hfcm5nX21hdGNoIjogZmFsc2UKICB9LAogICJ0cmFqZWN0b3J5X3N1bW1hcnkiOiB7CiAgICAiY2hlY2twb2ludF9zdGVwIjogNCwKICAgICJmaW5hbF9ldmFsdWF0aW9uX21hdGNoIjogZmFsc2UsCiAgICAiZmluYWxfc3RlcCI6IDgsCiAgICAiZmluYWxfdHJhaW5hYmxlX21hdGNoIjogZmFsc2UsCiAgICAibG9zc19oaXN0b3J5X21hdGNoIjogZmFsc2UKICB9LAogICJ1c2VyX29iamVjdGl2ZSI6IHsKICAgICJoYXJkX3JvbGxiYWNrX2xpbWl0X3N0ZXBzIjogMCwKICAgICJyZWNvdmVyeV9jb3JyZWN0bmVzcyI6ICJzdHJpY3QiCiAgfSwKICAid29ya2xvYWRfY2FwYWJpbGl0aWVzIjogewogICAgImFkYXB0ZXJfbmFtZSI6ICJuYXRpdmUtcHl0b3JjaCIsCiAgICAiYXNzdW1wdGlvbnMiOiBbCiAgICAgICJDUFUtb25seSBjb250cm9sbGVkIHdvcmtsb2FkIiwKICAgICAgIk9ubHkgcmVzaWR1YWwtYWRhcHRlciBwYXJhbWV0ZXJzIGFyZSB0cmFpbmFibGUiCiAgICBdLAogICAgImJhdGNoX3Bvc2l0aW9uX2lzX3N0ZXBfZGVyaXZlZCI6IHRydWUsCiAgICAiZnJhbWV3b3JrIjogIm5hdGl2ZS1weXRvcmNoIiwKICAgICJoYXNfZnJvemVuX2Jhc2UiOiB0cnVlLAogICAgImhhc190cmFpbmFibGVfYWRhcHRlciI6IHRydWUsCiAgICAib3B0aW1pemVyX3R5cGUiOiAiQWRhbVciLAogICAgInNjaGVkdWxlcl90eXBlIjogIkxpbmVhckxSIiwKICAgICJzdXBwb3J0ZWRfcmVwYWlyX2FjdGlvbnMiOiBbCiAgICAgICJwZXJzaXN0X29wdGltaXplcl9zdGF0ZSIsCiAgICAgICJwZXJzaXN0X3NjaGVkdWxlcl9zdGF0ZSIsCiAgICAgICJwZXJzaXN0X3B5dGhvbl9ybmdfc3RhdGUiLAogICAgICAicGVyc2lzdF9udW1weV9ybmdfc3RhdGUiLAogICAgICAicGVyc2lzdF90b3JjaF9ybmdfc3RhdGUiLAogICAgICAicmVzdG9yZV9zdGF0ZV9iZWZvcmVfbmV4dF9iYXRjaCIKICAgIF0sCiAgICAic3VwcG9ydGVkX3N0YXRlIjogWwogICAgICAibW9kZWwiLAogICAgICAiYWRhcHRlciIsCiAgICAgICJvcHRpbWl6ZXIiLAogICAgICAic2NoZWR1bGVyIiwKICAgICAgImdsb2JhbF9zdGVwIiwKICAgICAgInB5dGhvbl9ybmciLAogICAgICAibnVtcHlfcm5nIiwKICAgICAgInRvcmNoX3JuZyIsCiAgICAgICJiYXNlX21vZGVsX2lkZW50aXR5IgogICAgXSwKICAgICJ1c2VzX2N1ZGFfcm5nIjogZmFsc2UsCiAgICAidXNlc19kcm9wb3V0IjogdHJ1ZSwKICAgICJ1c2VzX251bXB5X3JuZyI6IHRydWUsCiAgICAidXNlc19weXRob25fcm5nIjogdHJ1ZSwKICAgICJ1c2VzX3RvcmNoX3JuZyI6IHRydWUKICB9Cn0K",
   "environment.json": "ewogICJjb2RlX2NvbW1pdCI6ICI5NzI2N2EzNTE1YzliOWFkZDMxYTYzNDg3MTQ5ZDU3NTdhNzU4ZjBkIiwKICAiY3B1X29ubHkiOiB0cnVlLAogICJkZXBlbmRlbmNpZXMiOiBbCiAgICB7CiAgICAgICJuYW1lIjogImZsYXNocGlsb3QiLAogICAgICAidmVyc2lvbiI6ICIwLjEuMCIKICAgIH0sCiAgICB7CiAgICAgICJuYW1lIjogIm51bXB5IiwKICAgICAgInZlcnNpb24iOiAiMi41LjEiCiAgICB9LAogICAgewogICAgICAibmFtZSI6ICJvcGVuYWkiLAogICAgICAidmVyc2lvbiI6ICIyLjQ2LjAiCiAgICB9LAogICAgewogICAgICAibmFtZSI6ICJweWRhbnRpYyIsCiAgICAgICJ2ZXJzaW9uIjogIjIuMTMuNCIKICAgIH0sCiAgICB7CiAgICAgICJuYW1lIjogInJpY2giLAogICAgICAidmVyc2lvbiI6ICIxNC4zLjQiCiAgICB9LAogICAgewogICAgICAibmFtZSI6ICJ0b3JjaCIsCiAgICAgICJ2ZXJzaW9uIjogIjIuMTMuMCtjcHUiCiAgICB9LAogICAgewogICAgICAibmFtZSI6ICJ0eXBlciIsCiAgICAgICJ2ZXJzaW9uIjogIjAuMjcuMCIKICAgIH0KICBdLAogICJkZXRlcm1pbmlzdGljX2FsZ29yaXRobXMiOiB0cnVlLAogICJwbGF0Zm9ybSI6ICJXaW5kb3dzLTExLTEwLjAuMjYyMDAtU1AwIiwKICAicHl0aG9uX3ZlcnNpb24iOiAiMy4xMi4xMyIsCiAgInNjaGVtYV92ZXJzaW9uIjogImZsYXNocGlsb3QtZGVwZW5kZW5jeS1lbnZpcm9ubWVudC12MSIsCiAgInNvdXJjZV90cmVlX3N0YXRlIjogImRpcnR5IiwKICAidG9yY2hfdGhyZWFkcyI6IDEKfQo=",
   "initial/agent/request.redacted.json": "ewogICJjaGVja3BvaW50X2NvbnRyYWN0IjogewogICAgImNvcnJlY3RuZXNzX3ByaW9yaXR5IjogInN0cmljdCIsCiAgICAicmVxdWlyZWRfaW50ZWdyaXR5X2NvbnRyb2xzIjogWwogICAgICAibWFuaWZlc3QiLAogICAgICAiY2hlY2tzdW1zIiwKICAgICAgImNvbXBsZXRpb25fbWFya2VyIiwKICAgICAgImF0b21pY19jb21taXQiLAogICAgICAiYmFzZV9hcnRpZmFjdF9oYXNoIgogICAgXSwKICAgICJyZXF1aXJlZF9zdGF0ZSI6IFsKICAgICAgImFkYXB0ZXIiLAogICAgICAib3B0aW1pemVyIiwKICAgICAgInNjaGVkdWxlciIsCiAgICAgICJnbG9iYWxfc3RlcCIsCiAgICAgICJweXRob25fcm5nIiwKICAgICAgIm51bXB5X3JuZyIsCiAgICAgICJ0b3JjaF9ybmciLAogICAgICAiYmFzZV9tb2RlbF9pZGVudGl0eSIKICAgIF0KICB9LAogICJjcmFzaF9tZXRhZGF0YSI6IHsKICAgICJjaGVja3BvaW50X2lkIjogImNoZWNrcG9pbnQtc3RlcC0wMDAwMDQiLAogICAgImNoZWNrcG9pbnRfc3RlcCI6IDQsCiAgICAibGFzdF9jb21wbGV0ZWRfc3RlcCI6IDQsCiAgICAicmVjb3Zlcnlfd29ya2VyX3BpZCI6IDE2NjAwLAogICAgInRlcm1pbmF0aW9uX2V4aXRfY29kZSI6IDEsCiAgICAidGVybWluYXRpb25fbWV0aG9kIjogIlRlcm1pbmF0ZVByb2Nlc3MgdmlhIHN1YnByb2Nlc3MuUG9wZW4ua2lsbCIsCiAgICAid29ya2VyX3BpZCI6IDMxNDEyCiAgfSwKICAiZXZpZGVuY2VfY2F0YWxvZyI6IHsKICAgICJiYXNlOnByZXNlbmNlIjogIkJhc2UgYXJ0aWZhY3QgcHJlc2VudCB3aGVuIHJlcXVpcmVkIiwKICAgICJiYXNlOnNoYTI1NiI6ICJCYXNlIGFydGlmYWN0IGhhc2ggbWF0Y2hlcyIsCiAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIjogIk5vIG1hbmRhdG9yeSBjb250cmFjdCByZXF1aXJlbWVudCB3YXMgc2lsZW50bHkgb21pdHRlZCIsCiAgICAiaW50ZWdyaXR5OmNvbXBsZXRpb24tbWFya2VyIjogIkNvbXBsZXRpb24gbWFya2VyIHByZXNlbnQiLAogICAgImludGVncml0eTpzaGEyNTYiOiAiQWxsIHBheWxvYWQgY2hlY2tzdW1zIHZhbGlkIiwKICAgICJtYW5pZmVzdDpnbG9iYWwtc3RlcCI6ICJDaGVja3BvaW50IGdsb2JhbCBzdGVwIGlzIHZhbGlkIiwKICAgICJtYW5pZmVzdDpzY2hlbWEiOiAiTWFuaWZlc3Qgc2NoZW1hIHZhbGlkIiwKICAgICJwcm9jZXNzOm5leHQtc3RlcCI6ICJSZXN1bWVkIHJ1biBjb250aW51ZXMgZnJvbSB0aGUgZXhwZWN0ZWQgbmV4dCBzdGVwIiwKICAgICJwcm9jZXNzOm9yaWdpbmFsLXBpZCI6ICJPcmlnaW5hbCB3b3JrZXIgUElEIGlzIHJlY29yZGVkIiwKICAgICJwcm9jZXNzOnJlY292ZXJ5LWV4aXQiOiAiUmVjb3Zlcnkgd29ya2VyIGV4aXRzIHN1Y2Nlc3NmdWxseSIsCiAgICAicHJvY2VzczpyZWNvdmVyeS1waWQiOiAiUmVjb3ZlcnkgdXNlcyBhIGRpZmZlcmVudCBQSUQiLAogICAgInByb2Nlc3M6dGVybWluYXRpb24iOiAiT3JpZ2luYWwgd29ya2VyIHRlcm1pbmF0aW9uIGlzIHZlcmlmaWVkIiwKICAgICJyZXN0b3JlOm1vZGVsLXN0YXRlIjogIk1vZGVsIG9yIGFkYXB0ZXIgc3RhdGUgcmVzdG9yZXMiLAogICAgInJlc3RvcmU6bnVtcHktcm5nIjogIk51bVB5IFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICJyZXN0b3JlOm9wdGltaXplci1zdGF0ZSI6ICJPcHRpbWl6ZXIgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAicmVzdG9yZTpweXRob24tcm5nIjogIlB5dGhvbiBSTkcgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAicmVzdG9yZTpzY2hlZHVsZXItc3RhdGUiOiAiU2NoZWR1bGVyIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgInJlc3RvcmU6dG9yY2gtcm5nIjogIlRvcmNoIFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICJyb2xsYmFjazphY2hpZXZlZCI6ICJBY2hpZXZlZCByb2xsYmFjayBpcyB3aXRoaW4gdGhlIGhhcmQgbGltaXQiLAogICAgInNhZmV0eTpwYXRoLWNvbnRhaW5tZW50IjogIkFsbCBtYW5hZ2VkIHdyaXRlIHBhdGhzIHBhc3NlZCBjb250YWlubWVudCIsCiAgICAidHJhamVjdG9yeTpjaGVja3BvaW50LWV2YWx1YXRpb24iOiAiRml4ZWQgZXZhbHVhdGlvbiBhZnRlciByZXN0b3JlIG1hdGNoZXMiLAogICAgInRyYWplY3Rvcnk6ZmluYWwtZXZhbHVhdGlvbiI6ICJGaW5hbCBldmFsdWF0aW9uIGxvZ2l0cyBtYXRjaCBjb250cm9sIiwKICAgICJ0cmFqZWN0b3J5OmZpbmFsLXRyYWluYWJsZSI6ICJGaW5hbCB0cmFpbmFibGUgcGFyYW1ldGVycyBtYXRjaCBjb250cm9sIiwKICAgICJ0cmFqZWN0b3J5Omxvc3MtaGlzdG9yeSI6ICJDb250aW51ZWQgbG9zcyB0cmFqZWN0b3J5IG1hdGNoZXMgY29udHJvbCIKICB9LAogICJnYXRlX2NoZWNrcyI6IFsKICAgIHsKICAgICAgImFjdHVhbCI6ICJjaGVja3BvaW50LW1hbmlmZXN0LXYxIiwKICAgICAgImNhdGVnb3J5IjogIkludGVncml0eSIsCiAgICAgICJjaGVja19pZCI6ICJpbnRlZ3JpdHkubWFuaWZlc3Rfc2NoZW1hIiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJtYW5pZmVzdDpzY2hlbWEiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJjaGVja3BvaW50LW1hbmlmZXN0LXYxIiwKICAgICAgImxhYmVsIjogIk1hbmlmZXN0IHNjaGVtYSB2YWxpZCIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAicHJlc2VudCIsCiAgICAgICJjYXRlZ29yeSI6ICJJbnRlZ3JpdHkiLAogICAgICAiY2hlY2tfaWQiOiAiaW50ZWdyaXR5LmNvbXBsZXRpb25fbWFya2VyIiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJpbnRlZ3JpdHk6Y29tcGxldGlvbi1tYXJrZXIiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJDT01QTEVURSBwcmVzZW50IGluIGZpbmFsIGNoZWNrcG9pbnQiLAogICAgICAibGFiZWwiOiAiQ29tcGxldGlvbiBtYXJrZXIgcHJlc2VudCIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAiMiBwYXlsb2FkcyB2YWxpZGF0ZWQiLAogICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgImNoZWNrX2lkIjogImludGVncml0eS5jaGVja3N1bXMiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgImludGVncml0eTpzaGEyNTYiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJldmVyeSBtYW5pZmVzdCBwYXlsb2FkIG1hdGNoZXMgU0hBLTI1NiBhbmQgc2l6ZSIsCiAgICAgICJsYWJlbCI6ICJBbGwgcGF5bG9hZCBjaGVja3N1bXMgdmFsaWQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInByZXNlbnQiLAogICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgImNoZWNrX2lkIjogImludGVncml0eS5iYXNlX3ByZXNlbnQiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgImJhc2U6cHJlc2VuY2UiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJjb250YWluZWQgaW1tdXRhYmxlIGJhc2UgYXJ0aWZhY3QiLAogICAgICAibGFiZWwiOiAiQmFzZSBhcnRpZmFjdCBwcmVzZW50IHdoZW4gcmVxdWlyZWQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogImMxN2NjODk5NGM4ZjBmZTZkZWYzMjQyM2IwZTVkOWVmZWRmZmIzY2Q3MWM3ZGU5NjMxZjI2Y2Y1MDU5MjVkODYiLAogICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgImNoZWNrX2lkIjogImludGVncml0eS5iYXNlX2hhc2giLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgImJhc2U6c2hhMjU2IgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAiYzE3Y2M4OTk0YzhmMGZlNmRlZjMyNDIzYjBlNWQ5ZWZlZGZmYjNjZDcxYzdkZTk2MzFmMjZjZjUwNTkyNWQ4NiIsCiAgICAgICJsYWJlbCI6ICJCYXNlIGFydGlmYWN0IGhhc2ggbWF0Y2hlcyIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAibWFuaWZlc3Q9NCwgZXZlbnQ9NCwgcmVzdG9yZWQ9NCIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5nbG9iYWxfc3RlcCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAibWFuaWZlc3Q6Z2xvYmFsLXN0ZXAiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICIwIDwgc3RlcCA8IDgsIGNvbnNpc3RlbnQgYWNyb3NzIHJlc3RvcmUiLAogICAgICAibGFiZWwiOiAiQ2hlY2twb2ludCBnbG9iYWwgc3RlcCBpcyB2YWxpZCIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAic2VyaWFsaXplZD1UcnVlLCBkaWdlc3RfbWF0Y2g9VHJ1ZSIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5tb2RlbF9vcl9hZGFwdGVyIiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJyZXN0b3JlOm1vZGVsLXN0YXRlIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBhZGFwdGVyIGFuZCBleGFjdCB0cmFpbmFibGUtc3RhdGUgZGlnZXN0IiwKICAgICAgImxhYmVsIjogIk1vZGVsIG9yIGFkYXB0ZXIgc3RhdGUgcmVzdG9yZXMiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1GYWxzZSIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5vcHRpbWl6ZXIiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJlc3RvcmU6b3B0aW1pemVyLXN0YXRlIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBvcHRpbWl6ZXIgd2l0aCBleGFjdCBkaWdlc3QiLAogICAgICAibGFiZWwiOiAiT3B0aW1pemVyIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1GYWxzZSIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5zY2hlZHVsZXIiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJlc3RvcmU6c2NoZWR1bGVyLXN0YXRlIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBzY2hlZHVsZXIgd2l0aCBleGFjdCBkaWdlc3QiLAogICAgICAibGFiZWwiOiAiU2NoZWR1bGVyIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1UcnVlIiwKICAgICAgImNhdGVnb3J5IjogIlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlIiwKICAgICAgImNoZWNrX2lkIjogInN0YXRlLnB5dGhvbl9ybmciLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJlc3RvcmU6cHl0aG9uLXJuZyIKICAgICAgXSwKICAgICAgImV4cGVjdGVkIjogInNlcmlhbGl6ZWQgc3RhdGUgd2l0aCBleGFjdCBkaWdlc3QiLAogICAgICAibGFiZWwiOiAiUHl0aG9uIFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICAgInN0YXR1cyI6ICJmYWlsIgogICAgfSwKICAgIHsKICAgICAgImFjdHVhbCI6ICJzZXJpYWxpemVkPUZhbHNlLCBkaWdlc3RfbWF0Y2g9VHJ1ZSIsCiAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5udW1weV9ybmciLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJlc3RvcmU6bnVtcHktcm5nIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBzdGF0ZSB3aXRoIGV4YWN0IGRpZ2VzdCIsCiAgICAgICJsYWJlbCI6ICJOdW1QeSBSTkcgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAgICJzdGF0dXMiOiAiZmFpbCIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAic2VyaWFsaXplZD1GYWxzZSwgZGlnZXN0X21hdGNoPUZhbHNlIiwKICAgICAgImNhdGVnb3J5IjogIlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlIiwKICAgICAgImNoZWNrX2lkIjogInN0YXRlLnRvcmNoX3JuZyIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicmVzdG9yZTp0b3JjaC1ybmciCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJzZXJpYWxpemVkIHN0YXRlIHdpdGggZXhhY3QgZGlnZXN0IiwKICAgICAgImxhYmVsIjogIlRvcmNoIFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICAgInN0YXR1cyI6ICJmYWlsIgogICAgfSwKICAgIHsKICAgICAgImFjdHVhbCI6ICJmaXJzdCBiYXRjaCBhdCA0LCBmaXJzdCBjb21wbGV0aW9uIGF0IDUiLAogICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLm5leHRfc3RlcCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicHJvY2VzczpuZXh0LXN0ZXAiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJmaXJzdCBiYXRjaCBhdCA0LCBmaXJzdCBjb21wbGV0aW9uIGF0IDUiLAogICAgICAibGFiZWwiOiAiUmVzdW1lZCBydW4gY29udGludWVzIGZyb20gdGhlIGV4cGVjdGVkIG5leHQgc3RlcCIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAiMzE0MTIiLAogICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLm9yaWdpbmFsX3BpZCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicHJvY2VzczpvcmlnaW5hbC1waWQiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICIzMTQxMiIsCiAgICAgICJsYWJlbCI6ICJPcmlnaW5hbCB3b3JrZXIgUElEIGlzIHJlY29yZGVkIiwKICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgfSwKICAgIHsKICAgICAgImFjdHVhbCI6ICJtZXRob2Q9VGVybWluYXRlUHJvY2VzcyB2aWEgc3VicHJvY2Vzcy5Qb3Blbi5raWxsLCBleGl0PTEsIHZlcmlmaWVkPVRydWUiLAogICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLmV4cGVjdGVkX3Rlcm1pbmF0aW9uIiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJwcm9jZXNzOnRlcm1pbmF0aW9uIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAicGFyZW50IHRlcm1pbmF0aW9uIHdpdGggbm9uemVybyBleGl0IGNvZGUiLAogICAgICAibGFiZWwiOiAiT3JpZ2luYWwgd29ya2VyIHRlcm1pbmF0aW9uIGlzIHZlcmlmaWVkIiwKICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgfSwKICAgIHsKICAgICAgImFjdHVhbCI6ICIxNjYwMCIsCiAgICAgICJjYXRlZ29yeSI6ICJQcm9jZXNzIHJlY292ZXJ5IiwKICAgICAgImNoZWNrX2lkIjogInByb2Nlc3MubmV3X3JlY292ZXJ5X3BpZCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicHJvY2VzczpyZWNvdmVyeS1waWQiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJQSUQgZGlmZmVyZW50IGZyb20gMzE0MTIiLAogICAgICAibGFiZWwiOiAiUmVjb3ZlcnkgdXNlcyBhIGRpZmZlcmVudCBQSUQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogImV4aXQ9MCwgdmVyaWZpZWQ9VHJ1ZSIsCiAgICAgICJjYXRlZ29yeSI6ICJQcm9jZXNzIHJlY292ZXJ5IiwKICAgICAgImNoZWNrX2lkIjogInByb2Nlc3MucmVjb3ZlcnlfZXhpdCIsCiAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAicHJvY2VzczpyZWNvdmVyeS1leGl0IgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAiZXhpdCBjb2RlIDAiLAogICAgICAibGFiZWwiOiAiUmVjb3Zlcnkgd29ya2VyIGV4aXRzIHN1Y2Nlc3NmdWxseSIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAiMCBzdGVwcyIsCiAgICAgICJjYXRlZ29yeSI6ICJTYWZldHkgYW5kIHJvbGxiYWNrIiwKICAgICAgImNoZWNrX2lkIjogInJvbGxiYWNrLmhhcmRfbGltaXQiLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInJvbGxiYWNrOmFjaGlldmVkIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAiPD0gMCBzdGVwcyIsCiAgICAgICJsYWJlbCI6ICJBY2hpZXZlZCByb2xsYmFjayBpcyB3aXRoaW4gdGhlIGhhcmQgbGltaXQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogImQ2MDU3MmFlYTEyZjkxOTYwZjNmMDAzMGJkZmRjYTU1ZmRhZmUwNTkxNDZjNzIzMGFmOTA5NDkyMzgxMWQzMTIiLAogICAgICAiY2F0ZWdvcnkiOiAiVHJhamVjdG9yeSBjb3JyZWN0bmVzcyIsCiAgICAgICJjaGVja19pZCI6ICJ0cmFqZWN0b3J5LmNoZWNrcG9pbnRfZXZhbHVhdGlvbiIsCiAgICAgICJkZXRhaWxzIjogIkV4YWN0IFNIQS0yNTYgY29tcGFyaXNvbjsgbm8gbnVtZXJpY2FsIHRvbGVyYW5jZSBpcyBhcHBsaWVkLiIsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgInRyYWplY3Rvcnk6Y2hlY2twb2ludC1ldmFsdWF0aW9uIgogICAgICBdLAogICAgICAiZXhwZWN0ZWQiOiAiZDYwNTcyYWVhMTJmOTE5NjBmM2YwMDMwYmRmZGNhNTVmZGFmZTA1OTE0NmM3MjMwYWY5MDk0OTIzODExZDMxMiIsCiAgICAgICJsYWJlbCI6ICJGaXhlZCBldmFsdWF0aW9uIGFmdGVyIHJlc3RvcmUgbWF0Y2hlcyIsCiAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgIH0sCiAgICB7CiAgICAgICJhY3R1YWwiOiAiZDI4NTQ3ZTgyZGM0MTJkNTgwNjBlOGJlNjRkZWI1MjE5MWI3YjI1ODU2MWJlNDc4NzQ2OTRiMWM1NDZlY2E2NiIsCiAgICAgICJjYXRlZ29yeSI6ICJUcmFqZWN0b3J5IGNvcnJlY3RuZXNzIiwKICAgICAgImNoZWNrX2lkIjogInRyYWplY3RvcnkuZmluYWxfdHJhaW5hYmxlIiwKICAgICAgImRldGFpbHMiOiAiRXhhY3QgU0hBLTI1NiBjb21wYXJpc29uOyBubyBudW1lcmljYWwgdG9sZXJhbmNlIGlzIGFwcGxpZWQuIiwKICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAidHJhamVjdG9yeTpmaW5hbC10cmFpbmFibGUiCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICIxZmM3MmZkZjIxNDg3YWZlN2IzMmRhODMzZDIzMDBjZDlhNjhmMGMwYzZmM2NlMTQ1NjkxMGE1MTAyYTkyOTk3IiwKICAgICAgImxhYmVsIjogIkZpbmFsIHRyYWluYWJsZSBwYXJhbWV0ZXJzIG1hdGNoIGNvbnRyb2wiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogIjQzNDZhMmQ3N2IzNzA3NmI4NTNkNDUyOTk4MTgyNGVkZDU0OTUzOGY5MzhkNDk2NDIyMDg5OTE0OWRkNWI0Y2QiLAogICAgICAiY2F0ZWdvcnkiOiAiVHJhamVjdG9yeSBjb3JyZWN0bmVzcyIsCiAgICAgICJjaGVja19pZCI6ICJ0cmFqZWN0b3J5LmZpbmFsX2V2YWx1YXRpb24iLAogICAgICAiZGV0YWlscyI6ICJFeGFjdCBTSEEtMjU2IGNvbXBhcmlzb247IG5vIG51bWVyaWNhbCB0b2xlcmFuY2UgaXMgYXBwbGllZC4iLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJ0cmFqZWN0b3J5OmZpbmFsLWV2YWx1YXRpb24iCiAgICAgIF0sCiAgICAgICJleHBlY3RlZCI6ICJhNDJhNmQyNWM4YWFmNjY3NDEzMGVmNjM0MzlmNmZkNDE1ODI0YmQyM2ZmOWNkNmE3YzBjYTAzMDViZTNlZjlhIiwKICAgICAgImxhYmVsIjogIkZpbmFsIGV2YWx1YXRpb24gbG9naXRzIG1hdGNoIGNvbnRyb2wiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogInNlcXVlbmNlIGRpZmZlcnMiLAogICAgICAiY2F0ZWdvcnkiOiAiVHJhamVjdG9yeSBjb3JyZWN0bmVzcyIsCiAgICAgICJjaGVja19pZCI6ICJ0cmFqZWN0b3J5Lmxvc3NfaGlzdG9yeSIsCiAgICAgICJkZXRhaWxzIjogIkV4YWN0IGZsb2F0IHNlcXVlbmNlIGNvbXBhcmlzb247IG5vIG51bWVyaWNhbCB0b2xlcmFuY2UgaXMgYXBwbGllZC4iLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJ0cmFqZWN0b3J5Omxvc3MtaGlzdG9yeSIKICAgICAgXSwKICAgICAgImV4cGVjdGVkIjogImV4YWN0IGxvc3Mgc2VxdWVuY2UgZXF1YWxpdHkiLAogICAgICAibGFiZWwiOiAiQ29udGludWVkIGxvc3MgdHJhamVjdG9yeSBtYXRjaGVzIGNvbnRyb2wiLAogICAgICAic3RhdHVzIjogImZhaWwiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogImNvbnRhaW5lZCIsCiAgICAgICJjYXRlZ29yeSI6ICJTYWZldHkgYW5kIHJvbGxiYWNrIiwKICAgICAgImNoZWNrX2lkIjogInNhZmV0eS5wYXRoX2NvbnRhaW5tZW50IiwKICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICJzYWZldHk6cGF0aC1jb250YWlubWVudCIKICAgICAgXSwKICAgICAgImV4cGVjdGVkIjogImFsbCBwYXRocyBjb250YWluZWQ7IHN5bWxpbmsgZXNjYXBlcyByZWplY3RlZCIsCiAgICAgICJsYWJlbCI6ICJBbGwgbWFuYWdlZCB3cml0ZSBwYXRocyBwYXNzZWQgY29udGFpbm1lbnQiLAogICAgICAic3RhdHVzIjogInBhc3MiCiAgICB9LAogICAgewogICAgICAiYWN0dWFsIjogIm1hbmlmZXN0IGxhY2tzOiBudW1weV9ybmcsIG9wdGltaXplciwgcHl0aG9uX3JuZywgc2NoZWR1bGVyLCB0b3JjaF9ybmciLAogICAgICAiY2F0ZWdvcnkiOiAiU2FmZXR5IGFuZCByb2xsYmFjayIsCiAgICAgICJjaGVja19pZCI6ICJjb250cmFjdC5ub19tYW5kYXRvcnlfb21pc3Npb24iLAogICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgImNvbnRyYWN0Om1hbmRhdG9yeS1zdGF0ZSIKICAgICAgXSwKICAgICAgImV4cGVjdGVkIjogImFsbCBtYW5kYXRvcnkgY29udGludWF0aW9uIHN0YXRlIGRlY2xhcmVkIiwKICAgICAgImxhYmVsIjogIk5vIG1hbmRhdG9yeSBjb250cmFjdCByZXF1aXJlbWVudCB3YXMgc2lsZW50bHkgb21pdHRlZCIsCiAgICAgICJzdGF0dXMiOiAiZmFpbCIKICAgIH0KICBdLAogICJpbnRlZ3JpdHlfc3VtbWFyeSI6IHsKICAgICJjaGVja3BvaW50X2xvYWRfc3VjY2VlZGVkIjogdHJ1ZSwKICAgICJjaGVja3N1bXNfdmFsaWQiOiB0cnVlLAogICAgImNvbXBsZXRpb25fbWFya2VyX3ByZXNlbnQiOiB0cnVlLAogICAgIm1hbmlmZXN0X3ZhbGlkIjogdHJ1ZQogIH0sCiAgIm1hbmlmZXN0X3N1bW1hcnkiOiB7CiAgICAiZ2xvYmFsX3N0ZXAiOiA0LAogICAgImhhc19iYXNlX3JlZmVyZW5jZSI6IHRydWUsCiAgICAicGF5bG9hZF9yb2xlcyI6IFsKICAgICAgImFkYXB0ZXIiLAogICAgICAic3RhdGUiCiAgICBdLAogICAgInByb2ZpbGUiOiAiY2kiLAogICAgInNjaGVtYV92ZXJzaW9uIjogImNoZWNrcG9pbnQtbWFuaWZlc3QtdjEiLAogICAgInNlcmlhbGl6ZWRfc3RhdGUiOiBbCiAgICAgICJhZGFwdGVyIiwKICAgICAgImdsb2JhbF9zdGVwIiwKICAgICAgImNvbmZpZyIsCiAgICAgICJiYXNlX21vZGVsX2lkZW50aXR5IgogICAgXQogIH0sCiAgInJlc3RvcmVfb3JkZXIiOiBbCiAgICAidmFsaWRhdGUgY2hlY2twb2ludCBtZXRhZGF0YSBhbmQgcGF5bG9hZCBjaGVja3N1bXMiLAogICAgInZhbGlkYXRlIGltbXV0YWJsZSBiYXNlIGlkZW50aXR5IHdoZW4gcmVmZXJlbmNlZCIsCiAgICAibG9hZCBkZWNsYXJlZCBtb2RlbCBzdGF0ZSIsCiAgICAicmVzdW1lIGZyb20gdGhlIHJlc3RvcmVkIGdsb2JhbCBzdGVwIgogIF0sCiAgInNhdmVfcmVzdG9yZV9zdW1tYXJ5IjogewogICAgImludGVncml0eV9jb250cm9scyI6IFsKICAgICAgIm1hbmlmZXN0IiwKICAgICAgIlNIQS0yNTYgY2hlY2tzdW1zIiwKICAgICAgImNvbXBsZXRpb24gbWFya2VyIiwKICAgICAgImF0b21pYyBkaXJlY3RvcnkgY29tbWl0IiwKICAgICAgImJhc2UgYXJ0aWZhY3QgU0hBLTI1NiIKICAgIF0sCiAgICAicmVzdG9yZWRfZ2xvYmFsX3N0ZXAiOiA0LAogICAgInNlcmlhbGl6ZWRfc3RhdGUiOiBbCiAgICAgICJhZGFwdGVyIiwKICAgICAgImdsb2JhbF9zdGVwIiwKICAgICAgImNvbmZpZyIsCiAgICAgICJiYXNlX21vZGVsX2lkZW50aXR5IgogICAgXQogIH0sCiAgInNjaGVtYV92ZXJzaW9uIjogInNhbml0aXplZC1mYWlsdXJlLXYxIiwKICAic3RhdGVfZGlmZmVyZW5jZXMiOiB7CiAgICAiY2hlY2twb2ludF90cmFpbmFibGVfbWF0Y2giOiB0cnVlLAogICAgIm51bXB5X3JuZ19tYXRjaCI6IHRydWUsCiAgICAib3B0aW1pemVyX21hdGNoIjogZmFsc2UsCiAgICAicHl0aG9uX3JuZ19tYXRjaCI6IHRydWUsCiAgICAic2NoZWR1bGVyX21hdGNoIjogZmFsc2UsCiAgICAidG9yY2hfcm5nX21hdGNoIjogZmFsc2UKICB9LAogICJ0cmFqZWN0b3J5X3N1bW1hcnkiOiB7CiAgICAiY2hlY2twb2ludF9zdGVwIjogNCwKICAgICJmaW5hbF9ldmFsdWF0aW9uX21hdGNoIjogZmFsc2UsCiAgICAiZmluYWxfc3RlcCI6IDgsCiAgICAiZmluYWxfdHJhaW5hYmxlX21hdGNoIjogZmFsc2UsCiAgICAibG9zc19oaXN0b3J5X21hdGNoIjogZmFsc2UKICB9LAogICJ1c2VyX29iamVjdGl2ZSI6IHsKICAgICJoYXJkX3JvbGxiYWNrX2xpbWl0X3N0ZXBzIjogMCwKICAgICJyZWNvdmVyeV9jb3JyZWN0bmVzcyI6ICJzdHJpY3QiCiAgfSwKICAid29ya2xvYWRfY2FwYWJpbGl0aWVzIjogewogICAgImFkYXB0ZXJfbmFtZSI6ICJuYXRpdmUtcHl0b3JjaCIsCiAgICAiYXNzdW1wdGlvbnMiOiBbCiAgICAgICJDUFUtb25seSBjb250cm9sbGVkIHdvcmtsb2FkIiwKICAgICAgIk9ubHkgcmVzaWR1YWwtYWRhcHRlciBwYXJhbWV0ZXJzIGFyZSB0cmFpbmFibGUiCiAgICBdLAogICAgImJhdGNoX3Bvc2l0aW9uX2lzX3N0ZXBfZGVyaXZlZCI6IHRydWUsCiAgICAiZnJhbWV3b3JrIjogIm5hdGl2ZS1weXRvcmNoIiwKICAgICJoYXNfZnJvemVuX2Jhc2UiOiB0cnVlLAogICAgImhhc190cmFpbmFibGVfYWRhcHRlciI6IHRydWUsCiAgICAib3B0aW1pemVyX3R5cGUiOiAiQWRhbVciLAogICAgInNjaGVkdWxlcl90eXBlIjogIkxpbmVhckxSIiwKICAgICJzdXBwb3J0ZWRfcmVwYWlyX2FjdGlvbnMiOiBbCiAgICAgICJwZXJzaXN0X29wdGltaXplcl9zdGF0ZSIsCiAgICAgICJwZXJzaXN0X3NjaGVkdWxlcl9zdGF0ZSIsCiAgICAgICJwZXJzaXN0X3B5dGhvbl9ybmdfc3RhdGUiLAogICAgICAicGVyc2lzdF9udW1weV9ybmdfc3RhdGUiLAogICAgICAicGVyc2lzdF90b3JjaF9ybmdfc3RhdGUiLAogICAgICAicmVzdG9yZV9zdGF0ZV9iZWZvcmVfbmV4dF9iYXRjaCIKICAgIF0sCiAgICAic3VwcG9ydGVkX3N0YXRlIjogWwogICAgICAibW9kZWwiLAogICAgICAiYWRhcHRlciIsCiAgICAgICJvcHRpbWl6ZXIiLAogICAgICAic2NoZWR1bGVyIiwKICAgICAgImdsb2JhbF9zdGVwIiwKICAgICAgInB5dGhvbl9ybmciLAogICAgICAibnVtcHlfcm5nIiwKICAgICAgInRvcmNoX3JuZyIsCiAgICAgICJiYXNlX21vZGVsX2lkZW50aXR5IgogICAgXSwKICAgICJ1c2VzX2N1ZGFfcm5nIjogZmFsc2UsCiAgICAidXNlc19kcm9wb3V0IjogdHJ1ZSwKICAgICJ1c2VzX251bXB5X3JuZyI6IHRydWUsCiAgICAidXNlc19weXRob25fcm5nIjogdHJ1ZSwKICAgICJ1c2VzX3RvcmNoX3JuZyI6IHRydWUKICB9Cn0K",
   "initial/artifacts/frozen-base/COMPLETE": "bmF0aXZlLXB5dG9yY2g6Y2k6YzE3Y2M4OTk0YzhmMGZlNmRlZjMyNDIzYjBlNWQ5ZWZlZGZmYjNjZDcxYzdkZTk2MzFmMjZjZjUwNTkyNWQ4Ngo=",
   "initial/artifacts/frozen-base/base.json": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJiYXNlLWFydGlmYWN0LXYxIiwKICAiYWRhcHRlcl9uYW1lIjogIm5hdGl2ZS1weXRvcmNoIiwKICAicHJvZmlsZSI6ICJjaSIsCiAgImFydGlmYWN0IjogewogICAgImlkZW50aXR5IjogIm5hdGl2ZS1weXRvcmNoOmNpOmMxN2NjODk5NGM4ZjBmZTZkZWYzMjQyM2IwZTVkOWVmZWRmZmIzY2Q3MWM3ZGU5NjMxZjI2Y2Y1MDU5MjVkODYiLAogICAgInBhdGgiOiAiYXJ0aWZhY3RzL2Zyb3plbi1iYXNlL2Jhc2UucHQiLAogICAgInNoYTI1NiI6ICJjMTdjYzg5OTRjOGYwZmU2ZGVmMzI0MjNiMGU1ZDllZmVkZmZiM2NkNzFjN2RlOTYzMWYyNmNmNTA1OTI1ZDg2IiwKICAgICJzaXplX2J5dGVzIjogMTg0NzUKICB9Cn0K",
   "initial/artifacts/frozen-base/base.pt": "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",
   "initial/checkpoints/missing-training-state/checkpoint-step-000004/COMPLETE": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJjb21wbGV0aW9uLW1hcmtlci12MSIsCiAgImNoZWNrcG9pbnRfaWQiOiAiY2hlY2twb2ludC1zdGVwLTAwMDAwNCIKfQo=",
   "initial/checkpoints/missing-training-state/checkpoint-step-000004/adapter.pt": "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",
   "initial/checkpoints/missing-training-state/checkpoint-step-000004/checksums.json": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJjaGVja3N1bXMtdjEiLAogICJmaWxlcyI6IFsKICAgIHsKICAgICAgInBhdGgiOiAiYWRhcHRlci5wdCIsCiAgICAgICJzaGEyNTYiOiAiY2M2NjgxYjIxNWU4MTA2YzM4MDFiNTk1ODJlNTdlMmE2YzczZDk2YTU0Yjk3ZTM5OGVjZThhYTE4Njg1OWJmMSIsCiAgICAgICJzaXplX2J5dGVzIjogMjc4MQogICAgfSwKICAgIHsKICAgICAgInBhdGgiOiAic3RhdGUuanNvbiIsCiAgICAgICJzaGEyNTYiOiAiNzZlNTI3ZTcwZDQyYmU3N2QwNzU5YjFjNjIyOWM1NmJhYWIzN2I3NTdhM2ZkMDk1NDAyNWJiNzE3OTI3YzBmMyIsCiAgICAgICJzaXplX2J5dGVzIjogODYxCiAgICB9CiAgXQp9Cg==",
   "initial/checkpoints/missing-training-state/checkpoint-step-000004/manifest.json": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJjaGVja3BvaW50LW1hbmlmZXN0LXYxIiwKICAiY2hlY2twb2ludF9pZCI6ICJjaGVja3BvaW50LXN0ZXAtMDAwMDA0IiwKICAic3RyYXRlZ3kiOiAibWlzc2luZ190cmFpbmluZ19zdGF0ZSIsCiAgInByb2ZpbGUiOiAiY2kiLAogICJnbG9iYWxfc3RlcCI6IDQsCiAgImNyZWF0ZWRfYXQiOiAiMjAyNi0wNy0yMFQwMToyODo1OC45ODc0OTZaIiwKICAic2VyaWFsaXplZF9zdGF0ZSI6IFsKICAgICJhZGFwdGVyIiwKICAgICJnbG9iYWxfc3RlcCIsCiAgICAiY29uZmlnIiwKICAgICJiYXNlX21vZGVsX2lkZW50aXR5IgogIF0sCiAgIm9taXR0ZWRfc3RhdGUiOiBbCiAgICAib3B0aW1pemVyIiwKICAgICJzY2hlZHVsZXIiLAogICAgInB5dGhvbl9ybmciLAogICAgIm51bXB5X3JuZyIsCiAgICAidG9yY2hfcm5nIgogIF0sCiAgImJhc2VfYXJ0aWZhY3QiOiB7CiAgICAiaWRlbnRpdHkiOiAibmF0aXZlLXB5dG9yY2g6Y2k6YzE3Y2M4OTk0YzhmMGZlNmRlZjMyNDIzYjBlNWQ5ZWZlZGZmYjNjZDcxYzdkZTk2MzFmMjZjZjUwNTkyNWQ4NiIsCiAgICAicGF0aCI6ICJhcnRpZmFjdHMvZnJvemVuLWJhc2UvYmFzZS5wdCIsCiAgICAic2hhMjU2IjogImMxN2NjODk5NGM4ZjBmZTZkZWYzMjQyM2IwZTVkOWVmZWRmZmIzY2Q3MWM3ZGU5NjMxZjI2Y2Y1MDU5MjVkODYiLAogICAgInNpemVfYnl0ZXMiOiAxODQ3NQogIH0sCiAgInBheWxvYWRzIjogWwogICAgewogICAgICAicm9sZSI6ICJhZGFwdGVyIiwKICAgICAgInBhdGgiOiAiYWRhcHRlci5wdCIsCiAgICAgICJzaGEyNTYiOiAiY2M2NjgxYjIxNWU4MTA2YzM4MDFiNTk1ODJlNTdlMmE2YzczZDk2YTU0Yjk3ZTM5OGVjZThhYTE4Njg1OWJmMSIsCiAgICAgICJzaXplX2J5dGVzIjogMjc4MQogICAgfSwKICAgIHsKICAgICAgInJvbGUiOiAic3RhdGUiLAogICAgICAicGF0aCI6ICJzdGF0ZS5qc29uIiwKICAgICAgInNoYTI1NiI6ICI3NmU1MjdlNzBkNDJiZTc3ZDA3NTliMWM2MjI5YzU2YmFhYjM3Yjc1N2EzZmQwOTU0MDI1YmI3MTc5MjdjMGYzIiwKICAgICAgInNpemVfYnl0ZXMiOiA4NjEKICAgIH0KICBdCn0K",
   "initial/checkpoints/missing-training-state/checkpoint-step-000004/state.json": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJhZGFwdGVyLWNoZWNrcG9pbnQtc3RhdGUtdjEiLAogICJjaGVja3BvaW50X2lkIjogImNoZWNrcG9pbnQtc3RlcC0wMDAwMDQiLAogICJzdHJhdGVneSI6ICJtaXNzaW5nX3RyYWluaW5nX3N0YXRlIiwKICAiZ2xvYmFsX3N0ZXAiOiA0LAogICJwcm9maWxlIjogewogICAgIm5hbWUiOiAiY2kiLAogICAgImdsb2JhbF9zZWVkIjogMjAyNjA3MTYsCiAgICAic3RlcHMiOiA4LAogICAgImJhdGNoX3NpemUiOiA0LAogICAgInNlcXVlbmNlX2xlbmd0aCI6IDgsCiAgICAidm9jYWJ1bGFyeV9zaXplIjogMzIsCiAgICAibW9kZWxfd2lkdGgiOiAxNiwKICAgICJhdHRlbnRpb25faGVhZHMiOiAyLAogICAgInRyYW5zZm9ybWVyX2xheWVycyI6IDEsCiAgICAiYWRhcHRlcl93aWR0aCI6IDQsCiAgICAiZHJvcG91dCI6IDAuMiwKICAgICJsZWFybmluZ19yYXRlIjogMC4wMQogIH0sCiAgImxvc3NfaGlzdG9yeSI6IFsKICAgIDMuNTM3MTk3NTg5ODc0MjY3NiwKICAgIDMuNDM0NDU3NTQwNTEyMDg1LAogICAgMy41OTc3MDY1NTYzMjAxOTA0LAogICAgMy41NjA3NDY2Njk3NjkyODcKICBdLAogICJiYXNlX2FydGlmYWN0IjogewogICAgImlkZW50aXR5IjogIm5hdGl2ZS1weXRvcmNoOmNpOmMxN2NjODk5NGM4ZjBmZTZkZWYzMjQyM2IwZTVkOWVmZWRmZmIzY2Q3MWM3ZGU5NjMxZjI2Y2Y1MDU5MjVkODYiLAogICAgInBhdGgiOiAiYXJ0aWZhY3RzL2Zyb3plbi1iYXNlL2Jhc2UucHQiLAogICAgInNoYTI1NiI6ICJjMTdjYzg5OTRjOGYwZmU2ZGVmMzI0MjNiMGU1ZDllZmVkZmZiM2NkNzFjN2RlOTYzMWYyNmNmNTA1OTI1ZDg2IiwKICAgICJzaXplX2J5dGVzIjogMTg0NzUKICB9Cn0K",
   "initial/logs/checkpoint-worker.stderr.log": "",
   "initial/logs/recovery-worker.stderr.log": "",
   "initial/result.json": "ewogICJjb250cm9sIjogewogICAgImV2YWx1YXRpb25fc2hhMjU2IjogImE0MmE2ZDI1YzhhYWY2Njc0MTMwZWY2MzQzOWY2ZmQ0MTU4MjRiZDIzZmY5Y2Q2YTdjMGNhMDMwNWJlM2VmOWEiLAogICAgImdsb2JhbF9zdGVwIjogOCwKICAgICJsb3NzX2hpc3RvcnkiOiBbCiAgICAgIDMuNTM3MTk3NTg5ODc0MjY3NiwKICAgICAgMy40MzQ0NTc1NDA1MTIwODUsCiAgICAgIDMuNTk3NzA2NTU2MzIwMTkwNCwKICAgICAgMy41NjA3NDY2Njk3NjkyODcsCiAgICAgIDMuNjcwODIzNTc0MDY2MTYyLAogICAgICAzLjYyNzI1MzI5Mzk5MTA4OSwKICAgICAgMy41MDg2MzkzMzU2MzIzMjQsCiAgICAgIDMuODI0ODE0MzE5NjEwNTk1NwogICAgXSwKICAgICJvcHRpbWl6ZXJfc2hhMjU2IjogImMwM2RmYzhiNjZlNjY0NWZiNTUyMjIzNDI4YWQ4NmE4NTVjOTcwNDlkMTMzYjA4OTg0NjA0ZjZlN2Q1NWEwNTAiLAogICAgInNjaGVkdWxlcl9zaGEyNTYiOiAiZTA3ZmZkNmE4OWZlZmI2MWU4MGQxY2E1NjAyNWE5MjcyMjJhODMxODBmZmNlZDc3ODc4OTYwNmQzYTdiZWM4MSIsCiAgICAidHJhaW5hYmxlX3N0YXRlX3NoYTI1NiI6ICIxZmM3MmZkZjIxNDg3YWZlN2IzMmRhODMzZDIzMDBjZDlhNjhmMGMwYzZmM2NlMTQ1NjkxMGE1MTAyYTkyOTk3IgogIH0sCiAgImNyYXNoIjogewogICAgImNoZWNrcG9pbnRfcGF0aCI6ICJjaGVja3BvaW50cy9taXNzaW5nLXRyYWluaW5nLXN0YXRlL2NoZWNrcG9pbnQtc3RlcC0wMDAwMDQiLAogICAgImNoZWNrcG9pbnRfc3RlcCI6IDQsCiAgICAiZXZlbnRfcmVjZWl2ZWRfYXQiOiAiMjAyNi0wNy0yMFQwMToyODo1OS4xMzIwMzhaIiwKICAgICJsYXN0X2NvbXBsZXRlZF9zdGVwIjogNCwKICAgICJ0ZXJtaW5hdGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjg6NTkuMTc0MjAyWiIsCiAgICAidGVybWluYXRpb25fZXhpdF9jb2RlIjogMSwKICAgICJ0ZXJtaW5hdGlvbl9tZXRob2QiOiAiVGVybWluYXRlUHJvY2VzcyB2aWEgc3VicHJvY2Vzcy5Qb3Blbi5raWxsIiwKICAgICJ0ZXJtaW5hdGlvbl92ZXJpZmllZCI6IHRydWUsCiAgICAid29ya2VyX3BpZCI6IDMxNDEyCiAgfSwKICAiY3JlYXRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjA1LjExOTkyMVoiLAogICJmYWlsdXJlX2FydGlmYWN0X3BhdGgiOiAiYWdlbnQvcmVxdWVzdC5yZWRhY3RlZC5qc29uIiwKICAiZ2F0ZSI6IHsKICAgICJhY2hpZXZlZF9yb2xsYmFja19zdGVwcyI6IDAsCiAgICAiY2hlY2tzIjogWwogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICJjaGVja3BvaW50LW1hbmlmZXN0LXYxIiwKICAgICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgICAiY2hlY2tfaWQiOiAiaW50ZWdyaXR5Lm1hbmlmZXN0X3NjaGVtYSIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAibWFuaWZlc3Q6c2NoZW1hIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogImNoZWNrcG9pbnQtbWFuaWZlc3QtdjEiLAogICAgICAgICJsYWJlbCI6ICJNYW5pZmVzdCBzY2hlbWEgdmFsaWQiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAicHJlc2VudCIsCiAgICAgICAgImNhdGVnb3J5IjogIkludGVncml0eSIsCiAgICAgICAgImNoZWNrX2lkIjogImludGVncml0eS5jb21wbGV0aW9uX21hcmtlciIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAiaW50ZWdyaXR5OmNvbXBsZXRpb24tbWFya2VyIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogIkNPTVBMRVRFIHByZXNlbnQgaW4gZmluYWwgY2hlY2twb2ludCIsCiAgICAgICAgImxhYmVsIjogIkNvbXBsZXRpb24gbWFya2VyIHByZXNlbnQiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAiMiBwYXlsb2FkcyB2YWxpZGF0ZWQiLAogICAgICAgICJjYXRlZ29yeSI6ICJJbnRlZ3JpdHkiLAogICAgICAgICJjaGVja19pZCI6ICJpbnRlZ3JpdHkuY2hlY2tzdW1zIiwKICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJpbnRlZ3JpdHk6c2hhMjU2IgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogImV2ZXJ5IG1hbmlmZXN0IHBheWxvYWQgbWF0Y2hlcyBTSEEtMjU2IGFuZCBzaXplIiwKICAgICAgICAibGFiZWwiOiAiQWxsIHBheWxvYWQgY2hlY2tzdW1zIHZhbGlkIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogInByZXNlbnQiLAogICAgICAgICJjYXRlZ29yeSI6ICJJbnRlZ3JpdHkiLAogICAgICAgICJjaGVja19pZCI6ICJpbnRlZ3JpdHkuYmFzZV9wcmVzZW50IiwKICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJiYXNlOnByZXNlbmNlIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogImNvbnRhaW5lZCBpbW11dGFibGUgYmFzZSBhcnRpZmFjdCIsCiAgICAgICAgImxhYmVsIjogIkJhc2UgYXJ0aWZhY3QgcHJlc2VudCB3aGVuIHJlcXVpcmVkIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogImMxN2NjODk5NGM4ZjBmZTZkZWYzMjQyM2IwZTVkOWVmZWRmZmIzY2Q3MWM3ZGU5NjMxZjI2Y2Y1MDU5MjVkODYiLAogICAgICAgICJjYXRlZ29yeSI6ICJJbnRlZ3JpdHkiLAogICAgICAgICJjaGVja19pZCI6ICJpbnRlZ3JpdHkuYmFzZV9oYXNoIiwKICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJiYXNlOnNoYTI1NiIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJjMTdjYzg5OTRjOGYwZmU2ZGVmMzI0MjNiMGU1ZDllZmVkZmZiM2NkNzFjN2RlOTYzMWYyNmNmNTA1OTI1ZDg2IiwKICAgICAgICAibGFiZWwiOiAiQmFzZSBhcnRpZmFjdCBoYXNoIG1hdGNoZXMiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAibWFuaWZlc3Q9NCwgZXZlbnQ9NCwgcmVzdG9yZWQ9NCIsCiAgICAgICAgImNhdGVnb3J5IjogIlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlIiwKICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUuZ2xvYmFsX3N0ZXAiLAogICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgIm1hbmlmZXN0Omdsb2JhbC1zdGVwIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogIjAgPCBzdGVwIDwgOCwgY29uc2lzdGVudCBhY3Jvc3MgcmVzdG9yZSIsCiAgICAgICAgImxhYmVsIjogIkNoZWNrcG9pbnQgZ2xvYmFsIHN0ZXAgaXMgdmFsaWQiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAic2VyaWFsaXplZD1UcnVlLCBkaWdlc3RfbWF0Y2g9VHJ1ZSIsCiAgICAgICAgImNhdGVnb3J5IjogIlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlIiwKICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUubW9kZWxfb3JfYWRhcHRlciIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAicmVzdG9yZTptb2RlbC1zdGF0ZSIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJzZXJpYWxpemVkIGFkYXB0ZXIgYW5kIGV4YWN0IHRyYWluYWJsZS1zdGF0ZSBkaWdlc3QiLAogICAgICAgICJsYWJlbCI6ICJNb2RlbCBvciBhZGFwdGVyIHN0YXRlIHJlc3RvcmVzIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1GYWxzZSIsCiAgICAgICAgImNhdGVnb3J5IjogIlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlIiwKICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUub3B0aW1pemVyIiwKICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJyZXN0b3JlOm9wdGltaXplci1zdGF0ZSIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJzZXJpYWxpemVkIG9wdGltaXplciB3aXRoIGV4YWN0IGRpZ2VzdCIsCiAgICAgICAgImxhYmVsIjogIk9wdGltaXplciBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICAgICAic3RhdHVzIjogImZhaWwiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1GYWxzZSIsCiAgICAgICAgImNhdGVnb3J5IjogIlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlIiwKICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUuc2NoZWR1bGVyIiwKICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJyZXN0b3JlOnNjaGVkdWxlci1zdGF0ZSIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJzZXJpYWxpemVkIHNjaGVkdWxlciB3aXRoIGV4YWN0IGRpZ2VzdCIsCiAgICAgICAgImxhYmVsIjogIlNjaGVkdWxlciBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICAgICAic3RhdHVzIjogImZhaWwiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1UcnVlIiwKICAgICAgICAiY2F0ZWdvcnkiOiAiUmVxdWlyZWQgdHJhaW5pbmcgc3RhdGUiLAogICAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5weXRob25fcm5nIiwKICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJyZXN0b3JlOnB5dGhvbi1ybmciCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBzdGF0ZSB3aXRoIGV4YWN0IGRpZ2VzdCIsCiAgICAgICAgImxhYmVsIjogIlB5dGhvbiBSTkcgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAgICAgInN0YXR1cyI6ICJmYWlsIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICJzZXJpYWxpemVkPUZhbHNlLCBkaWdlc3RfbWF0Y2g9VHJ1ZSIsCiAgICAgICAgImNhdGVnb3J5IjogIlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlIiwKICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUubnVtcHlfcm5nIiwKICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJyZXN0b3JlOm51bXB5LXJuZyIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJzZXJpYWxpemVkIHN0YXRlIHdpdGggZXhhY3QgZGlnZXN0IiwKICAgICAgICAibGFiZWwiOiAiTnVtUHkgUk5HIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAgICJzdGF0dXMiOiAiZmFpbCIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAic2VyaWFsaXplZD1GYWxzZSwgZGlnZXN0X21hdGNoPUZhbHNlIiwKICAgICAgICAiY2F0ZWdvcnkiOiAiUmVxdWlyZWQgdHJhaW5pbmcgc3RhdGUiLAogICAgICAgICJjaGVja19pZCI6ICJzdGF0ZS50b3JjaF9ybmciLAogICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgInJlc3RvcmU6dG9yY2gtcm5nIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogInNlcmlhbGl6ZWQgc3RhdGUgd2l0aCBleGFjdCBkaWdlc3QiLAogICAgICAgICJsYWJlbCI6ICJUb3JjaCBSTkcgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAgICAgInN0YXR1cyI6ICJmYWlsIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICJmaXJzdCBiYXRjaCBhdCA0LCBmaXJzdCBjb21wbGV0aW9uIGF0IDUiLAogICAgICAgICJjYXRlZ29yeSI6ICJQcm9jZXNzIHJlY292ZXJ5IiwKICAgICAgICAiY2hlY2tfaWQiOiAicHJvY2Vzcy5uZXh0X3N0ZXAiLAogICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgInByb2Nlc3M6bmV4dC1zdGVwIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogImZpcnN0IGJhdGNoIGF0IDQsIGZpcnN0IGNvbXBsZXRpb24gYXQgNSIsCiAgICAgICAgImxhYmVsIjogIlJlc3VtZWQgcnVuIGNvbnRpbnVlcyBmcm9tIHRoZSBleHBlY3RlZCBuZXh0IHN0ZXAiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAiMzE0MTIiLAogICAgICAgICJjYXRlZ29yeSI6ICJQcm9jZXNzIHJlY292ZXJ5IiwKICAgICAgICAiY2hlY2tfaWQiOiAicHJvY2Vzcy5vcmlnaW5hbF9waWQiLAogICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgInByb2Nlc3M6b3JpZ2luYWwtcGlkIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogIjMxNDEyIiwKICAgICAgICAibGFiZWwiOiAiT3JpZ2luYWwgd29ya2VyIFBJRCBpcyByZWNvcmRlZCIsCiAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICJtZXRob2Q9VGVybWluYXRlUHJvY2VzcyB2aWEgc3VicHJvY2Vzcy5Qb3Blbi5raWxsLCBleGl0PTEsIHZlcmlmaWVkPVRydWUiLAogICAgICAgICJjYXRlZ29yeSI6ICJQcm9jZXNzIHJlY292ZXJ5IiwKICAgICAgICAiY2hlY2tfaWQiOiAicHJvY2Vzcy5leHBlY3RlZF90ZXJtaW5hdGlvbiIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAicHJvY2Vzczp0ZXJtaW5hdGlvbiIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJwYXJlbnQgdGVybWluYXRpb24gd2l0aCBub256ZXJvIGV4aXQgY29kZSIsCiAgICAgICAgImxhYmVsIjogIk9yaWdpbmFsIHdvcmtlciB0ZXJtaW5hdGlvbiBpcyB2ZXJpZmllZCIsCiAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICIxNjYwMCIsCiAgICAgICAgImNhdGVnb3J5IjogIlByb2Nlc3MgcmVjb3ZlcnkiLAogICAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLm5ld19yZWNvdmVyeV9waWQiLAogICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgInByb2Nlc3M6cmVjb3ZlcnktcGlkIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogIlBJRCBkaWZmZXJlbnQgZnJvbSAzMTQxMiIsCiAgICAgICAgImxhYmVsIjogIlJlY292ZXJ5IHVzZXMgYSBkaWZmZXJlbnQgUElEIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogImV4aXQ9MCwgdmVyaWZpZWQ9VHJ1ZSIsCiAgICAgICAgImNhdGVnb3J5IjogIlByb2Nlc3MgcmVjb3ZlcnkiLAogICAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLnJlY292ZXJ5X2V4aXQiLAogICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgInByb2Nlc3M6cmVjb3ZlcnktZXhpdCIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJleGl0IGNvZGUgMCIsCiAgICAgICAgImxhYmVsIjogIlJlY292ZXJ5IHdvcmtlciBleGl0cyBzdWNjZXNzZnVsbHkiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAiMCBzdGVwcyIsCiAgICAgICAgImNhdGVnb3J5IjogIlNhZmV0eSBhbmQgcm9sbGJhY2siLAogICAgICAgICJjaGVja19pZCI6ICJyb2xsYmFjay5oYXJkX2xpbWl0IiwKICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJyb2xsYmFjazphY2hpZXZlZCIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICI8PSAwIHN0ZXBzIiwKICAgICAgICAibGFiZWwiOiAiQWNoaWV2ZWQgcm9sbGJhY2sgaXMgd2l0aGluIHRoZSBoYXJkIGxpbWl0IiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogImQ2MDU3MmFlYTEyZjkxOTYwZjNmMDAzMGJkZmRjYTU1ZmRhZmUwNTkxNDZjNzIzMGFmOTA5NDkyMzgxMWQzMTIiLAogICAgICAgICJjYXRlZ29yeSI6ICJUcmFqZWN0b3J5IGNvcnJlY3RuZXNzIiwKICAgICAgICAiY2hlY2tfaWQiOiAidHJhamVjdG9yeS5jaGVja3BvaW50X2V2YWx1YXRpb24iLAogICAgICAgICJkZXRhaWxzIjogIkV4YWN0IFNIQS0yNTYgY29tcGFyaXNvbjsgbm8gbnVtZXJpY2FsIHRvbGVyYW5jZSBpcyBhcHBsaWVkLiIsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJ0cmFqZWN0b3J5OmNoZWNrcG9pbnQtZXZhbHVhdGlvbiIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJkNjA1NzJhZWExMmY5MTk2MGYzZjAwMzBiZGZkY2E1NWZkYWZlMDU5MTQ2YzcyMzBhZjkwOTQ5MjM4MTFkMzEyIiwKICAgICAgICAibGFiZWwiOiAiRml4ZWQgZXZhbHVhdGlvbiBhZnRlciByZXN0b3JlIG1hdGNoZXMiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAiZDI4NTQ3ZTgyZGM0MTJkNTgwNjBlOGJlNjRkZWI1MjE5MWI3YjI1ODU2MWJlNDc4NzQ2OTRiMWM1NDZlY2E2NiIsCiAgICAgICAgImNhdGVnb3J5IjogIlRyYWplY3RvcnkgY29ycmVjdG5lc3MiLAogICAgICAgICJjaGVja19pZCI6ICJ0cmFqZWN0b3J5LmZpbmFsX3RyYWluYWJsZSIsCiAgICAgICAgImRldGFpbHMiOiAiRXhhY3QgU0hBLTI1NiBjb21wYXJpc29uOyBubyBudW1lcmljYWwgdG9sZXJhbmNlIGlzIGFwcGxpZWQuIiwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgInRyYWplY3Rvcnk6ZmluYWwtdHJhaW5hYmxlIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogIjFmYzcyZmRmMjE0ODdhZmU3YjMyZGE4MzNkMjMwMGNkOWE2OGYwYzBjNmYzY2UxNDU2OTEwYTUxMDJhOTI5OTciLAogICAgICAgICJsYWJlbCI6ICJGaW5hbCB0cmFpbmFibGUgcGFyYW1ldGVycyBtYXRjaCBjb250cm9sIiwKICAgICAgICAic3RhdHVzIjogImZhaWwiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogIjQzNDZhMmQ3N2IzNzA3NmI4NTNkNDUyOTk4MTgyNGVkZDU0OTUzOGY5MzhkNDk2NDIyMDg5OTE0OWRkNWI0Y2QiLAogICAgICAgICJjYXRlZ29yeSI6ICJUcmFqZWN0b3J5IGNvcnJlY3RuZXNzIiwKICAgICAgICAiY2hlY2tfaWQiOiAidHJhamVjdG9yeS5maW5hbF9ldmFsdWF0aW9uIiwKICAgICAgICAiZGV0YWlscyI6ICJFeGFjdCBTSEEtMjU2IGNvbXBhcmlzb247IG5vIG51bWVyaWNhbCB0b2xlcmFuY2UgaXMgYXBwbGllZC4iLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAidHJhamVjdG9yeTpmaW5hbC1ldmFsdWF0aW9uIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogImE0MmE2ZDI1YzhhYWY2Njc0MTMwZWY2MzQzOWY2ZmQ0MTU4MjRiZDIzZmY5Y2Q2YTdjMGNhMDMwNWJlM2VmOWEiLAogICAgICAgICJsYWJlbCI6ICJGaW5hbCBldmFsdWF0aW9uIGxvZ2l0cyBtYXRjaCBjb250cm9sIiwKICAgICAgICAic3RhdHVzIjogImZhaWwiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogInNlcXVlbmNlIGRpZmZlcnMiLAogICAgICAgICJjYXRlZ29yeSI6ICJUcmFqZWN0b3J5IGNvcnJlY3RuZXNzIiwKICAgICAgICAiY2hlY2tfaWQiOiAidHJhamVjdG9yeS5sb3NzX2hpc3RvcnkiLAogICAgICAgICJkZXRhaWxzIjogIkV4YWN0IGZsb2F0IHNlcXVlbmNlIGNvbXBhcmlzb247IG5vIG51bWVyaWNhbCB0b2xlcmFuY2UgaXMgYXBwbGllZC4iLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAidHJhamVjdG9yeTpsb3NzLWhpc3RvcnkiCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAiZXhhY3QgbG9zcyBzZXF1ZW5jZSBlcXVhbGl0eSIsCiAgICAgICAgImxhYmVsIjogIkNvbnRpbnVlZCBsb3NzIHRyYWplY3RvcnkgbWF0Y2hlcyBjb250cm9sIiwKICAgICAgICAic3RhdHVzIjogImZhaWwiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogImNvbnRhaW5lZCIsCiAgICAgICAgImNhdGVnb3J5IjogIlNhZmV0eSBhbmQgcm9sbGJhY2siLAogICAgICAgICJjaGVja19pZCI6ICJzYWZldHkucGF0aF9jb250YWlubWVudCIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAic2FmZXR5OnBhdGgtY29udGFpbm1lbnQiCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAiYWxsIHBhdGhzIGNvbnRhaW5lZDsgc3ltbGluayBlc2NhcGVzIHJlamVjdGVkIiwKICAgICAgICAibGFiZWwiOiAiQWxsIG1hbmFnZWQgd3JpdGUgcGF0aHMgcGFzc2VkIGNvbnRhaW5tZW50IiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogIm1hbmlmZXN0IGxhY2tzOiBudW1weV9ybmcsIG9wdGltaXplciwgcHl0aG9uX3JuZywgc2NoZWR1bGVyLCB0b3JjaF9ybmciLAogICAgICAgICJjYXRlZ29yeSI6ICJTYWZldHkgYW5kIHJvbGxiYWNrIiwKICAgICAgICAiY2hlY2tfaWQiOiAiY29udHJhY3Qubm9fbWFuZGF0b3J5X29taXNzaW9uIiwKICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJjb250cmFjdDptYW5kYXRvcnktc3RhdGUiCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAiYWxsIG1hbmRhdG9yeSBjb250aW51YXRpb24gc3RhdGUgZGVjbGFyZWQiLAogICAgICAgICJsYWJlbCI6ICJObyBtYW5kYXRvcnkgY29udHJhY3QgcmVxdWlyZW1lbnQgd2FzIHNpbGVudGx5IG9taXR0ZWQiLAogICAgICAgICJzdGF0dXMiOiAiZmFpbCIKICAgICAgfQogICAgXSwKICAgICJjb21wYXJpc29uX3BvbGljeSI6IHsKICAgICAgImF0b2wiOiAwLjAsCiAgICAgICJldmFsdWF0aW9uX2xvZ2l0cyI6ICJzaGEyNTZfZXhhY3QiLAogICAgICAiZXZpZGVuY2UiOiAiVGhlIGNvbnRyb2xsZWQgQ1BVIHdvcmtsb2FkIHVzZXMgZGV0ZXJtaW5pc3RpYyBhbGdvcml0aG1zLCBvbmUgVG9yY2ggdGhyZWFkLCBmaXhlZCBzZWVkcywgYW5kIHN0ZXAtZGVyaXZlZCBiYXRjaGVzLiBDcm9zcy1wcm9jZXNzIGNvbXBhcmlzb25zIGZhaWwgb24gYW55IGRpZ2VzdCBvciBsb3NzLXNlcXVlbmNlIGRpZmZlcmVuY2UuIiwKICAgICAgImxvc3NfaGlzdG9yeSI6ICJzZXF1ZW5jZV9leGFjdCIsCiAgICAgICJtb2RlIjogImV4YWN0IiwKICAgICAgIm9wdGltaXplcl9zdGF0ZSI6ICJzaGEyNTZfZXhhY3QiLAogICAgICAicm5nX3N0YXRlIjogInNoYTI1Nl9leGFjdCIsCiAgICAgICJydG9sIjogMC4wLAogICAgICAic2NoZWR1bGVyX3N0YXRlIjogInNoYTI1Nl9leGFjdCIsCiAgICAgICJ0cmFpbmFibGVfcGFyYW1ldGVycyI6ICJzaGEyNTZfZXhhY3QiCiAgICB9LAogICAgImZhaWxlZF9jaGVja19pZHMiOiBbCiAgICAgICJzdGF0ZS5vcHRpbWl6ZXIiLAogICAgICAic3RhdGUuc2NoZWR1bGVyIiwKICAgICAgInN0YXRlLnB5dGhvbl9ybmciLAogICAgICAic3RhdGUubnVtcHlfcm5nIiwKICAgICAgInN0YXRlLnRvcmNoX3JuZyIsCiAgICAgICJ0cmFqZWN0b3J5LmZpbmFsX3RyYWluYWJsZSIsCiAgICAgICJ0cmFqZWN0b3J5LmZpbmFsX2V2YWx1YXRpb24iLAogICAgICAidHJhamVjdG9yeS5sb3NzX2hpc3RvcnkiLAogICAgICAiY29udHJhY3Qubm9fbWFuZGF0b3J5X29taXNzaW9uIgogICAgXSwKICAgICJoYXJkX3JvbGxiYWNrX2xpbWl0X3N0ZXBzIjogMCwKICAgICJwYXNzZWQiOiBmYWxzZSwKICAgICJzY2hlbWFfdmVyc2lvbiI6ICJyZWNvdmVyeS1nYXRlLXYxIgogIH0sCiAgImxpbWl0YXRpb25zIjogWwogICAgIlBoeXNpY2FsIE5BTkQgd3JpdGVzLCB3cml0ZSBhbXBsaWZpY2F0aW9uLCBhbmQgU1NEIGxpZmV0aW1lIHdlcmUgbm90IG1lYXN1cmVkLiIsCiAgICAiTm8gR1BUIHByb3ZpZGVyLCBkaWFnbm9zaXMsIHJlcGFpciBleGVjdXRpb24sIEhUTUwsIG9yIHBhY2thZ2luZyBpcyBwYXJ0IG9mIFByb21wdCAzLiIKICBdLAogICJwbGF0Zm9ybV9zdXBwb3J0X25vdGUiOiAiV2luZG93czogcGF5bG9hZCBhbmQgbWV0YWRhdGEgZmlsZXMgYXJlIGZzeW5jZWQgYW5kIGRpcmVjdG9yeSByZW5hbWUgaXMgYXRvbWljOyBkaXJlY3RvcnkgZnN5bmMgaXMgdW5hdmFpbGFibGUgdGhyb3VnaCBQeXRob24gYW5kIHJlbWFpbnMgYmVzdC1lZmZvcnQuIiwKICAicHJvZmlsZSI6ICJjaSIsCiAgInJlY292ZXJ5IjogewogICAgImFmdGVyX3Jlc3RvcmUiOiB7CiAgICAgICJldmFsdWF0aW9uX3NoYTI1NiI6ICJkNjA1NzJhZWExMmY5MTk2MGYzZjAwMzBiZGZkY2E1NWZkYWZlMDU5MTQ2YzcyMzBhZjkwOTQ5MjM4MTFkMzEyIiwKICAgICAgImdsb2JhbF9zdGVwIjogNCwKICAgICAgImxvc3NfaGlzdG9yeSI6IFsKICAgICAgICAzLjUzNzE5NzU4OTg3NDI2NzYsCiAgICAgICAgMy40MzQ0NTc1NDA1MTIwODUsCiAgICAgICAgMy41OTc3MDY1NTYzMjAxOTA0LAogICAgICAgIDMuNTYwNzQ2NjY5NzY5Mjg3CiAgICAgIF0sCiAgICAgICJvcHRpbWl6ZXJfc2hhMjU2IjogIjNmZDBmNTBlMGI0ODNmZDU0OTUyMDI5NmY4OGVjNjE2NGM2MGRkOGU3NTNkYTU0M2JmZjdiYTUzNWQ5ZTZkZTMiLAogICAgICAic2NoZWR1bGVyX3NoYTI1NiI6ICI3OGEwMzM5ZTEyYWJlZDMyNzJiYmJhYWIxZjNhZTY3NTliNTVlYWYzZjNlZTgwN2Y5OThjNWNjOTIxMTNjZmE4IiwKICAgICAgInRyYWluYWJsZV9zdGF0ZV9zaGEyNTYiOiAiNDNiYTc1ODA4OTA2OTMyYTAwNWIwZDNlMTg2YjU3ODZhYjY0YTI1ZmRjZTU1NDI2NTVkMmQwOTUxZmM2ZWViNSIKICAgIH0sCiAgICAiYWZ0ZXJfcmVzdG9yZV9ybmciOiB7CiAgICAgICJudW1weV9zaGEyNTYiOiAiYWRjN2U1NDVlYzA1MzBlYWU5ZjFkYTcyNWU4M2Y0OGIxNDZiZDRlYzc5Zjk4NDUxMzY3Y2EzZDE4ZTk5NGRiNSIsCiAgICAgICJweXRob25fc2hhMjU2IjogImRkOGFlYzFjY2YzMDUzZGU2MWVkNmE0NTllMjY2OGMzODViNzk5NmVhZWRkOTQ3NDQ0MDA2MjA5OTk1YTcwNjMiLAogICAgICAidG9yY2hfc2hhMjU2IjogIjU2YTU5ZWU0MTU0Yzg3NjM4NmQ5YWZhOTZhMjQyN2Y3OWE3MzZlOTg4ODdjYzYwNzdhNjQwOWQwYWZmZWUyOTAiCiAgICB9LAogICAgImNoZWNrcG9pbnRfcGF0aCI6ICJjaGVja3BvaW50cy9taXNzaW5nLXRyYWluaW5nLXN0YXRlL2NoZWNrcG9pbnQtc3RlcC0wMDAwMDQiLAogICAgImNvbXBsZXRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjA0LjY2OTY0NVoiLAogICAgImZpbmFsIjogewogICAgICAiZXZhbHVhdGlvbl9zaGEyNTYiOiAiNDM0NmEyZDc3YjM3MDc2Yjg1M2Q0NTI5OTgxODI0ZWRkNTQ5NTM4ZjkzOGQ0OTY0MjIwODk5MTQ5ZGQ1YjRjZCIsCiAgICAgICJnbG9iYWxfc3RlcCI6IDgsCiAgICAgICJsb3NzX2hpc3RvcnkiOiBbCiAgICAgICAgMy41MzcxOTc1ODk4NzQyNjc2LAogICAgICAgIDMuNDM0NDU3NTQwNTEyMDg1LAogICAgICAgIDMuNTk3NzA2NTU2MzIwMTkwNCwKICAgICAgICAzLjU2MDc0NjY2OTc2OTI4NywKICAgICAgICAzLjU5MDQ3OTEzNTUxMzMwNTcsCiAgICAgICAgMy42MDkxMTA4MzIyMTQzNTU1LAogICAgICAgIDMuNTIxMzY2MTE5Mzg0NzY1NiwKICAgICAgICAzLjg2NTkzNTA4NzIwMzk3OTUKICAgICAgXSwKICAgICAgIm9wdGltaXplcl9zaGEyNTYiOiAiZTgwMzExNGI1MDU2MDcwZDc1YTNmMDJmNmExY2Q5ODdmNjJiMGQ4NGZjYjUzMzUwYmI0M2U4NDc1N2YyOWVmYSIsCiAgICAgICJzY2hlZHVsZXJfc2hhMjU2IjogImNhYTgxN2ZiMzE5MWFiMTQ1NmFkZTAwMzIwNTY1ZmIzZGZiN2U3ZTY0OGExMjA3ZjNmMjJmMDQ4OTNkZWM3NzAiLAogICAgICAidHJhaW5hYmxlX3N0YXRlX3NoYTI1NiI6ICJkMjg1NDdlODJkYzQxMmQ1ODA2MGU4YmU2NGRlYjUyMTkxYjdiMjU4NTYxYmU0Nzg3NDY5NGIxYzU0NmVjYTY2IgogICAgfSwKICAgICJmaXJzdF9jb21wbGV0ZWRfc3RlcCI6IDUsCiAgICAiZmlyc3RfcmVzdW1lZF9iYXRjaF9zdGVwIjogNCwKICAgICJyZXN0b3JlZF9nbG9iYWxfc3RlcCI6IDQsCiAgICAic2NoZW1hX3ZlcnNpb24iOiAicmVjb3Zlcnktd29ya2VyLXJlc3VsdC12MSIsCiAgICAic3RhcnRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjAzLjE4NjY3MVoiLAogICAgInN0cmF0ZWd5IjogIm1pc3NpbmdfdHJhaW5pbmdfc3RhdGUiLAogICAgIndvcmtlcl9waWQiOiAxNjYwMAogIH0sCiAgInJlY292ZXJ5X3Byb2Nlc3MiOiB7CiAgICAiY29tcGxldGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjk6MDUuMDg4NjMxWiIsCiAgICAiZXhpdF9jb2RlIjogMCwKICAgICJleGl0X3ZlcmlmaWVkIjogdHJ1ZSwKICAgICJzdGFydGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjg6NTkuMTc5MjAxWiIsCiAgICAid29ya2VyX3BpZCI6IDE2NjAwCiAgfSwKICAicmVzdWx0X3BhdGgiOiAicmVzdWx0Lmpzb24iLAogICJydW5faWQiOiAiaW5pdGlhbCIsCiAgInNjaGVtYV92ZXJzaW9uIjogImNyYXNoLWV4cGVyaW1lbnQtdjEiLAogICJzdHJhdGVneSI6ICJtaXNzaW5nX3RyYWluaW5nX3N0YXRlIgp9Cg==",
   "initial/workers/recovery-result.json": "ewogICJhZnRlcl9yZXN0b3JlIjogewogICAgImV2YWx1YXRpb25fc2hhMjU2IjogImQ2MDU3MmFlYTEyZjkxOTYwZjNmMDAzMGJkZmRjYTU1ZmRhZmUwNTkxNDZjNzIzMGFmOTA5NDkyMzgxMWQzMTIiLAogICAgImdsb2JhbF9zdGVwIjogNCwKICAgICJsb3NzX2hpc3RvcnkiOiBbCiAgICAgIDMuNTM3MTk3NTg5ODc0MjY3NiwKICAgICAgMy40MzQ0NTc1NDA1MTIwODUsCiAgICAgIDMuNTk3NzA2NTU2MzIwMTkwNCwKICAgICAgMy41NjA3NDY2Njk3NjkyODcKICAgIF0sCiAgICAib3B0aW1pemVyX3NoYTI1NiI6ICIzZmQwZjUwZTBiNDgzZmQ1NDk1MjAyOTZmODhlYzYxNjRjNjBkZDhlNzUzZGE1NDNiZmY3YmE1MzVkOWU2ZGUzIiwKICAgICJzY2hlZHVsZXJfc2hhMjU2IjogIjc4YTAzMzllMTJhYmVkMzI3MmJiYmFhYjFmM2FlNjc1OWI1NWVhZjNmM2VlODA3Zjk5OGM1Y2M5MjExM2NmYTgiLAogICAgInRyYWluYWJsZV9zdGF0ZV9zaGEyNTYiOiAiNDNiYTc1ODA4OTA2OTMyYTAwNWIwZDNlMTg2YjU3ODZhYjY0YTI1ZmRjZTU1NDI2NTVkMmQwOTUxZmM2ZWViNSIKICB9LAogICJhZnRlcl9yZXN0b3JlX3JuZyI6IHsKICAgICJudW1weV9zaGEyNTYiOiAiYWRjN2U1NDVlYzA1MzBlYWU5ZjFkYTcyNWU4M2Y0OGIxNDZiZDRlYzc5Zjk4NDUxMzY3Y2EzZDE4ZTk5NGRiNSIsCiAgICAicHl0aG9uX3NoYTI1NiI6ICJkZDhhZWMxY2NmMzA1M2RlNjFlZDZhNDU5ZTI2NjhjMzg1Yjc5OTZlYWVkZDk0NzQ0NDAwNjIwOTk5NWE3MDYzIiwKICAgICJ0b3JjaF9zaGEyNTYiOiAiNTZhNTllZTQxNTRjODc2Mzg2ZDlhZmE5NmEyNDI3Zjc5YTczNmU5ODg4N2NjNjA3N2E2NDA5ZDBhZmZlZTI5MCIKICB9LAogICJjaGVja3BvaW50X3BhdGgiOiAiY2hlY2twb2ludHMvbWlzc2luZy10cmFpbmluZy1zdGF0ZS9jaGVja3BvaW50LXN0ZXAtMDAwMDA0IiwKICAiY29tcGxldGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjk6MDQuNjY5NjQ1WiIsCiAgImZpbmFsIjogewogICAgImV2YWx1YXRpb25fc2hhMjU2IjogIjQzNDZhMmQ3N2IzNzA3NmI4NTNkNDUyOTk4MTgyNGVkZDU0OTUzOGY5MzhkNDk2NDIyMDg5OTE0OWRkNWI0Y2QiLAogICAgImdsb2JhbF9zdGVwIjogOCwKICAgICJsb3NzX2hpc3RvcnkiOiBbCiAgICAgIDMuNTM3MTk3NTg5ODc0MjY3NiwKICAgICAgMy40MzQ0NTc1NDA1MTIwODUsCiAgICAgIDMuNTk3NzA2NTU2MzIwMTkwNCwKICAgICAgMy41NjA3NDY2Njk3NjkyODcsCiAgICAgIDMuNTkwNDc5MTM1NTEzMzA1NywKICAgICAgMy42MDkxMTA4MzIyMTQzNTU1LAogICAgICAzLjUyMTM2NjExOTM4NDc2NTYsCiAgICAgIDMuODY1OTM1MDg3MjAzOTc5NQogICAgXSwKICAgICJvcHRpbWl6ZXJfc2hhMjU2IjogImU4MDMxMTRiNTA1NjA3MGQ3NWEzZjAyZjZhMWNkOTg3ZjYyYjBkODRmY2I1MzM1MGJiNDNlODQ3NTdmMjllZmEiLAogICAgInNjaGVkdWxlcl9zaGEyNTYiOiAiY2FhODE3ZmIzMTkxYWIxNDU2YWRlMDAzMjA1NjVmYjNkZmI3ZTdlNjQ4YTEyMDdmM2YyMmYwNDg5M2RlYzc3MCIsCiAgICAidHJhaW5hYmxlX3N0YXRlX3NoYTI1NiI6ICJkMjg1NDdlODJkYzQxMmQ1ODA2MGU4YmU2NGRlYjUyMTkxYjdiMjU4NTYxYmU0Nzg3NDY5NGIxYzU0NmVjYTY2IgogIH0sCiAgImZpcnN0X2NvbXBsZXRlZF9zdGVwIjogNSwKICAiZmlyc3RfcmVzdW1lZF9iYXRjaF9zdGVwIjogNCwKICAicmVzdG9yZWRfZ2xvYmFsX3N0ZXAiOiA0LAogICJzY2hlbWFfdmVyc2lvbiI6ICJyZWNvdmVyeS13b3JrZXItcmVzdWx0LXYxIiwKICAic3RhcnRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjAzLjE4NjY3MVoiLAogICJzdHJhdGVneSI6ICJtaXNzaW5nX3RyYWluaW5nX3N0YXRlIiwKICAid29ya2VyX3BpZCI6IDE2NjAwCn0K",
   "job-summary.md": "IyBGbGFzaFBpbG90IENJIHN1bW1hcnkKCi0gT3V0Y29tZTogKipWRVJJRklFRCoqCi0gRXZpZGVuY2Uga2luZDogYG5hdGl2ZS1xdWFsaWZpY2F0aW9uYAotIEZyYW1ld29yazogYG5hdGl2ZS1weXRvcmNoYAotIFF1YWxpZmljYXRpb24gcHJvZmlsZTogYGV4YWN0LXRyYWluaW5nLXJlc3VtZWAKLSBDaGVja3M6IGAyNC8yNGAgbm9uLWZhaWxpbmcKLSBSUE86IGAwYCBzdGVwcwotIFJUTzogYDMuOTY1NDU1YCBzZWNvbmRzCgojIyBFeGFjdCBmYWlsZWQgcmVxdWlyZW1lbnRzCgotIE5vbmUKClRoaXMgc3VtbWFyeSBpcyBkZXJpdmVkIGZyb20gdGhlIHNhbWUgdHlwZWQgZXZpZGVuY2UgdXNlZCBieSB0aGUgbG9jYWwgQ0xJLgo=",
   "junit.xml": "PD94bWwgdmVyc2lvbj0nMS4wJyBlbmNvZGluZz0ndXRmLTgnPz4KPHRlc3RzdWl0ZSBuYW1lPSJmbGFzaHBpbG90Lm5hdGl2ZS1xdWFsaWZpY2F0aW9uIiB0ZXN0cz0iMjQiIGZhaWx1cmVzPSIwIiBlcnJvcnM9IjAiIHNraXBwZWQ9IjAiPgogIDxwcm9wZXJ0aWVzPgogICAgPHByb3BlcnR5IG5hbWU9InN0YXR1cyIgdmFsdWU9IlZFUklGSUVEIiAvPgogICAgPHByb3BlcnR5IG5hbWU9ImZyYW1ld29yayIgdmFsdWU9Im5hdGl2ZS1weXRvcmNoIiAvPgogICAgPHByb3BlcnR5IG5hbWU9InF1YWxpZmljYXRpb25fcHJvZmlsZSIgdmFsdWU9ImV4YWN0LXRyYWluaW5nLXJlc3VtZSIgLz4KICAgIDxwcm9wZXJ0eSBuYW1lPSJycG9fc3RlcHMiIHZhbHVlPSIwIiAvPgogICAgPHByb3BlcnR5IG5hbWU9InJ0b19zZWNvbmRzIiB2YWx1ZT0iMy45NjU0NTUiIC8+CiAgPC9wcm9wZXJ0aWVzPgogIDx0ZXN0Y2FzZSBjbGFzc25hbWU9ImZsYXNocGlsb3QubmF0aXZlLXB5dG9yY2giIG5hbWU9ImludGVncml0eS5tYW5pZmVzdF9zY2hlbWEiPgogICAgPHN5c3RlbS1vdXQ+TWFuaWZlc3Qgc2NoZW1hIHZhbGlkIEV4cGVjdGVkPWNoZWNrcG9pbnQtbWFuaWZlc3QtdjE7IGFjdHVhbD1jaGVja3BvaW50LW1hbmlmZXN0LXYxLjwvc3lzdGVtLW91dD4KICA8L3Rlc3RjYXNlPgogIDx0ZXN0Y2FzZSBjbGFzc25hbWU9ImZsYXNocGlsb3QubmF0aXZlLXB5dG9yY2giIG5hbWU9ImludGVncml0eS5jb21wbGV0aW9uX21hcmtlciI+CiAgICA8c3lzdGVtLW91dD5Db21wbGV0aW9uIG1hcmtlciBwcmVzZW50IEV4cGVjdGVkPUNPTVBMRVRFIHByZXNlbnQgaW4gZmluYWwgY2hlY2twb2ludDsgYWN0dWFsPXByZXNlbnQuPC9zeXN0ZW0tb3V0PgogIDwvdGVzdGNhc2U+CiAgPHRlc3RjYXNlIGNsYXNzbmFtZT0iZmxhc2hwaWxvdC5uYXRpdmUtcHl0b3JjaCIgbmFtZT0iaW50ZWdyaXR5LmNoZWNrc3VtcyI+CiAgICA8c3lzdGVtLW91dD5BbGwgcGF5bG9hZCBjaGVja3N1bXMgdmFsaWQgRXhwZWN0ZWQ9ZXZlcnkgbWFuaWZlc3QgcGF5bG9hZCBtYXRjaGVzIFNIQS0yNTYgYW5kIHNpemU7IGFjdHVhbD01IHBheWxvYWRzIHZhbGlkYXRlZC48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lm5hdGl2ZS1weXRvcmNoIiBuYW1lPSJpbnRlZ3JpdHkuYmFzZV9wcmVzZW50Ij4KICAgIDxzeXN0ZW0tb3V0PkJhc2UgYXJ0aWZhY3QgcHJlc2VudCB3aGVuIHJlcXVpcmVkIEV4cGVjdGVkPWNvbnRhaW5lZCBpbW11dGFibGUgYmFzZSBhcnRpZmFjdDsgYWN0dWFsPXByZXNlbnQuPC9zeXN0ZW0tb3V0PgogIDwvdGVzdGNhc2U+CiAgPHRlc3RjYXNlIGNsYXNzbmFtZT0iZmxhc2hwaWxvdC5uYXRpdmUtcHl0b3JjaCIgbmFtZT0iaW50ZWdyaXR5LmJhc2VfaGFzaCI+CiAgICA8c3lzdGVtLW91dD5CYXNlIGFydGlmYWN0IGhhc2ggbWF0Y2hlcyBFeHBlY3RlZD1jMTdjYzg5OTRjOGYwZmU2ZGVmMzI0MjNiMGU1ZDllZmVkZmZiM2NkNzFjN2RlOTYzMWYyNmNmNTA1OTI1ZDg2OyBhY3R1YWw9YzE3Y2M4OTk0YzhmMGZlNmRlZjMyNDIzYjBlNWQ5ZWZlZGZmYjNjZDcxYzdkZTk2MzFmMjZjZjUwNTkyNWQ4Ni48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lm5hdGl2ZS1weXRvcmNoIiBuYW1lPSJzdGF0ZS5nbG9iYWxfc3RlcCI+CiAgICA8c3lzdGVtLW91dD5DaGVja3BvaW50IGdsb2JhbCBzdGVwIGlzIHZhbGlkIEV4cGVjdGVkPTAgJmx0OyBzdGVwICZsdDsgOCwgY29uc2lzdGVudCBhY3Jvc3MgcmVzdG9yZTsgYWN0dWFsPW1hbmlmZXN0PTQsIGV2ZW50PTQsIHJlc3RvcmVkPTQuPC9zeXN0ZW0tb3V0PgogIDwvdGVzdGNhc2U+CiAgPHRlc3RjYXNlIGNsYXNzbmFtZT0iZmxhc2hwaWxvdC5uYXRpdmUtcHl0b3JjaCIgbmFtZT0ic3RhdGUubW9kZWxfb3JfYWRhcHRlciI+CiAgICA8c3lzdGVtLW91dD5Nb2RlbCBvciBhZGFwdGVyIHN0YXRlIHJlc3RvcmVzIEV4cGVjdGVkPXNlcmlhbGl6ZWQgYWRhcHRlciBhbmQgZXhhY3QgdHJhaW5hYmxlLXN0YXRlIGRpZ2VzdDsgYWN0dWFsPXNlcmlhbGl6ZWQ9VHJ1ZSwgZGlnZXN0X21hdGNoPVRydWUuPC9zeXN0ZW0tb3V0PgogIDwvdGVzdGNhc2U+CiAgPHRlc3RjYXNlIGNsYXNzbmFtZT0iZmxhc2hwaWxvdC5uYXRpdmUtcHl0b3JjaCIgbmFtZT0ic3RhdGUub3B0aW1pemVyIj4KICAgIDxzeXN0ZW0tb3V0Pk9wdGltaXplciBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIEV4cGVjdGVkPXNlcmlhbGl6ZWQgb3B0aW1pemVyIHdpdGggZXhhY3QgZGlnZXN0OyBhY3R1YWw9c2VyaWFsaXplZD1UcnVlLCBkaWdlc3RfbWF0Y2g9VHJ1ZS48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lm5hdGl2ZS1weXRvcmNoIiBuYW1lPSJzdGF0ZS5zY2hlZHVsZXIiPgogICAgPHN5c3RlbS1vdXQ+U2NoZWR1bGVyIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQgRXhwZWN0ZWQ9c2VyaWFsaXplZCBzY2hlZHVsZXIgd2l0aCBleGFjdCBkaWdlc3Q7IGFjdHVhbD1zZXJpYWxpemVkPVRydWUsIGRpZ2VzdF9tYXRjaD1UcnVlLjwvc3lzdGVtLW91dD4KICA8L3Rlc3RjYXNlPgogIDx0ZXN0Y2FzZSBjbGFzc25hbWU9ImZsYXNocGlsb3QubmF0aXZlLXB5dG9yY2giIG5hbWU9InN0YXRlLnB5dGhvbl9ybmciPgogICAgPHN5c3RlbS1vdXQ+UHl0aG9uIFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIEV4cGVjdGVkPXNlcmlhbGl6ZWQgc3RhdGUgd2l0aCBleGFjdCBkaWdlc3Q7IGFjdHVhbD1zZXJpYWxpemVkPVRydWUsIGRpZ2VzdF9tYXRjaD1UcnVlLjwvc3lzdGVtLW91dD4KICA8L3Rlc3RjYXNlPgogIDx0ZXN0Y2FzZSBjbGFzc25hbWU9ImZsYXNocGlsb3QubmF0aXZlLXB5dG9yY2giIG5hbWU9InN0YXRlLm51bXB5X3JuZyI+CiAgICA8c3lzdGVtLW91dD5OdW1QeSBSTkcgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCBFeHBlY3RlZD1zZXJpYWxpemVkIHN0YXRlIHdpdGggZXhhY3QgZGlnZXN0OyBhY3R1YWw9c2VyaWFsaXplZD1UcnVlLCBkaWdlc3RfbWF0Y2g9VHJ1ZS48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lm5hdGl2ZS1weXRvcmNoIiBuYW1lPSJzdGF0ZS50b3JjaF9ybmciPgogICAgPHN5c3RlbS1vdXQ+VG9yY2ggUk5HIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQgRXhwZWN0ZWQ9c2VyaWFsaXplZCBzdGF0ZSB3aXRoIGV4YWN0IGRpZ2VzdDsgYWN0dWFsPXNlcmlhbGl6ZWQ9VHJ1ZSwgZGlnZXN0X21hdGNoPVRydWUuPC9zeXN0ZW0tb3V0PgogIDwvdGVzdGNhc2U+CiAgPHRlc3RjYXNlIGNsYXNzbmFtZT0iZmxhc2hwaWxvdC5uYXRpdmUtcHl0b3JjaCIgbmFtZT0icHJvY2Vzcy5uZXh0X3N0ZXAiPgogICAgPHN5c3RlbS1vdXQ+UmVzdW1lZCBydW4gY29udGludWVzIGZyb20gdGhlIGV4cGVjdGVkIG5leHQgc3RlcCBFeHBlY3RlZD1maXJzdCBiYXRjaCBhdCA0LCBmaXJzdCBjb21wbGV0aW9uIGF0IDU7IGFjdHVhbD1maXJzdCBiYXRjaCBhdCA0LCBmaXJzdCBjb21wbGV0aW9uIGF0IDUuPC9zeXN0ZW0tb3V0PgogIDwvdGVzdGNhc2U+CiAgPHRlc3RjYXNlIGNsYXNzbmFtZT0iZmxhc2hwaWxvdC5uYXRpdmUtcHl0b3JjaCIgbmFtZT0icHJvY2Vzcy5vcmlnaW5hbF9waWQiPgogICAgPHN5c3RlbS1vdXQ+T3JpZ2luYWwgd29ya2VyIFBJRCBpcyByZWNvcmRlZCBFeHBlY3RlZD0yNzYzMjsgYWN0dWFsPTI3NjMyLjwvc3lzdGVtLW91dD4KICA8L3Rlc3RjYXNlPgogIDx0ZXN0Y2FzZSBjbGFzc25hbWU9ImZsYXNocGlsb3QubmF0aXZlLXB5dG9yY2giIG5hbWU9InByb2Nlc3MuZXhwZWN0ZWRfdGVybWluYXRpb24iPgogICAgPHN5c3RlbS1vdXQ+T3JpZ2luYWwgd29ya2VyIHRlcm1pbmF0aW9uIGlzIHZlcmlmaWVkIEV4cGVjdGVkPXBhcmVudCB0ZXJtaW5hdGlvbiB3aXRoIG5vbnplcm8gZXhpdCBjb2RlOyBhY3R1YWw9bWV0aG9kPVRlcm1pbmF0ZVByb2Nlc3MgdmlhIHN1YnByb2Nlc3MuUG9wZW4ua2lsbCwgZXhpdD0xLCB2ZXJpZmllZD1UcnVlLjwvc3lzdGVtLW91dD4KICA8L3Rlc3RjYXNlPgogIDx0ZXN0Y2FzZSBjbGFzc25hbWU9ImZsYXNocGlsb3QubmF0aXZlLXB5dG9yY2giIG5hbWU9InByb2Nlc3MubmV3X3JlY292ZXJ5X3BpZCI+CiAgICA8c3lzdGVtLW91dD5SZWNvdmVyeSB1c2VzIGEgZGlmZmVyZW50IFBJRCBFeHBlY3RlZD1QSUQgZGlmZmVyZW50IGZyb20gMjc2MzI7IGFjdHVhbD0zMTM5Ni48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lm5hdGl2ZS1weXRvcmNoIiBuYW1lPSJwcm9jZXNzLnJlY292ZXJ5X2V4aXQiPgogICAgPHN5c3RlbS1vdXQ+UmVjb3Zlcnkgd29ya2VyIGV4aXRzIHN1Y2Nlc3NmdWxseSBFeHBlY3RlZD1leGl0IGNvZGUgMDsgYWN0dWFsPWV4aXQ9MCwgdmVyaWZpZWQ9VHJ1ZS48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lm5hdGl2ZS1weXRvcmNoIiBuYW1lPSJyb2xsYmFjay5oYXJkX2xpbWl0Ij4KICAgIDxzeXN0ZW0tb3V0PkFjaGlldmVkIHJvbGxiYWNrIGlzIHdpdGhpbiB0aGUgaGFyZCBsaW1pdCBFeHBlY3RlZD0mbHQ7PSAwIHN0ZXBzOyBhY3R1YWw9MCBzdGVwcy48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lm5hdGl2ZS1weXRvcmNoIiBuYW1lPSJ0cmFqZWN0b3J5LmNoZWNrcG9pbnRfZXZhbHVhdGlvbiI+CiAgICA8c3lzdGVtLW91dD5GaXhlZCBldmFsdWF0aW9uIGFmdGVyIHJlc3RvcmUgbWF0Y2hlcyBFeHBlY3RlZD1kNjA1NzJhZWExMmY5MTk2MGYzZjAwMzBiZGZkY2E1NWZkYWZlMDU5MTQ2YzcyMzBhZjkwOTQ5MjM4MTFkMzEyOyBhY3R1YWw9ZDYwNTcyYWVhMTJmOTE5NjBmM2YwMDMwYmRmZGNhNTVmZGFmZTA1OTE0NmM3MjMwYWY5MDk0OTIzODExZDMxMi48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lm5hdGl2ZS1weXRvcmNoIiBuYW1lPSJ0cmFqZWN0b3J5LmZpbmFsX3RyYWluYWJsZSI+CiAgICA8c3lzdGVtLW91dD5GaW5hbCB0cmFpbmFibGUgcGFyYW1ldGVycyBtYXRjaCBjb250cm9sIEV4cGVjdGVkPTFmYzcyZmRmMjE0ODdhZmU3YjMyZGE4MzNkMjMwMGNkOWE2OGYwYzBjNmYzY2UxNDU2OTEwYTUxMDJhOTI5OTc7IGFjdHVhbD0xZmM3MmZkZjIxNDg3YWZlN2IzMmRhODMzZDIzMDBjZDlhNjhmMGMwYzZmM2NlMTQ1NjkxMGE1MTAyYTkyOTk3Ljwvc3lzdGVtLW91dD4KICA8L3Rlc3RjYXNlPgogIDx0ZXN0Y2FzZSBjbGFzc25hbWU9ImZsYXNocGlsb3QubmF0aXZlLXB5dG9yY2giIG5hbWU9InRyYWplY3RvcnkuZmluYWxfZXZhbHVhdGlvbiI+CiAgICA8c3lzdGVtLW91dD5GaW5hbCBldmFsdWF0aW9uIGxvZ2l0cyBtYXRjaCBjb250cm9sIEV4cGVjdGVkPWE0MmE2ZDI1YzhhYWY2Njc0MTMwZWY2MzQzOWY2ZmQ0MTU4MjRiZDIzZmY5Y2Q2YTdjMGNhMDMwNWJlM2VmOWE7IGFjdHVhbD1hNDJhNmQyNWM4YWFmNjY3NDEzMGVmNjM0MzlmNmZkNDE1ODI0YmQyM2ZmOWNkNmE3YzBjYTAzMDViZTNlZjlhLjwvc3lzdGVtLW91dD4KICA8L3Rlc3RjYXNlPgogIDx0ZXN0Y2FzZSBjbGFzc25hbWU9ImZsYXNocGlsb3QubmF0aXZlLXB5dG9yY2giIG5hbWU9InRyYWplY3RvcnkubG9zc19oaXN0b3J5Ij4KICAgIDxzeXN0ZW0tb3V0PkNvbnRpbnVlZCBsb3NzIHRyYWplY3RvcnkgbWF0Y2hlcyBjb250cm9sIEV4cGVjdGVkPWV4YWN0IGxvc3Mgc2VxdWVuY2UgZXF1YWxpdHk7IGFjdHVhbD1leGFjdCBtYXRjaC48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KICA8dGVzdGNhc2UgY2xhc3NuYW1lPSJmbGFzaHBpbG90Lm5hdGl2ZS1weXRvcmNoIiBuYW1lPSJzYWZldHkucGF0aF9jb250YWlubWVudCI+CiAgICA8c3lzdGVtLW91dD5BbGwgbWFuYWdlZCB3cml0ZSBwYXRocyBwYXNzZWQgY29udGFpbm1lbnQgRXhwZWN0ZWQ9YWxsIHBhdGhzIGNvbnRhaW5lZDsgc3ltbGluayBlc2NhcGVzIHJlamVjdGVkOyBhY3R1YWw9Y29udGFpbmVkLjwvc3lzdGVtLW91dD4KICA8L3Rlc3RjYXNlPgogIDx0ZXN0Y2FzZSBjbGFzc25hbWU9ImZsYXNocGlsb3QubmF0aXZlLXB5dG9yY2giIG5hbWU9ImNvbnRyYWN0Lm5vX21hbmRhdG9yeV9vbWlzc2lvbiI+CiAgICA8c3lzdGVtLW91dD5ObyBtYW5kYXRvcnkgY29udHJhY3QgcmVxdWlyZW1lbnQgd2FzIHNpbGVudGx5IG9taXR0ZWQgRXhwZWN0ZWQ9YWxsIG1hbmRhdG9yeSBjb250aW51YXRpb24gc3RhdGUgZGVjbGFyZWQ7IGFjdHVhbD1jb21wbGV0ZS48L3N5c3RlbS1vdXQ+CiAgPC90ZXN0Y2FzZT4KPC90ZXN0c3VpdGU+Cg==",
   "measurements/safe-full/checkpoints/checkpoint-step-000004/COMPLETE": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJjb21wbGV0aW9uLW1hcmtlci12MSIsCiAgImNoZWNrcG9pbnRfaWQiOiAiY2hlY2twb2ludC1zdGVwLTAwMDAwNCIKfQo=",
   "measurements/safe-full/checkpoints/checkpoint-step-000004/checksums.json": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJjaGVja3N1bXMtdjEiLAogICJmaWxlcyI6IFsKICAgIHsKICAgICAgInBhdGgiOiAibW9kZWwucHQiLAogICAgICAic2hhMjU2IjogIjJiYmRkNDdiN2UzNDZlZDdkOGYzZWU0NDM4OTdjZTk4ODRkYmU0NTE3ZDA2ZGEyYmJkMzcxZjAyZjQzZjNkMWIiLAogICAgICAic2l6ZV9ieXRlcyI6IDIwNzE4CiAgICB9LAogICAgewogICAgICAicGF0aCI6ICJvcHRpbWl6ZXIucHQiLAogICAgICAic2hhMjU2IjogImNlMWE1N2Y2YjVlZDE0NGY1ZmZlZDBhNzNiMjdjZGE2NmY0OWNhYTE5ZjA2MTI0OTg0ZGJiOWVlZGFiZjRiYWYiLAogICAgICAic2l6ZV9ieXRlcyI6IDU3OTUKICAgIH0sCiAgICB7CiAgICAgICJwYXRoIjogInJuZy5wdCIsCiAgICAgICJzaGEyNTYiOiAiNzFlZDE4MWE4OGY5ZjQyNTBmYTM3MDg4YWNlNmU1MDIzMDhiNjZmNzJkYWUzZTRjMDg1NTE0NTExNjMwZjk3ZSIsCiAgICAgICJzaXplX2J5dGVzIjogMTQyODUKICAgIH0sCiAgICB7CiAgICAgICJwYXRoIjogInNjaGVkdWxlci5wdCIsCiAgICAgICJzaGEyNTYiOiAiNGIwNjc1OGRkOGM1M2Y0NDc5YzM3YjdlNWI1ZmY3YTU4NTA0MDhlYzdlOWE1MTlkMzBjNThjYjhiNjFhNjc1OSIsCiAgICAgICJzaXplX2J5dGVzIjogMTQ2NQogICAgfSwKICAgIHsKICAgICAgInBhdGgiOiAic3RhdGUuanNvbiIsCiAgICAgICJzaGEyNTYiOiAiNmRmZmQ0ODRhY2ViNTI4NTE2OWZjMTcyNjU0N2IxZjNjZDEyMTViNDEyZTYyNTJjOGNmYjA2NDNmMGRmNWQ5ZiIsCiAgICAgICJzaXplX2J5dGVzIjogNTMzCiAgICB9CiAgXQp9Cg==",
   "measurements/safe-full/checkpoints/checkpoint-step-000004/manifest.json": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJjaGVja3BvaW50LW1hbmlmZXN0LXYxIiwKICAiY2hlY2twb2ludF9pZCI6ICJjaGVja3BvaW50LXN0ZXAtMDAwMDA0IiwKICAic3RyYXRlZ3kiOiAic2FmZV9mdWxsIiwKICAicHJvZmlsZSI6ICJjaSIsCiAgImdsb2JhbF9zdGVwIjogNCwKICAiY3JlYXRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjEzLjAyODM3MFoiLAogICJzZXJpYWxpemVkX3N0YXRlIjogWwogICAgIm1vZGVsIiwKICAgICJvcHRpbWl6ZXIiLAogICAgInNjaGVkdWxlciIsCiAgICAiZ2xvYmFsX3N0ZXAiLAogICAgInB5dGhvbl9ybmciLAogICAgIm51bXB5X3JuZyIsCiAgICAidG9yY2hfcm5nIiwKICAgICJjb25maWciCiAgXSwKICAib21pdHRlZF9zdGF0ZSI6IFtdLAogICJiYXNlX2FydGlmYWN0IjogbnVsbCwKICAicGF5bG9hZHMiOiBbCiAgICB7CiAgICAgICJyb2xlIjogIm1vZGVsIiwKICAgICAgInBhdGgiOiAibW9kZWwucHQiLAogICAgICAic2hhMjU2IjogIjJiYmRkNDdiN2UzNDZlZDdkOGYzZWU0NDM4OTdjZTk4ODRkYmU0NTE3ZDA2ZGEyYmJkMzcxZjAyZjQzZjNkMWIiLAogICAgICAic2l6ZV9ieXRlcyI6IDIwNzE4CiAgICB9LAogICAgewogICAgICAicm9sZSI6ICJvcHRpbWl6ZXIiLAogICAgICAicGF0aCI6ICJvcHRpbWl6ZXIucHQiLAogICAgICAic2hhMjU2IjogImNlMWE1N2Y2YjVlZDE0NGY1ZmZlZDBhNzNiMjdjZGE2NmY0OWNhYTE5ZjA2MTI0OTg0ZGJiOWVlZGFiZjRiYWYiLAogICAgICAic2l6ZV9ieXRlcyI6IDU3OTUKICAgIH0sCiAgICB7CiAgICAgICJyb2xlIjogInJuZyIsCiAgICAgICJwYXRoIjogInJuZy5wdCIsCiAgICAgICJzaGEyNTYiOiAiNzFlZDE4MWE4OGY5ZjQyNTBmYTM3MDg4YWNlNmU1MDIzMDhiNjZmNzJkYWUzZTRjMDg1NTE0NTExNjMwZjk3ZSIsCiAgICAgICJzaXplX2J5dGVzIjogMTQyODUKICAgIH0sCiAgICB7CiAgICAgICJyb2xlIjogInNjaGVkdWxlciIsCiAgICAgICJwYXRoIjogInNjaGVkdWxlci5wdCIsCiAgICAgICJzaGEyNTYiOiAiNGIwNjc1OGRkOGM1M2Y0NDc5YzM3YjdlNWI1ZmY3YTU4NTA0MDhlYzdlOWE1MTlkMzBjNThjYjhiNjFhNjc1OSIsCiAgICAgICJzaXplX2J5dGVzIjogMTQ2NQogICAgfSwKICAgIHsKICAgICAgInJvbGUiOiAic3RhdGUiLAogICAgICAicGF0aCI6ICJzdGF0ZS5qc29uIiwKICAgICAgInNoYTI1NiI6ICI2ZGZmZDQ4NGFjZWI1Mjg1MTY5ZmMxNzI2NTQ3YjFmM2NkMTIxNWI0MTJlNjI1MmM4Y2ZiMDY0M2YwZGY1ZDlmIiwKICAgICAgInNpemVfYnl0ZXMiOiA1MzMKICAgIH0KICBdCn0K",
   "measurements/safe-full/checkpoints/checkpoint-step-000004/model.pt": "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m3RxnFJxnVgPAAAAZmluYWxfbm9ybS5iaWFzcZ5oAygoaARoBVgCAAAAMTlxn2gHSxB0caBRSwBLEIVxoUsBhXGiiWgAKVJxo3RxpFJxpVgSAAAAb3V0cHV0X2hlYWQud2VpZ2h0caZoAygoaARoBVgCAAAAMjBxp2gHTQACdHGoUUsASyBLEIZxqUsQSwGGcaqJaAApUnGrdHGsUnGtdX1xrlgJAAAAX21ldGFkYXRhca9oAClScbAoWAAAAABxsX1xslgHAAAAdmVyc2lvbnGzSwFzWA8AAAB0b2tlbl9lbWJlZGRpbmdxtH1xtWizSwFzWBIAAABwb3NpdGlvbl9lbWJlZGRpbmdxtn1xt2izSwFzWAcAAABlbmNvZGVycbh9cblos0sBc1gOAAAAZW5jb2Rlci5sYXllcnNxun1xu2izSwFzWBAAAABlbmNvZGVyLmxheWVycy4wcbx9cb1os0sBc1gaAAAAZW5jb2Rlci5sYXllcnMuMC5zZWxmX2F0dG5xvn1xv2izSwFzWCMAAABlbmNvZGVyLmxheWVycy4wLnNlbGZfYXR0bi5vdXRfcHJvanHAfXHBaLNLAXNYGAAAAGVuY29kZXIubGF5ZXJzLjAubGluZWFyMXHCfXHDaLNLAXNYGAAAAGVuY29kZXIubGF5ZXJzLjAuZHJvcG91dHHEfXHFaLNLAXNYGAAAAGVuY29kZXIubGF5ZXJzLjAubGluZWFyMnHGfXHHaLNLAXNYFgAAAGVuY29kZXIubGF5ZXJzLjAubm9ybTFxyH1xyWizSwFzWBYAAABlbmNvZGVyLmxheWVycy4wLm5vcm0yccp9cctos0sBc1gZAAAAZW5jb2Rlci5sYXllcnMuMC5kcm9wb3V0MXHMfXHNaLNLAXNYGQAAAGVuY29kZXIubGF5ZXJzLjAuZHJvcG91dDJxzn1xz2izSwFzWAcAAABhZGFwdGVycdB9cdFos0sBc1gMAAAAYWRhcHRlci5kb3ducdJ9cdNos0sBc1gSAAAAYWRhcHRlci5hY3RpdmF0aW9ucdR9cdVos0sBc1gPAAAAYWRhcHRlci5kcm9wb3V0cdZ9cddos0sBc1gKAAAAYWRhcHRlci51cHHYfXHZaLNLAXNYCgAAAGZpbmFsX25vcm1x2n1x22izSwFzWAsAAABvdXRwdXRfaGVhZHHc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",
   "measurements/safe-full/checkpoints/checkpoint-step-000004/optimizer.pt": "UEsDBAAACAgAAAAAAAAAAAAAAAAAAAAAAAASABAAb3B0aW1pemVyL2RhdGEucGtsRkIMAFpaWlpaWlpaWlpaWoACfXEAKFgFAAAAc3RhdGVxAX1xAihLAH1xAyhYBAAAAHN0ZXBxBGN0b3JjaC5fdXRpbHMKX3JlYnVpbGRfdGVuc29yX3YyCnEFKChYBwAAAHN0b3JhZ2VxBmN0b3JjaApGbG9hdFN0b3JhZ2UKcQdYAQAAADBxCFgDAAAAY3B1cQlLAXRxClFLACkpiWNjb2xsZWN0aW9ucwpPcmRlcmVkRGljdApxCylScQx0cQ1ScQ5YBwAAAGV4cF9hdmdxD2gFKChoBmgHWAEAAAAxcRBoCUtAdHERUUsASwRLEIZxEksQSwGGcROJaAspUnEUdHEVUnEWWAoAAABleHBfYXZnX3NxcRdoBSgoaAZoB1gBAAAAMnEYaAlLQHRxGVFLAEsESxCGcRpLEEsBhnEbiWgLKVJxHHRxHVJxHnVLAX1xHyhoBGgFKChoBmgHWAEAAAAzcSBoCUsBdHEhUUsAKSmJaAspUnEidHEjUnEkaA9oBSgoaAZoB1gBAAAANHElaAlLBHRxJlFLAEsEhXEnSwGFcSiJaAspUnEpdHEqUnEraBdoBSgoaAZoB1gBAAAANXEsaAlLBHRxLVFLAEsEhXEuSwGFcS+JaAspUnEwdHExUnEydUsCfXEzKGgEaAUoKGgGaAdYAQAAADZxNGgJSwF0cTVRSwApKYloCylScTZ0cTdScThoD2gFKChoBmgHWAEAAAA3cTloCUtAdHE6UUsASxBLBIZxO0sESwGGcTyJaAspUnE9dHE+UnE/aBdoBSgoaAZoB1gBAAAAOHFAaAlLQHRxQVFLAEsQSwSGcUJLBEsBhnFDiWgLKVJxRHRxRVJxRnVLA31xRyhoBGgFKChoBmgHWAEAAAA5cUhoCUsBdHFJUUsAKSmJaAspUnFKdHFLUnFMaA9oBSgoaAZoB1gCAAAAMTBxTWgJSxB0cU5RSwBLEIVxT0sBhXFQiWgLKVJxUXRxUlJxU2gXaAUoKGgGaAdYAgAAADExcVRoCUsQdHFVUUsASxCFcVZLAYVxV4loCylScVh0cVlScVp1dVgMAAAAcGFyYW1fZ3JvdXBzcVtdcVx9cV0oWAIAAABscnFeRz9+uFHrhR65WAUAAABiZXRhc3FfRz/szMzMzMzNRz/v987ZFocrhnFgWAMAAABlcHNxYUc+RXmO4jCMOlgMAAAAd2VpZ2h0X2RlY2F5cWJHP4R64UeuFHtYBwAAAGFtc2dyYWRxY4lYCAAAAG1heGltaXplcWSJWAcAAABmb3JlYWNocWVOWAoAAABjYXB0dXJhYmxlcWaJWA4AAABkaWZmZXJlbnRpYWJsZXFniVgFAAAAZnVzZWRxaE5YFgAAAGRlY291cGxlZF93ZWlnaHRfZGVjYXlxaYhYCgAAAGluaXRpYWxfbHJxakc/hHrhR64Ue1gGAAAAcGFyYW1zcWtdcWwoSwBLAUsCSwNldWF1LlBLBwiqXOnRRAQAAEQEAABQSwMEAAAICAAAAAAAAAAAAAAAAAAAAAAAABkANQBvcHRpbWl6ZXIvLmZvcm1hdF92ZXJzaW9uRkIxAFpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWloxUEsHCLfv3IMBAAAAAQAAAFBLAwQAAAgIAAAAAAAAAAAAAAAAAAAAAAAAHAA1AG9wdGltaXplci8uc3RvcmFnZV9hbGlnbm1lbnRGQjEAWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWjY0UEsHCD93cekCAAAAAgAAAFBLAwQAAAgIAAAAAAAAAAAAAAAAAAAAAAAAEwA9AG9wdGltaXplci9ieXRlb3JkZXJGQjkAWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpabGl0dGxlUEsHCIU94xkGAAAABgAAAFBLAwQAAAgIAAAAAAAAAAAAAAAAAAAAAAAAEAA8AG9wdGltaXplci9kYXRhLzBGQjgAWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWloAAIBAUEsHCMcGG2wEAAAABAAAAFBLAwQAAAgIAAAAAAAAAAAAAAAAAAAAAAAAEAA+AG9wdGltaXplci9kYXRhLzFGQjoAWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWjF3DDwSs5G5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",
   "measurements/safe-full/checkpoints/checkpoint-step-000004/rng.pt": "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",
   "measurements/safe-full/checkpoints/checkpoint-step-000004/scheduler.pt": "UEsDBAAACAgAAAAAAAAAAAAAAAAAAAAAAAASABAAc2NoZWR1bGVyL2RhdGEucGtsRkIMAFpaWlpaWlpaWlpaWoACfXEAKFgMAAAAc3RhcnRfZmFjdG9ycQFHP/AAAAAAAABYCgAAAGVuZF9mYWN0b3JxAkc/4AAAAAAAAFgLAAAAdG90YWxfaXRlcnNxA0sIWAgAAABiYXNlX2xyc3EEXXEFRz+EeuFHrhR7YVgKAAAAbGFzdF9lcG9jaHEGSwRYCwAAAF9zdGVwX2NvdW50cQdLBVgLAAAAX2lzX2luaXRpYWxxCIlYGgAAAF9nZXRfbHJfY2FsbGVkX3dpdGhpbl9zdGVwcQmJWAgAAABfbGFzdF9scnEKXXELRz9+uFHrhR65YXUuUEsHCFYlw7bmAAAA5gAAAFBLAwQAAAgIAAAAAAAAAAAAAAAAAAAAAAAAGQATAHNjaGVkdWxlci8uZm9ybWF0X3ZlcnNpb25GQg8AWlpaWlpaWlpaWlpaWlpaMVBLBwi379yDAQAAAAEAAABQSwMEAAAICAAAAAAAAAAAAAAAAAAAAAAAABwANQBzY2hlZHVsZXIvLnN0b3JhZ2VfYWxpZ25tZW50RkIxAFpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlo2NFBLBwg/d3HpAgAAAAIAAABQSwMEAAAICAAAAAAAAAAAAAAAAAAAAAAAABMAPQBzY2hlZHVsZXIvYnl0ZW9yZGVyRkI5AFpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWmxpdHRsZVBLBwiFPeMZBgAAAAYAAABQSwMEAAAICAAAAAAAAAAAAAAAAAAAAAAAABEAOwBzY2hlZHVsZXIvdmVyc2lvbkZCNwBaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaMwpQSwcI0Z5nVQIAAAACAAAAUEsDBAAACAgAAAAAAAAAAAAAAAAAAAAAAAAgADAAc2NoZWR1bGVyLy5kYXRhL3NlcmlhbGl6YXRpb25faWRGQiwAWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlowOTk1ODc1MTc0OTQ5MTkzMjc0MjAwMDk5NDgwMjU3OTIyNjExNjcxUEsHCD8sYqgoAAAAKAAAAFBLAQIAAAAACAgAAAAAAABWJcO25gAAAOYAAAASAAAAAAAAAAAAAAAAAAAAAABzY2hlZHVsZXIvZGF0YS5wa2xQSwECAAAAAAgIAAAAAAAAt+/cgwEAAAABAAAAGQAAAAAAAAAAAAAAAAA2AQAAc2NoZWR1bGVyLy5mb3JtYXRfdmVyc2lvblBLAQIAAAAACAgAAAAAAAA/d3HpAgAAAAIAAAAcAAAAAAAAAAAAAAAAAJEBAABzY2hlZHVsZXIvLnN0b3JhZ2VfYWxpZ25tZW50UEsBAgAAAAAICAAAAAAAAIU94xkGAAAABgAAABMAAAAAAAAAAAAAAAAAEgIAAHNjaGVkdWxlci9ieXRlb3JkZXJQSwECAAAAAAgIAAAAAAAA0Z5nVQIAAAACAAAAEQAAAAAAAAAAAAAAAACWAgAAc2NoZWR1bGVyL3ZlcnNpb25QSwECAAAAAAgIAAAAAAAAPyxiqCgAAAAoAAAAIAAAAAAAAAAAAAAAAAASAwAAc2NoZWR1bGVyLy5kYXRhL3NlcmlhbGl6YXRpb25faWRQSwYGLAAAAAAAAAAeAy0AAAAAAAAAAAAGAAAAAAAAAAYAAAAAAAAAnwEAAAAAAAC4AwAAAAAAAFBLBgcAAAAAVwUAAAAAAAABAAAAUEsFBgAAAAAGAAYAnwEAALgDAAAAAA==",
   "measurements/safe-full/checkpoints/checkpoint-step-000004/state.json": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJzYWZlLWZ1bGwtc3RhdGUtdjEiLAogICJjaGVja3BvaW50X2lkIjogImNoZWNrcG9pbnQtc3RlcC0wMDAwMDQiLAogICJnbG9iYWxfc3RlcCI6IDQsCiAgInByb2ZpbGUiOiB7CiAgICAibmFtZSI6ICJjaSIsCiAgICAiZ2xvYmFsX3NlZWQiOiAyMDI2MDcxNiwKICAgICJzdGVwcyI6IDgsCiAgICAiYmF0Y2hfc2l6ZSI6IDQsCiAgICAic2VxdWVuY2VfbGVuZ3RoIjogOCwKICAgICJ2b2NhYnVsYXJ5X3NpemUiOiAzMiwKICAgICJtb2RlbF93aWR0aCI6IDE2LAogICAgImF0dGVudGlvbl9oZWFkcyI6IDIsCiAgICAidHJhbnNmb3JtZXJfbGF5ZXJzIjogMSwKICAgICJhZGFwdGVyX3dpZHRoIjogNCwKICAgICJkcm9wb3V0IjogMC4yLAogICAgImxlYXJuaW5nX3JhdGUiOiAwLjAxCiAgfSwKICAibG9zc19oaXN0b3J5IjogWwogICAgMy41MzcxOTc1ODk4NzQyNjc2LAogICAgMy40MzQ0NTc1NDA1MTIwODUsCiAgICAzLjU5NzcwNjU1NjMyMDE5MDQsCiAgICAzLjU2MDc0NjY2OTc2OTI4NwogIF0KfQo=",
   "measurements/storage-comparison.json": "ewogICJjaGVja3BvaW50X3N0ZXAiOiA0LAogICJsaW1pdGF0aW9ucyI6IFsKICAgICJUaGUgcmVwYWlyZWQgcmVjdXJyaW5nIHRvdGFsIGV4Y2x1ZGVzIHRoZSBpbW11dGFibGUgYmFzZSBhcnRpZmFjdCBzdG9yZWQgb25jZSBwZXIgcnVuLiIsCiAgICAiTG9naWNhbCBmaWxlIGJ5dGVzIGFyZSBtZWFzdXJlZDsgcGh5c2ljYWwgTkFORCB3cml0ZXMgYW5kIHdyaXRlIGFtcGxpZmljYXRpb24gYXJlIG5vdC4iLAogICAgIlRoZSBzYWZlX2Z1bGwgc291cmNlIGlzIHRoZSB1bmNoYW5nZWQgZGlyZWN0LXJlc3RvcmUgbWVhc3VyZW1lbnQgaW1wbGVtZW50YXRpb24uIgogIF0sCiAgIm1lYXN1cmVtZW50X3Njb3BlIjogImxvZ2ljYWxfY2hlY2twb2ludF9kaXJlY3RvcnlfYnl0ZXMiLAogICJwcm9maWxlIjogImNpIiwKICAicmVwYWlyZWRfb25lX3RpbWVfYmFzZV9ieXRlcyI6IDE4NDc1LAogICJyZXBhaXJlZF9yZWN1cnJpbmdfYnl0ZXMiOiAyNzY4MSwKICAicmVwb3J0ZWRfYWZ0ZXJfcmVjb3ZlcnlfcGFzc2VkIjogdHJ1ZSwKICAic2FmZV9mdWxsX2J5dGVzIjogNDQ5OTgsCiAgInNhZmVfZnVsbF9tZWFzdXJlbWVudF9zb3VyY2UiOiAidW5jaGFuZ2VkX3NhZmVfZnVsbF9kaXJlY3RfcmVzdG9yZV9iYXNlbGluZSIsCiAgInNjaGVtYV92ZXJzaW9uIjogInN0b3JhZ2UtY29tcGFyaXNvbi12MSIsCiAgInN0cnVjdHVyYWxfcmVkdWN0aW9uX2J5dGVzIjogMTczMTcsCiAgInN0cnVjdHVyYWxfcmVkdWN0aW9uX3BlcmNlbnQiOiAzOC40ODM5MzI2MTkyMjc1MjQKfQo=",
   "persistence-contract.json": "eyJhZGFwdGVyIjoibmF0aXZlLXB5dG9yY2giLCJhc3N1bXB0aW9ucyI6WyJDUFUtb25seSBjb250cm9sbGVkIHdvcmtsb2FkIiwiT25seSByZXNpZHVhbC1hZGFwdGVyIHBhcmFtZXRlcnMgYXJlIHRyYWluYWJsZSJdLCJmcmFtZXdvcmsiOiJuYXRpdmUtcHl0b3JjaCIsIml0ZW1zIjpbeyJldmlkZW5jZV9pZHMiOlsicmVzdG9yZTptb2RlbC1zdGF0ZSJdLCJleGFjdG5lc3MiOiJleGFjdCIsImlkZW50aXR5X2NvbnRyb2xzIjpbIm1hbmlmZXN0LWVudHJ5Iiwic2hhMjU2LWNoZWNrc3VtIl0sInJlYXNvbiI6IlRoZSB0cmFpbmFibGUgcmVzaWR1YWwgYWRhcHRlciBtdXN0IHJlc3RvcmUgZXhhY3RseS4iLCJyZWNvdmVyeV9zb3VyY2UiOiJjaGVja3BvaW50IiwicmVxdWlyZW1lbnQiOiJyZXF1aXJlZCIsInN0YXRlX2lkIjoiYWRhcHRlciJ9LHsiZXZpZGVuY2VfaWRzIjpbImJhc2U6cHJlc2VuY2UiLCJiYXNlOnNoYTI1NiJdLCJleGFjdG5lc3MiOiJleGFjdCIsImlkZW50aXR5X2NvbnRyb2xzIjpbImJhc2UtYXJ0aWZhY3QtaWRlbnRpdHkiLCJiYXNlLWFydGlmYWN0LXNoYTI1NiJdLCJyZWFzb24iOiJUaGUgYWRhcHRlciBtdXN0IGJpbmQgdG8gdGhlIGV4YWN0IGltbXV0YWJsZSBmcm96ZW4gYmFzZS4iLCJyZWNvdmVyeV9zb3VyY2UiOiJpbW11dGFibGVfcmVmZXJlbmNlIiwicmVxdWlyZW1lbnQiOiJyZXF1aXJlZCIsInN0YXRlX2lkIjoiYmFzZV9tb2RlbF9pZGVudGl0eSJ9LHsiZXZpZGVuY2VfaWRzIjpbInByb2Nlc3M6bmV4dC1zdGVwIl0sImV4YWN0bmVzcyI6ImV4YWN0IiwiaWRlbnRpdHlfY29udHJvbHMiOlsiZ2xvYmFsLXNlZWQiLCJnbG9iYWwtc3RlcCJdLCJyZWFzb24iOiJUaGUgY29udHJvbGxlZCB3b3JrbG9hZCBkZXJpdmVzIHRoZSBuZXh0IGJhdGNoIGZyb20gc2VlZCBhbmQgZ2xvYmFsIHN0ZXAuIiwicmVjb3Zlcnlfc291cmNlIjoiZGV0ZXJtaW5pc3RpY19yZWNvbXB1dGUiLCJyZXF1aXJlbWVudCI6InJlcXVpcmVkIiwic3RhdGVfaWQiOiJiYXRjaF9wb3NpdGlvbiJ9LHsiZXZpZGVuY2VfaWRzIjpbIm1hbmlmZXN0Omdsb2JhbC1zdGVwIl0sImV4YWN0bmVzcyI6ImV4YWN0IiwiaWRlbnRpdHlfY29udHJvbHMiOlsibWFuaWZlc3QtZW50cnkiLCJzaGEyNTYtY2hlY2tzdW0iXSwicmVhc29uIjoiVGhlIGV4YWN0IGNvbXBsZXRlZC1zdGVwIHBvc2l0aW9uIG11c3QgcmVzdG9yZS4iLCJyZWNvdmVyeV9zb3VyY2UiOiJjaGVja3BvaW50IiwicmVxdWlyZW1lbnQiOiJyZXF1aXJlZCIsInN0YXRlX2lkIjoiZ2xvYmFsX3N0ZXAifSx7ImV2aWRlbmNlX2lkcyI6WyJyZXN0b3JlOm51bXB5LXJuZyJdLCJleGFjdG5lc3MiOiJleGFjdCIsImlkZW50aXR5X2NvbnRyb2xzIjpbIm1hbmlmZXN0LWVudHJ5Iiwic2hhMjU2LWNoZWNrc3VtIl0sInJlYXNvbiI6Ik51bVB5IFJORyBwcm9ncmVzc2lvbiBtdXN0IHJlc3RvcmUgZXhhY3RseS4iLCJyZWNvdmVyeV9zb3VyY2UiOiJjaGVja3BvaW50IiwicmVxdWlyZW1lbnQiOiJyZXF1aXJlZCIsInN0YXRlX2lkIjoibnVtcHlfcm5nIn0seyJldmlkZW5jZV9pZHMiOlsicmVzdG9yZTpvcHRpbWl6ZXItc3RhdGUiXSwiZXhhY3RuZXNzIjoiZXhhY3QiLCJpZGVudGl0eV9jb250cm9scyI6WyJtYW5pZmVzdC1lbnRyeSIsInNoYTI1Ni1jaGVja3N1bSJdLCJyZWFzb24iOiJBZGFtVyBjb250aW51YXRpb24gc3RhdGUgbXVzdCByZXN0b3JlIGV4YWN0bHkuIiwicmVjb3Zlcnlfc291cmNlIjoiY2hlY2twb2ludCIsInJlcXVpcmVtZW50IjoicmVxdWlyZWQiLCJzdGF0ZV9pZCI6Im9wdGltaXplciJ9LHsiZXZpZGVuY2VfaWRzIjpbInJlc3RvcmU6cHl0aG9uLXJuZyJdLCJleGFjdG5lc3MiOiJleGFjdCIsImlkZW50aXR5X2NvbnRyb2xzIjpbIm1hbmlmZXN0LWVudHJ5Iiwic2hhMjU2LWNoZWNrc3VtIl0sInJlYXNvbiI6IlB5dGhvbiBSTkcgcHJvZ3Jlc3Npb24gbXVzdCByZXN0b3JlIGV4YWN0bHkuIiwicmVjb3Zlcnlfc291cmNlIjoiY2hlY2twb2ludCIsInJlcXVpcmVtZW50IjoicmVxdWlyZWQiLCJzdGF0ZV9pZCI6InB5dGhvbl9ybmcifSx7ImV2aWRlbmNlX2lkcyI6WyJyZXN0b3JlOnNjaGVkdWxlci1zdGF0ZSJdLCJleGFjdG5lc3MiOiJleGFjdCIsImlkZW50aXR5X2NvbnRyb2xzIjpbIm1hbmlmZXN0LWVudHJ5Iiwic2hhMjU2LWNoZWNrc3VtIl0sInJlYXNvbiI6IkxpbmVhckxSIGNvbnRpbnVhdGlvbiBzdGF0ZSBtdXN0IHJlc3RvcmUgZXhhY3RseS4iLCJyZWNvdmVyeV9zb3VyY2UiOiJjaGVja3BvaW50IiwicmVxdWlyZW1lbnQiOiJyZXF1aXJlZCIsInN0YXRlX2lkIjoic2NoZWR1bGVyIn0seyJldmlkZW5jZV9pZHMiOlsicmVzdG9yZTp0b3JjaC1ybmciXSwiZXhhY3RuZXNzIjoiZXhhY3QiLCJpZGVudGl0eV9jb250cm9scyI6WyJtYW5pZmVzdC1lbnRyeSIsInNoYTI1Ni1jaGVja3N1bSJdLCJyZWFzb24iOiJUb3JjaCBSTkcgcHJvZ3Jlc3Npb24sIGluY2x1ZGluZyBkcm9wb3V0LCBtdXN0IHJlc3RvcmUgZXhhY3RseS4iLCJyZWNvdmVyeV9zb3VyY2UiOiJjaGVja3BvaW50IiwicmVxdWlyZW1lbnQiOiJyZXF1aXJlZCIsInN0YXRlX2lkIjoidG9yY2hfcm5nIn1dLCJtYXhfcnBvX3N0ZXBzIjowLCJxdWFsaWZpY2F0aW9uX3Byb2ZpbGUiOiJleGFjdC10cmFpbmluZy1yZXN1bWUiLCJzY2hlbWFfdmVyc2lvbiI6ImZsYXNocGlsb3QtcGVyc2lzdGVuY2UtY29udHJhY3QtdjEiLCJ3YXJuaW5ncyI6WyJPbmx5IHRoZSBkZXRlcm1pbmlzdGljIFJlY292ZXJ5IEdhdGUgY2FuIHZlcmlmeSByZWNvdmVyeS4iXX0K",
   "repaired/artifacts/frozen-base/COMPLETE": "bmF0aXZlLXB5dG9yY2g6Y2k6YzE3Y2M4OTk0YzhmMGZlNmRlZjMyNDIzYjBlNWQ5ZWZlZGZmYjNjZDcxYzdkZTk2MzFmMjZjZjUwNTkyNWQ4Ngo=",
   "repaired/artifacts/frozen-base/base.json": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJiYXNlLWFydGlmYWN0LXYxIiwKICAiYWRhcHRlcl9uYW1lIjogIm5hdGl2ZS1weXRvcmNoIiwKICAicHJvZmlsZSI6ICJjaSIsCiAgImFydGlmYWN0IjogewogICAgImlkZW50aXR5IjogIm5hdGl2ZS1weXRvcmNoOmNpOmMxN2NjODk5NGM4ZjBmZTZkZWYzMjQyM2IwZTVkOWVmZWRmZmIzY2Q3MWM3ZGU5NjMxZjI2Y2Y1MDU5MjVkODYiLAogICAgInBhdGgiOiAiYXJ0aWZhY3RzL2Zyb3plbi1iYXNlL2Jhc2UucHQiLAogICAgInNoYTI1NiI6ICJjMTdjYzg5OTRjOGYwZmU2ZGVmMzI0MjNiMGU1ZDllZmVkZmZiM2NkNzFjN2RlOTYzMWYyNmNmNTA1OTI1ZDg2IiwKICAgICJzaXplX2J5dGVzIjogMTg0NzUKICB9Cn0K",
   "repaired/artifacts/frozen-base/base.pt": "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",
   "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/COMPLETE": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJjb21wbGV0aW9uLW1hcmtlci12MSIsCiAgImNoZWNrcG9pbnRfaWQiOiAiY2hlY2twb2ludC1zdGVwLTAwMDAwNCIKfQo=",
   "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/adapter.pt": "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",
   "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/checksums.json": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJjaGVja3N1bXMtdjEiLAogICJmaWxlcyI6IFsKICAgIHsKICAgICAgInBhdGgiOiAiYWRhcHRlci5wdCIsCiAgICAgICJzaGEyNTYiOiAiY2M2NjgxYjIxNWU4MTA2YzM4MDFiNTk1ODJlNTdlMmE2YzczZDk2YTU0Yjk3ZTM5OGVjZThhYTE4Njg1OWJmMSIsCiAgICAgICJzaXplX2J5dGVzIjogMjc4MQogICAgfSwKICAgIHsKICAgICAgInBhdGgiOiAib3B0aW1pemVyLnB0IiwKICAgICAgInNoYTI1NiI6ICJjZTFhNTdmNmI1ZWQxNDRmNWZmZWQwYTczYjI3Y2RhNjZmNDljYWExOWYwNjEyNDk4NGRiYjllZWRhYmY0YmFmIiwKICAgICAgInNpemVfYnl0ZXMiOiA1Nzk1CiAgICB9LAogICAgewogICAgICAicGF0aCI6ICJybmcucHQiLAogICAgICAic2hhMjU2IjogIjcxZWQxODFhODhmOWY0MjUwZmEzNzA4OGFjZTZlNTAyMzA4YjY2ZjcyZGFlM2U0YzA4NTUxNDUxMTYzMGY5N2UiLAogICAgICAic2l6ZV9ieXRlcyI6IDE0Mjg1CiAgICB9LAogICAgewogICAgICAicGF0aCI6ICJzY2hlZHVsZXIucHQiLAogICAgICAic2hhMjU2IjogIjRiMDY3NThkZDhjNTNmNDQ3OWMzN2I3ZTViNWZmN2E1ODUwNDA4ZWM3ZTlhNTE5ZDMwYzU4Y2I4YjYxYTY3NTkiLAogICAgICAic2l6ZV9ieXRlcyI6IDE0NjUKICAgIH0sCiAgICB7CiAgICAgICJwYXRoIjogInN0YXRlLmpzb24iLAogICAgICAic2hhMjU2IjogIjQyZjBmZmQwOWFmZjY4N2M2ZDM2M2U2N2VmZGI2YjQwOTNiYzMwYjVmZWIxOTU1YWM5NGFkNDU1MzUyYjE5YTEiLAogICAgICAic2l6ZV9ieXRlcyI6IDg1NwogICAgfQogIF0KfQo=",
   "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/manifest.json": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJjaGVja3BvaW50LW1hbmlmZXN0LXYxIiwKICAiY2hlY2twb2ludF9pZCI6ICJjaGVja3BvaW50LXN0ZXAtMDAwMDA0IiwKICAic3RyYXRlZ3kiOiAic2FmZV9hZGFwdGVyX2F3YXJlIiwKICAicHJvZmlsZSI6ICJjaSIsCiAgImdsb2JhbF9zdGVwIjogNCwKICAiY3JlYXRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjA4LjgzMzIyNFoiLAogICJzZXJpYWxpemVkX3N0YXRlIjogWwogICAgImFkYXB0ZXIiLAogICAgIm9wdGltaXplciIsCiAgICAic2NoZWR1bGVyIiwKICAgICJnbG9iYWxfc3RlcCIsCiAgICAicHl0aG9uX3JuZyIsCiAgICAibnVtcHlfcm5nIiwKICAgICJ0b3JjaF9ybmciLAogICAgImNvbmZpZyIsCiAgICAiYmFzZV9tb2RlbF9pZGVudGl0eSIKICBdLAogICJvbWl0dGVkX3N0YXRlIjogW10sCiAgImJhc2VfYXJ0aWZhY3QiOiB7CiAgICAiaWRlbnRpdHkiOiAibmF0aXZlLXB5dG9yY2g6Y2k6YzE3Y2M4OTk0YzhmMGZlNmRlZjMyNDIzYjBlNWQ5ZWZlZGZmYjNjZDcxYzdkZTk2MzFmMjZjZjUwNTkyNWQ4NiIsCiAgICAicGF0aCI6ICJhcnRpZmFjdHMvZnJvemVuLWJhc2UvYmFzZS5wdCIsCiAgICAic2hhMjU2IjogImMxN2NjODk5NGM4ZjBmZTZkZWYzMjQyM2IwZTVkOWVmZWRmZmIzY2Q3MWM3ZGU5NjMxZjI2Y2Y1MDU5MjVkODYiLAogICAgInNpemVfYnl0ZXMiOiAxODQ3NQogIH0sCiAgInBheWxvYWRzIjogWwogICAgewogICAgICAicm9sZSI6ICJhZGFwdGVyIiwKICAgICAgInBhdGgiOiAiYWRhcHRlci5wdCIsCiAgICAgICJzaGEyNTYiOiAiY2M2NjgxYjIxNWU4MTA2YzM4MDFiNTk1ODJlNTdlMmE2YzczZDk2YTU0Yjk3ZTM5OGVjZThhYTE4Njg1OWJmMSIsCiAgICAgICJzaXplX2J5dGVzIjogMjc4MQogICAgfSwKICAgIHsKICAgICAgInJvbGUiOiAib3B0aW1pemVyIiwKICAgICAgInBhdGgiOiAib3B0aW1pemVyLnB0IiwKICAgICAgInNoYTI1NiI6ICJjZTFhNTdmNmI1ZWQxNDRmNWZmZWQwYTczYjI3Y2RhNjZmNDljYWExOWYwNjEyNDk4NGRiYjllZWRhYmY0YmFmIiwKICAgICAgInNpemVfYnl0ZXMiOiA1Nzk1CiAgICB9LAogICAgewogICAgICAicm9sZSI6ICJybmciLAogICAgICAicGF0aCI6ICJybmcucHQiLAogICAgICAic2hhMjU2IjogIjcxZWQxODFhODhmOWY0MjUwZmEzNzA4OGFjZTZlNTAyMzA4YjY2ZjcyZGFlM2U0YzA4NTUxNDUxMTYzMGY5N2UiLAogICAgICAic2l6ZV9ieXRlcyI6IDE0Mjg1CiAgICB9LAogICAgewogICAgICAicm9sZSI6ICJzY2hlZHVsZXIiLAogICAgICAicGF0aCI6ICJzY2hlZHVsZXIucHQiLAogICAgICAic2hhMjU2IjogIjRiMDY3NThkZDhjNTNmNDQ3OWMzN2I3ZTViNWZmN2E1ODUwNDA4ZWM3ZTlhNTE5ZDMwYzU4Y2I4YjYxYTY3NTkiLAogICAgICAic2l6ZV9ieXRlcyI6IDE0NjUKICAgIH0sCiAgICB7CiAgICAgICJyb2xlIjogInN0YXRlIiwKICAgICAgInBhdGgiOiAic3RhdGUuanNvbiIsCiAgICAgICJzaGEyNTYiOiAiNDJmMGZmZDA5YWZmNjg3YzZkMzYzZTY3ZWZkYjZiNDA5M2JjMzBiNWZlYjE5NTVhYzk0YWQ0NTUzNTJiMTlhMSIsCiAgICAgICJzaXplX2J5dGVzIjogODU3CiAgICB9CiAgXQp9Cg==",
   "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/optimizer.pt": "UEsDBAAACAgAAAAAAAAAAAAAAAAAAAAAAAASABAAb3B0aW1pemVyL2RhdGEucGtsRkIMAFpaWlpaWlpaWlpaWoACfXEAKFgFAAAAc3RhdGVxAX1xAihLAH1xAyhYBAAAAHN0ZXBxBGN0b3JjaC5fdXRpbHMKX3JlYnVpbGRfdGVuc29yX3YyCnEFKChYBwAAAHN0b3JhZ2VxBmN0b3JjaApGbG9hdFN0b3JhZ2UKcQdYAQAAADBxCFgDAAAAY3B1cQlLAXRxClFLACkpiWNjb2xsZWN0aW9ucwpPcmRlcmVkRGljdApxCylScQx0cQ1ScQ5YBwAAAGV4cF9hdmdxD2gFKChoBmgHWAEAAAAxcRBoCUtAdHERUUsASwRLEIZxEksQSwGGcROJaAspUnEUdHEVUnEWWAoAAABleHBfYXZnX3NxcRdoBSgoaAZoB1gBAAAAMnEYaAlLQHRxGVFLAEsESxCGcRpLEEsBhnEbiWgLKVJxHHRxHVJxHnVLAX1xHyhoBGgFKChoBmgHWAEAAAAzcSBoCUsBdHEhUUsAKSmJaAspUnEidHEjUnEkaA9oBSgoaAZoB1gBAAAANHElaAlLBHRxJlFLAEsEhXEnSwGFcSiJaAspUnEpdHEqUnEraBdoBSgoaAZoB1gBAAAANXEsaAlLBHRxLVFLAEsEhXEuSwGFcS+JaAspUnEwdHExUnEydUsCfXEzKGgEaAUoKGgGaAdYAQAAADZxNGgJSwF0cTVRSwApKYloCylScTZ0cTdScThoD2gFKChoBmgHWAEAAAA3cTloCUtAdHE6UUsASxBLBIZxO0sESwGGcTyJaAspUnE9dHE+UnE/aBdoBSgoaAZoB1gBAAAAOHFAaAlLQHRxQVFLAEsQSwSGcUJLBEsBhnFDiWgLKVJxRHRxRVJxRnVLA31xRyhoBGgFKChoBmgHWAEAAAA5cUhoCUsBdHFJUUsAKSmJaAspUnFKdHFLUnFMaA9oBSgoaAZoB1gCAAAAMTBxTWgJSxB0cU5RSwBLEIVxT0sBhXFQiWgLKVJxUXRxUlJxU2gXaAUoKGgGaAdYAgAAADExcVRoCUsQdHFVUUsASxCFcVZLAYVxV4loCylScVh0cVlScVp1dVgMAAAAcGFyYW1fZ3JvdXBzcVtdcVx9cV0oWAIAAABscnFeRz9+uFHrhR65WAUAAABiZXRhc3FfRz/szMzMzMzNRz/v987ZFocrhnFgWAMAAABlcHNxYUc+RXmO4jCMOlgMAAAAd2VpZ2h0X2RlY2F5cWJHP4R64UeuFHtYBwAAAGFtc2dyYWRxY4lYCAAAAG1heGltaXplcWSJWAcAAABmb3JlYWNocWVOWAoAAABjYXB0dXJhYmxlcWaJWA4AAABkaWZmZXJlbnRpYWJsZXFniVgFAAAAZnVzZWRxaE5YFgAAAGRlY291cGxlZF93ZWlnaHRfZGVjYXlxaYhYCgAAAGluaXRpYWxfbHJxakc/hHrhR64Ue1gGAAAAcGFyYW1zcWtdcWwoSwBLAUsCSwNldWF1LlBLBwiqXOnRRAQAAEQEAABQSwMEAAAICAAAAAAAAAAAAAAAAAAAAAAAABkANQBvcHRpbWl6ZXIvLmZvcm1hdF92ZXJzaW9uRkIxAFpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWloxUEsHCLfv3IMBAAAAAQAAAFBLAwQAAAgIAAAAAAAAAAAAAAAAAAAAAAAAHAA1AG9wdGltaXplci8uc3RvcmFnZV9hbGlnbm1lbnRGQjEAWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWjY0UEsHCD93cekCAAAAAgAAAFBLAwQAAAgIAAAAAAAAAAAAAAAAAAAAAAAAEwA9AG9wdGltaXplci9ieXRlb3JkZXJGQjkAWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpabGl0dGxlUEsHCIU94xkGAAAABgAAAFBLAwQAAAgIAAAAAAAAAAAAAAAAAAAAAAAAEAA8AG9wdGltaXplci9kYXRhLzBGQjgAWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWloAAIBAUEsHCMcGG2wEAAAABAAAAFBLAwQAAAgIAAAAAAAAAAAAAAAAAAAAAAAAEAA+AG9wdGltaXplci9kYXRhLzFGQjoAWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWjF3DDwSs5G5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",
   "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/rng.pt": "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",
   "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/scheduler.pt": "UEsDBAAACAgAAAAAAAAAAAAAAAAAAAAAAAASABAAc2NoZWR1bGVyL2RhdGEucGtsRkIMAFpaWlpaWlpaWlpaWoACfXEAKFgMAAAAc3RhcnRfZmFjdG9ycQFHP/AAAAAAAABYCgAAAGVuZF9mYWN0b3JxAkc/4AAAAAAAAFgLAAAAdG90YWxfaXRlcnNxA0sIWAgAAABiYXNlX2xyc3EEXXEFRz+EeuFHrhR7YVgKAAAAbGFzdF9lcG9jaHEGSwRYCwAAAF9zdGVwX2NvdW50cQdLBVgLAAAAX2lzX2luaXRpYWxxCIlYGgAAAF9nZXRfbHJfY2FsbGVkX3dpdGhpbl9zdGVwcQmJWAgAAABfbGFzdF9scnEKXXELRz9+uFHrhR65YXUuUEsHCFYlw7bmAAAA5gAAAFBLAwQAAAgIAAAAAAAAAAAAAAAAAAAAAAAAGQATAHNjaGVkdWxlci8uZm9ybWF0X3ZlcnNpb25GQg8AWlpaWlpaWlpaWlpaWlpaMVBLBwi379yDAQAAAAEAAABQSwMEAAAICAAAAAAAAAAAAAAAAAAAAAAAABwANQBzY2hlZHVsZXIvLnN0b3JhZ2VfYWxpZ25tZW50RkIxAFpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlo2NFBLBwg/d3HpAgAAAAIAAABQSwMEAAAICAAAAAAAAAAAAAAAAAAAAAAAABMAPQBzY2hlZHVsZXIvYnl0ZW9yZGVyRkI5AFpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWmxpdHRsZVBLBwiFPeMZBgAAAAYAAABQSwMEAAAICAAAAAAAAAAAAAAAAAAAAAAAABEAOwBzY2hlZHVsZXIvdmVyc2lvbkZCNwBaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaMwpQSwcI0Z5nVQIAAAACAAAAUEsDBAAACAgAAAAAAAAAAAAAAAAAAAAAAAAgADAAc2NoZWR1bGVyLy5kYXRhL3NlcmlhbGl6YXRpb25faWRGQiwAWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlpaWlowOTk1ODc1MTc0OTQ5MTkzMjc0MjAwMDk5NDgwMjU3OTIyNjExNjcxUEsHCD8sYqgoAAAAKAAAAFBLAQIAAAAACAgAAAAAAABWJcO25gAAAOYAAAASAAAAAAAAAAAAAAAAAAAAAABzY2hlZHVsZXIvZGF0YS5wa2xQSwECAAAAAAgIAAAAAAAAt+/cgwEAAAABAAAAGQAAAAAAAAAAAAAAAAA2AQAAc2NoZWR1bGVyLy5mb3JtYXRfdmVyc2lvblBLAQIAAAAACAgAAAAAAAA/d3HpAgAAAAIAAAAcAAAAAAAAAAAAAAAAAJEBAABzY2hlZHVsZXIvLnN0b3JhZ2VfYWxpZ25tZW50UEsBAgAAAAAICAAAAAAAAIU94xkGAAAABgAAABMAAAAAAAAAAAAAAAAAEgIAAHNjaGVkdWxlci9ieXRlb3JkZXJQSwECAAAAAAgIAAAAAAAA0Z5nVQIAAAACAAAAEQAAAAAAAAAAAAAAAACWAgAAc2NoZWR1bGVyL3ZlcnNpb25QSwECAAAAAAgIAAAAAAAAPyxiqCgAAAAoAAAAIAAAAAAAAAAAAAAAAAASAwAAc2NoZWR1bGVyLy5kYXRhL3NlcmlhbGl6YXRpb25faWRQSwYGLAAAAAAAAAAeAy0AAAAAAAAAAAAGAAAAAAAAAAYAAAAAAAAAnwEAAAAAAAC4AwAAAAAAAFBLBgcAAAAAVwUAAAAAAAABAAAAUEsFBgAAAAAGAAYAnwEAALgDAAAAAA==",
   "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/state.json": "ewogICJzY2hlbWFfdmVyc2lvbiI6ICJhZGFwdGVyLWNoZWNrcG9pbnQtc3RhdGUtdjEiLAogICJjaGVja3BvaW50X2lkIjogImNoZWNrcG9pbnQtc3RlcC0wMDAwMDQiLAogICJzdHJhdGVneSI6ICJzYWZlX2FkYXB0ZXJfYXdhcmUiLAogICJnbG9iYWxfc3RlcCI6IDQsCiAgInByb2ZpbGUiOiB7CiAgICAibmFtZSI6ICJjaSIsCiAgICAiZ2xvYmFsX3NlZWQiOiAyMDI2MDcxNiwKICAgICJzdGVwcyI6IDgsCiAgICAiYmF0Y2hfc2l6ZSI6IDQsCiAgICAic2VxdWVuY2VfbGVuZ3RoIjogOCwKICAgICJ2b2NhYnVsYXJ5X3NpemUiOiAzMiwKICAgICJtb2RlbF93aWR0aCI6IDE2LAogICAgImF0dGVudGlvbl9oZWFkcyI6IDIsCiAgICAidHJhbnNmb3JtZXJfbGF5ZXJzIjogMSwKICAgICJhZGFwdGVyX3dpZHRoIjogNCwKICAgICJkcm9wb3V0IjogMC4yLAogICAgImxlYXJuaW5nX3JhdGUiOiAwLjAxCiAgfSwKICAibG9zc19oaXN0b3J5IjogWwogICAgMy41MzcxOTc1ODk4NzQyNjc2LAogICAgMy40MzQ0NTc1NDA1MTIwODUsCiAgICAzLjU5NzcwNjU1NjMyMDE5MDQsCiAgICAzLjU2MDc0NjY2OTc2OTI4NwogIF0sCiAgImJhc2VfYXJ0aWZhY3QiOiB7CiAgICAiaWRlbnRpdHkiOiAibmF0aXZlLXB5dG9yY2g6Y2k6YzE3Y2M4OTk0YzhmMGZlNmRlZjMyNDIzYjBlNWQ5ZWZlZGZmYjNjZDcxYzdkZTk2MzFmMjZjZjUwNTkyNWQ4NiIsCiAgICAicGF0aCI6ICJhcnRpZmFjdHMvZnJvemVuLWJhc2UvYmFzZS5wdCIsCiAgICAic2hhMjU2IjogImMxN2NjODk5NGM4ZjBmZTZkZWYzMjQyM2IwZTVkOWVmZWRmZmIzY2Q3MWM3ZGU5NjMxZjI2Y2Y1MDU5MjVkODYiLAogICAgInNpemVfYnl0ZXMiOiAxODQ3NQogIH0KfQo=",
   "repaired/logs/checkpoint-worker.stderr.log": "",
   "repaired/logs/recovery-worker.stderr.log": "",
   "repaired/result.json": "ewogICJjb250cm9sIjogewogICAgImV2YWx1YXRpb25fc2hhMjU2IjogImE0MmE2ZDI1YzhhYWY2Njc0MTMwZWY2MzQzOWY2ZmQ0MTU4MjRiZDIzZmY5Y2Q2YTdjMGNhMDMwNWJlM2VmOWEiLAogICAgImdsb2JhbF9zdGVwIjogOCwKICAgICJsb3NzX2hpc3RvcnkiOiBbCiAgICAgIDMuNTM3MTk3NTg5ODc0MjY3NiwKICAgICAgMy40MzQ0NTc1NDA1MTIwODUsCiAgICAgIDMuNTk3NzA2NTU2MzIwMTkwNCwKICAgICAgMy41NjA3NDY2Njk3NjkyODcsCiAgICAgIDMuNjcwODIzNTc0MDY2MTYyLAogICAgICAzLjYyNzI1MzI5Mzk5MTA4OSwKICAgICAgMy41MDg2MzkzMzU2MzIzMjQsCiAgICAgIDMuODI0ODE0MzE5NjEwNTk1NwogICAgXSwKICAgICJvcHRpbWl6ZXJfc2hhMjU2IjogImMwM2RmYzhiNjZlNjY0NWZiNTUyMjIzNDI4YWQ4NmE4NTVjOTcwNDlkMTMzYjA4OTg0NjA0ZjZlN2Q1NWEwNTAiLAogICAgInNjaGVkdWxlcl9zaGEyNTYiOiAiZTA3ZmZkNmE4OWZlZmI2MWU4MGQxY2E1NjAyNWE5MjcyMjJhODMxODBmZmNlZDc3ODc4OTYwNmQzYTdiZWM4MSIsCiAgICAidHJhaW5hYmxlX3N0YXRlX3NoYTI1NiI6ICIxZmM3MmZkZjIxNDg3YWZlN2IzMmRhODMzZDIzMDBjZDlhNjhmMGMwYzZmM2NlMTQ1NjkxMGE1MTAyYTkyOTk3IgogIH0sCiAgImNyYXNoIjogewogICAgImNoZWNrcG9pbnRfcGF0aCI6ICJjaGVja3BvaW50cy9yZXBhaXJlZC9uYXRpdmUtcmVwYWlyZWQtY29tcGxldGUtdjEvY2hlY2twb2ludC1zdGVwLTAwMDAwNCIsCiAgICAiY2hlY2twb2ludF9zdGVwIjogNCwKICAgICJldmVudF9yZWNlaXZlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjA4LjkyMTg1NloiLAogICAgImxhc3RfY29tcGxldGVkX3N0ZXAiOiA0LAogICAgInRlcm1pbmF0ZWRfYXQiOiAiMjAyNi0wNy0yMFQwMToyOTowOC45NDQyMzlaIiwKICAgICJ0ZXJtaW5hdGlvbl9leGl0X2NvZGUiOiAxLAogICAgInRlcm1pbmF0aW9uX21ldGhvZCI6ICJUZXJtaW5hdGVQcm9jZXNzIHZpYSBzdWJwcm9jZXNzLlBvcGVuLmtpbGwiLAogICAgInRlcm1pbmF0aW9uX3ZlcmlmaWVkIjogdHJ1ZSwKICAgICJ3b3JrZXJfcGlkIjogMjc2MzIKICB9LAogICJjcmVhdGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjk6MTIuOTI1MjQzWiIsCiAgImZhaWx1cmVfYXJ0aWZhY3RfcGF0aCI6IG51bGwsCiAgImdhdGUiOiB7CiAgICAiYWNoaWV2ZWRfcm9sbGJhY2tfc3RlcHMiOiAwLAogICAgImNoZWNrcyI6IFsKICAgICAgewogICAgICAgICJhY3R1YWwiOiAiY2hlY2twb2ludC1tYW5pZmVzdC12MSIsCiAgICAgICAgImNhdGVnb3J5IjogIkludGVncml0eSIsCiAgICAgICAgImNoZWNrX2lkIjogImludGVncml0eS5tYW5pZmVzdF9zY2hlbWEiLAogICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgIm1hbmlmZXN0OnNjaGVtYSIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJjaGVja3BvaW50LW1hbmlmZXN0LXYxIiwKICAgICAgICAibGFiZWwiOiAiTWFuaWZlc3Qgc2NoZW1hIHZhbGlkIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogInByZXNlbnQiLAogICAgICAgICJjYXRlZ29yeSI6ICJJbnRlZ3JpdHkiLAogICAgICAgICJjaGVja19pZCI6ICJpbnRlZ3JpdHkuY29tcGxldGlvbl9tYXJrZXIiLAogICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgImludGVncml0eTpjb21wbGV0aW9uLW1hcmtlciIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJDT01QTEVURSBwcmVzZW50IGluIGZpbmFsIGNoZWNrcG9pbnQiLAogICAgICAgICJsYWJlbCI6ICJDb21wbGV0aW9uIG1hcmtlciBwcmVzZW50IiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogIjUgcGF5bG9hZHMgdmFsaWRhdGVkIiwKICAgICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgICAiY2hlY2tfaWQiOiAiaW50ZWdyaXR5LmNoZWNrc3VtcyIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAiaW50ZWdyaXR5OnNoYTI1NiIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJldmVyeSBtYW5pZmVzdCBwYXlsb2FkIG1hdGNoZXMgU0hBLTI1NiBhbmQgc2l6ZSIsCiAgICAgICAgImxhYmVsIjogIkFsbCBwYXlsb2FkIGNoZWNrc3VtcyB2YWxpZCIsCiAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICJwcmVzZW50IiwKICAgICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgICAiY2hlY2tfaWQiOiAiaW50ZWdyaXR5LmJhc2VfcHJlc2VudCIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAiYmFzZTpwcmVzZW5jZSIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJjb250YWluZWQgaW1tdXRhYmxlIGJhc2UgYXJ0aWZhY3QiLAogICAgICAgICJsYWJlbCI6ICJCYXNlIGFydGlmYWN0IHByZXNlbnQgd2hlbiByZXF1aXJlZCIsCiAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICJjMTdjYzg5OTRjOGYwZmU2ZGVmMzI0MjNiMGU1ZDllZmVkZmZiM2NkNzFjN2RlOTYzMWYyNmNmNTA1OTI1ZDg2IiwKICAgICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgICAiY2hlY2tfaWQiOiAiaW50ZWdyaXR5LmJhc2VfaGFzaCIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAiYmFzZTpzaGEyNTYiCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAiYzE3Y2M4OTk0YzhmMGZlNmRlZjMyNDIzYjBlNWQ5ZWZlZGZmYjNjZDcxYzdkZTk2MzFmMjZjZjUwNTkyNWQ4NiIsCiAgICAgICAgImxhYmVsIjogIkJhc2UgYXJ0aWZhY3QgaGFzaCBtYXRjaGVzIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogIm1hbmlmZXN0PTQsIGV2ZW50PTQsIHJlc3RvcmVkPTQiLAogICAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICAgImNoZWNrX2lkIjogInN0YXRlLmdsb2JhbF9zdGVwIiwKICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJtYW5pZmVzdDpnbG9iYWwtc3RlcCIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICIwIDwgc3RlcCA8IDgsIGNvbnNpc3RlbnQgYWNyb3NzIHJlc3RvcmUiLAogICAgICAgICJsYWJlbCI6ICJDaGVja3BvaW50IGdsb2JhbCBzdGVwIGlzIHZhbGlkIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9VHJ1ZSwgZGlnZXN0X21hdGNoPVRydWUiLAogICAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICAgImNoZWNrX2lkIjogInN0YXRlLm1vZGVsX29yX2FkYXB0ZXIiLAogICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgInJlc3RvcmU6bW9kZWwtc3RhdGUiCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBhZGFwdGVyIGFuZCBleGFjdCB0cmFpbmFibGUtc3RhdGUgZGlnZXN0IiwKICAgICAgICAibGFiZWwiOiAiTW9kZWwgb3IgYWRhcHRlciBzdGF0ZSByZXN0b3JlcyIsCiAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICJzZXJpYWxpemVkPVRydWUsIGRpZ2VzdF9tYXRjaD1UcnVlIiwKICAgICAgICAiY2F0ZWdvcnkiOiAiUmVxdWlyZWQgdHJhaW5pbmcgc3RhdGUiLAogICAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5vcHRpbWl6ZXIiLAogICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgInJlc3RvcmU6b3B0aW1pemVyLXN0YXRlIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogInNlcmlhbGl6ZWQgb3B0aW1pemVyIHdpdGggZXhhY3QgZGlnZXN0IiwKICAgICAgICAibGFiZWwiOiAiT3B0aW1pemVyIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAic2VyaWFsaXplZD1UcnVlLCBkaWdlc3RfbWF0Y2g9VHJ1ZSIsCiAgICAgICAgImNhdGVnb3J5IjogIlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlIiwKICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUuc2NoZWR1bGVyIiwKICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJyZXN0b3JlOnNjaGVkdWxlci1zdGF0ZSIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJzZXJpYWxpemVkIHNjaGVkdWxlciB3aXRoIGV4YWN0IGRpZ2VzdCIsCiAgICAgICAgImxhYmVsIjogIlNjaGVkdWxlciBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9VHJ1ZSwgZGlnZXN0X21hdGNoPVRydWUiLAogICAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICAgImNoZWNrX2lkIjogInN0YXRlLnB5dGhvbl9ybmciLAogICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgInJlc3RvcmU6cHl0aG9uLXJuZyIKICAgICAgICBdLAogICAgICAgICJleHBlY3RlZCI6ICJzZXJpYWxpemVkIHN0YXRlIHdpdGggZXhhY3QgZGlnZXN0IiwKICAgICAgICAibGFiZWwiOiAiUHl0aG9uIFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9VHJ1ZSwgZGlnZXN0X21hdGNoPVRydWUiLAogICAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICAgImNoZWNrX2lkIjogInN0YXRlLm51bXB5X3JuZyIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAicmVzdG9yZTpudW1weS1ybmciCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBzdGF0ZSB3aXRoIGV4YWN0IGRpZ2VzdCIsCiAgICAgICAgImxhYmVsIjogIk51bVB5IFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9VHJ1ZSwgZGlnZXN0X21hdGNoPVRydWUiLAogICAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICAgImNoZWNrX2lkIjogInN0YXRlLnRvcmNoX3JuZyIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAicmVzdG9yZTp0b3JjaC1ybmciCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBzdGF0ZSB3aXRoIGV4YWN0IGRpZ2VzdCIsCiAgICAgICAgImxhYmVsIjogIlRvcmNoIFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogImZpcnN0IGJhdGNoIGF0IDQsIGZpcnN0IGNvbXBsZXRpb24gYXQgNSIsCiAgICAgICAgImNhdGVnb3J5IjogIlByb2Nlc3MgcmVjb3ZlcnkiLAogICAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLm5leHRfc3RlcCIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAicHJvY2VzczpuZXh0LXN0ZXAiCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAiZmlyc3QgYmF0Y2ggYXQgNCwgZmlyc3QgY29tcGxldGlvbiBhdCA1IiwKICAgICAgICAibGFiZWwiOiAiUmVzdW1lZCBydW4gY29udGludWVzIGZyb20gdGhlIGV4cGVjdGVkIG5leHQgc3RlcCIsCiAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICIyNzYzMiIsCiAgICAgICAgImNhdGVnb3J5IjogIlByb2Nlc3MgcmVjb3ZlcnkiLAogICAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLm9yaWdpbmFsX3BpZCIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAicHJvY2VzczpvcmlnaW5hbC1waWQiCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAiMjc2MzIiLAogICAgICAgICJsYWJlbCI6ICJPcmlnaW5hbCB3b3JrZXIgUElEIGlzIHJlY29yZGVkIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogIm1ldGhvZD1UZXJtaW5hdGVQcm9jZXNzIHZpYSBzdWJwcm9jZXNzLlBvcGVuLmtpbGwsIGV4aXQ9MSwgdmVyaWZpZWQ9VHJ1ZSIsCiAgICAgICAgImNhdGVnb3J5IjogIlByb2Nlc3MgcmVjb3ZlcnkiLAogICAgICAgICJjaGVja19pZCI6ICJwcm9jZXNzLmV4cGVjdGVkX3Rlcm1pbmF0aW9uIiwKICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJwcm9jZXNzOnRlcm1pbmF0aW9uIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogInBhcmVudCB0ZXJtaW5hdGlvbiB3aXRoIG5vbnplcm8gZXhpdCBjb2RlIiwKICAgICAgICAibGFiZWwiOiAiT3JpZ2luYWwgd29ya2VyIHRlcm1pbmF0aW9uIGlzIHZlcmlmaWVkIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogIjMxMzk2IiwKICAgICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICAgImNoZWNrX2lkIjogInByb2Nlc3MubmV3X3JlY292ZXJ5X3BpZCIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAicHJvY2VzczpyZWNvdmVyeS1waWQiCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAiUElEIGRpZmZlcmVudCBmcm9tIDI3NjMyIiwKICAgICAgICAibGFiZWwiOiAiUmVjb3ZlcnkgdXNlcyBhIGRpZmZlcmVudCBQSUQiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAiZXhpdD0wLCB2ZXJpZmllZD1UcnVlIiwKICAgICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICAgImNoZWNrX2lkIjogInByb2Nlc3MucmVjb3ZlcnlfZXhpdCIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAicHJvY2VzczpyZWNvdmVyeS1leGl0IgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogImV4aXQgY29kZSAwIiwKICAgICAgICAibGFiZWwiOiAiUmVjb3Zlcnkgd29ya2VyIGV4aXRzIHN1Y2Nlc3NmdWxseSIsCiAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICIwIHN0ZXBzIiwKICAgICAgICAiY2F0ZWdvcnkiOiAiU2FmZXR5IGFuZCByb2xsYmFjayIsCiAgICAgICAgImNoZWNrX2lkIjogInJvbGxiYWNrLmhhcmRfbGltaXQiLAogICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgInJvbGxiYWNrOmFjaGlldmVkIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogIjw9IDAgc3RlcHMiLAogICAgICAgICJsYWJlbCI6ICJBY2hpZXZlZCByb2xsYmFjayBpcyB3aXRoaW4gdGhlIGhhcmQgbGltaXQiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAiZDYwNTcyYWVhMTJmOTE5NjBmM2YwMDMwYmRmZGNhNTVmZGFmZTA1OTE0NmM3MjMwYWY5MDk0OTIzODExZDMxMiIsCiAgICAgICAgImNhdGVnb3J5IjogIlRyYWplY3RvcnkgY29ycmVjdG5lc3MiLAogICAgICAgICJjaGVja19pZCI6ICJ0cmFqZWN0b3J5LmNoZWNrcG9pbnRfZXZhbHVhdGlvbiIsCiAgICAgICAgImRldGFpbHMiOiAiRXhhY3QgU0hBLTI1NiBjb21wYXJpc29uOyBubyBudW1lcmljYWwgdG9sZXJhbmNlIGlzIGFwcGxpZWQuIiwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgInRyYWplY3Rvcnk6Y2hlY2twb2ludC1ldmFsdWF0aW9uIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogImQ2MDU3MmFlYTEyZjkxOTYwZjNmMDAzMGJkZmRjYTU1ZmRhZmUwNTkxNDZjNzIzMGFmOTA5NDkyMzgxMWQzMTIiLAogICAgICAgICJsYWJlbCI6ICJGaXhlZCBldmFsdWF0aW9uIGFmdGVyIHJlc3RvcmUgbWF0Y2hlcyIsCiAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICB9LAogICAgICB7CiAgICAgICAgImFjdHVhbCI6ICIxZmM3MmZkZjIxNDg3YWZlN2IzMmRhODMzZDIzMDBjZDlhNjhmMGMwYzZmM2NlMTQ1NjkxMGE1MTAyYTkyOTk3IiwKICAgICAgICAiY2F0ZWdvcnkiOiAiVHJhamVjdG9yeSBjb3JyZWN0bmVzcyIsCiAgICAgICAgImNoZWNrX2lkIjogInRyYWplY3RvcnkuZmluYWxfdHJhaW5hYmxlIiwKICAgICAgICAiZGV0YWlscyI6ICJFeGFjdCBTSEEtMjU2IGNvbXBhcmlzb247IG5vIG51bWVyaWNhbCB0b2xlcmFuY2UgaXMgYXBwbGllZC4iLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAidHJhamVjdG9yeTpmaW5hbC10cmFpbmFibGUiCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAiMWZjNzJmZGYyMTQ4N2FmZTdiMzJkYTgzM2QyMzAwY2Q5YTY4ZjBjMGM2ZjNjZTE0NTY5MTBhNTEwMmE5Mjk5NyIsCiAgICAgICAgImxhYmVsIjogIkZpbmFsIHRyYWluYWJsZSBwYXJhbWV0ZXJzIG1hdGNoIGNvbnRyb2wiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAiYTQyYTZkMjVjOGFhZjY2NzQxMzBlZjYzNDM5ZjZmZDQxNTgyNGJkMjNmZjljZDZhN2MwY2EwMzA1YmUzZWY5YSIsCiAgICAgICAgImNhdGVnb3J5IjogIlRyYWplY3RvcnkgY29ycmVjdG5lc3MiLAogICAgICAgICJjaGVja19pZCI6ICJ0cmFqZWN0b3J5LmZpbmFsX2V2YWx1YXRpb24iLAogICAgICAgICJkZXRhaWxzIjogIkV4YWN0IFNIQS0yNTYgY29tcGFyaXNvbjsgbm8gbnVtZXJpY2FsIHRvbGVyYW5jZSBpcyBhcHBsaWVkLiIsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJ0cmFqZWN0b3J5OmZpbmFsLWV2YWx1YXRpb24iCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAiYTQyYTZkMjVjOGFhZjY2NzQxMzBlZjYzNDM5ZjZmZDQxNTgyNGJkMjNmZjljZDZhN2MwY2EwMzA1YmUzZWY5YSIsCiAgICAgICAgImxhYmVsIjogIkZpbmFsIGV2YWx1YXRpb24gbG9naXRzIG1hdGNoIGNvbnRyb2wiLAogICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3R1YWwiOiAiZXhhY3QgbWF0Y2giLAogICAgICAgICJjYXRlZ29yeSI6ICJUcmFqZWN0b3J5IGNvcnJlY3RuZXNzIiwKICAgICAgICAiY2hlY2tfaWQiOiAidHJhamVjdG9yeS5sb3NzX2hpc3RvcnkiLAogICAgICAgICJkZXRhaWxzIjogIkV4YWN0IGZsb2F0IHNlcXVlbmNlIGNvbXBhcmlzb247IG5vIG51bWVyaWNhbCB0b2xlcmFuY2UgaXMgYXBwbGllZC4iLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAidHJhamVjdG9yeTpsb3NzLWhpc3RvcnkiCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAiZXhhY3QgbG9zcyBzZXF1ZW5jZSBlcXVhbGl0eSIsCiAgICAgICAgImxhYmVsIjogIkNvbnRpbnVlZCBsb3NzIHRyYWplY3RvcnkgbWF0Y2hlcyBjb250cm9sIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogImNvbnRhaW5lZCIsCiAgICAgICAgImNhdGVnb3J5IjogIlNhZmV0eSBhbmQgcm9sbGJhY2siLAogICAgICAgICJjaGVja19pZCI6ICJzYWZldHkucGF0aF9jb250YWlubWVudCIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAic2FmZXR5OnBhdGgtY29udGFpbm1lbnQiCiAgICAgICAgXSwKICAgICAgICAiZXhwZWN0ZWQiOiAiYWxsIHBhdGhzIGNvbnRhaW5lZDsgc3ltbGluayBlc2NhcGVzIHJlamVjdGVkIiwKICAgICAgICAibGFiZWwiOiAiQWxsIG1hbmFnZWQgd3JpdGUgcGF0aHMgcGFzc2VkIGNvbnRhaW5tZW50IiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0dWFsIjogImNvbXBsZXRlIiwKICAgICAgICAiY2F0ZWdvcnkiOiAiU2FmZXR5IGFuZCByb2xsYmFjayIsCiAgICAgICAgImNoZWNrX2lkIjogImNvbnRyYWN0Lm5vX21hbmRhdG9yeV9vbWlzc2lvbiIsCiAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIgogICAgICAgIF0sCiAgICAgICAgImV4cGVjdGVkIjogImFsbCBtYW5kYXRvcnkgY29udGludWF0aW9uIHN0YXRlIGRlY2xhcmVkIiwKICAgICAgICAibGFiZWwiOiAiTm8gbWFuZGF0b3J5IGNvbnRyYWN0IHJlcXVpcmVtZW50IHdhcyBzaWxlbnRseSBvbWl0dGVkIiwKICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgIH0KICAgIF0sCiAgICAiY29tcGFyaXNvbl9wb2xpY3kiOiB7CiAgICAgICJhdG9sIjogMC4wLAogICAgICAiZXZhbHVhdGlvbl9sb2dpdHMiOiAic2hhMjU2X2V4YWN0IiwKICAgICAgImV2aWRlbmNlIjogIlRoZSBjb250cm9sbGVkIENQVSB3b3JrbG9hZCB1c2VzIGRldGVybWluaXN0aWMgYWxnb3JpdGhtcywgb25lIFRvcmNoIHRocmVhZCwgZml4ZWQgc2VlZHMsIGFuZCBzdGVwLWRlcml2ZWQgYmF0Y2hlcy4gQ3Jvc3MtcHJvY2VzcyBjb21wYXJpc29ucyBmYWlsIG9uIGFueSBkaWdlc3Qgb3IgbG9zcy1zZXF1ZW5jZSBkaWZmZXJlbmNlLiIsCiAgICAgICJsb3NzX2hpc3RvcnkiOiAic2VxdWVuY2VfZXhhY3QiLAogICAgICAibW9kZSI6ICJleGFjdCIsCiAgICAgICJvcHRpbWl6ZXJfc3RhdGUiOiAic2hhMjU2X2V4YWN0IiwKICAgICAgInJuZ19zdGF0ZSI6ICJzaGEyNTZfZXhhY3QiLAogICAgICAicnRvbCI6IDAuMCwKICAgICAgInNjaGVkdWxlcl9zdGF0ZSI6ICJzaGEyNTZfZXhhY3QiLAogICAgICAidHJhaW5hYmxlX3BhcmFtZXRlcnMiOiAic2hhMjU2X2V4YWN0IgogICAgfSwKICAgICJmYWlsZWRfY2hlY2tfaWRzIjogW10sCiAgICAiaGFyZF9yb2xsYmFja19saW1pdF9zdGVwcyI6IDAsCiAgICAicGFzc2VkIjogdHJ1ZSwKICAgICJzY2hlbWFfdmVyc2lvbiI6ICJyZWNvdmVyeS1nYXRlLXYxIgogIH0sCiAgImxpbWl0YXRpb25zIjogWwogICAgIlBoeXNpY2FsIE5BTkQgd3JpdGVzLCB3cml0ZSBhbXBsaWZpY2F0aW9uLCBhbmQgU1NEIGxpZmV0aW1lIHdlcmUgbm90IG1lYXN1cmVkLiIsCiAgICAiTm8gR1BUIHByb3ZpZGVyLCBkaWFnbm9zaXMsIHJlcGFpciBleGVjdXRpb24sIEhUTUwsIG9yIHBhY2thZ2luZyBpcyBwYXJ0IG9mIFByb21wdCAzLiIKICBdLAogICJwbGF0Zm9ybV9zdXBwb3J0X25vdGUiOiAiV2luZG93czogcGF5bG9hZCBhbmQgbWV0YWRhdGEgZmlsZXMgYXJlIGZzeW5jZWQgYW5kIGRpcmVjdG9yeSByZW5hbWUgaXMgYXRvbWljOyBkaXJlY3RvcnkgZnN5bmMgaXMgdW5hdmFpbGFibGUgdGhyb3VnaCBQeXRob24gYW5kIHJlbWFpbnMgYmVzdC1lZmZvcnQuIiwKICAicHJvZmlsZSI6ICJjaSIsCiAgInJlY292ZXJ5IjogewogICAgImFmdGVyX3Jlc3RvcmUiOiB7CiAgICAgICJldmFsdWF0aW9uX3NoYTI1NiI6ICJkNjA1NzJhZWExMmY5MTk2MGYzZjAwMzBiZGZkY2E1NWZkYWZlMDU5MTQ2YzcyMzBhZjkwOTQ5MjM4MTFkMzEyIiwKICAgICAgImdsb2JhbF9zdGVwIjogNCwKICAgICAgImxvc3NfaGlzdG9yeSI6IFsKICAgICAgICAzLjUzNzE5NzU4OTg3NDI2NzYsCiAgICAgICAgMy40MzQ0NTc1NDA1MTIwODUsCiAgICAgICAgMy41OTc3MDY1NTYzMjAxOTA0LAogICAgICAgIDMuNTYwNzQ2NjY5NzY5Mjg3CiAgICAgIF0sCiAgICAgICJvcHRpbWl6ZXJfc2hhMjU2IjogIjlkNzRjMmFiMWQwMDY1YjlhMjcwMDgwY2JhY2QzY2NkZjI5MzdlOGMyYWVlMTEyZDUwMTcxZGVjNDIzYTBhM2EiLAogICAgICAic2NoZWR1bGVyX3NoYTI1NiI6ICJjYWE4MTdmYjMxOTFhYjE0NTZhZGUwMDMyMDU2NWZiM2RmYjdlN2U2NDhhMTIwN2YzZjIyZjA0ODkzZGVjNzcwIiwKICAgICAgInRyYWluYWJsZV9zdGF0ZV9zaGEyNTYiOiAiNDNiYTc1ODA4OTA2OTMyYTAwNWIwZDNlMTg2YjU3ODZhYjY0YTI1ZmRjZTU1NDI2NTVkMmQwOTUxZmM2ZWViNSIKICAgIH0sCiAgICAiYWZ0ZXJfcmVzdG9yZV9ybmciOiB7CiAgICAgICJudW1weV9zaGEyNTYiOiAiYWRjN2U1NDVlYzA1MzBlYWU5ZjFkYTcyNWU4M2Y0OGIxNDZiZDRlYzc5Zjk4NDUxMzY3Y2EzZDE4ZTk5NGRiNSIsCiAgICAgICJweXRob25fc2hhMjU2IjogImRkOGFlYzFjY2YzMDUzZGU2MWVkNmE0NTllMjY2OGMzODViNzk5NmVhZWRkOTQ3NDQ0MDA2MjA5OTk1YTcwNjMiLAogICAgICAidG9yY2hfc2hhMjU2IjogImZhMTYzYzY3YmRjNmJkMzA4ZTczNzk5NzAxZWZmNjAzYjA3ZTYxOTZiMDk3NDhhZjNhMDUxYTE2ZDI1N2NhNjIiCiAgICB9LAogICAgImNoZWNrcG9pbnRfcGF0aCI6ICJjaGVja3BvaW50cy9yZXBhaXJlZC9uYXRpdmUtcmVwYWlyZWQtY29tcGxldGUtdjEvY2hlY2twb2ludC1zdGVwLTAwMDAwNCIsCiAgICAiY29tcGxldGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjk6MTIuNDE4MTA1WiIsCiAgICAiZmluYWwiOiB7CiAgICAgICJldmFsdWF0aW9uX3NoYTI1NiI6ICJhNDJhNmQyNWM4YWFmNjY3NDEzMGVmNjM0MzlmNmZkNDE1ODI0YmQyM2ZmOWNkNmE3YzBjYTAzMDViZTNlZjlhIiwKICAgICAgImdsb2JhbF9zdGVwIjogOCwKICAgICAgImxvc3NfaGlzdG9yeSI6IFsKICAgICAgICAzLjUzNzE5NzU4OTg3NDI2NzYsCiAgICAgICAgMy40MzQ0NTc1NDA1MTIwODUsCiAgICAgICAgMy41OTc3MDY1NTYzMjAxOTA0LAogICAgICAgIDMuNTYwNzQ2NjY5NzY5Mjg3LAogICAgICAgIDMuNjcwODIzNTc0MDY2MTYyLAogICAgICAgIDMuNjI3MjUzMjkzOTkxMDg5LAogICAgICAgIDMuNTA4NjM5MzM1NjMyMzI0LAogICAgICAgIDMuODI0ODE0MzE5NjEwNTk1NwogICAgICBdLAogICAgICAib3B0aW1pemVyX3NoYTI1NiI6ICJjMDNkZmM4YjY2ZTY2NDVmYjU1MjIyMzQyOGFkODZhODU1Yzk3MDQ5ZDEzM2IwODk4NDYwNGY2ZTdkNTVhMDUwIiwKICAgICAgInNjaGVkdWxlcl9zaGEyNTYiOiAiZTA3ZmZkNmE4OWZlZmI2MWU4MGQxY2E1NjAyNWE5MjcyMjJhODMxODBmZmNlZDc3ODc4OTYwNmQzYTdiZWM4MSIsCiAgICAgICJ0cmFpbmFibGVfc3RhdGVfc2hhMjU2IjogIjFmYzcyZmRmMjE0ODdhZmU3YjMyZGE4MzNkMjMwMGNkOWE2OGYwYzBjNmYzY2UxNDU2OTEwYTUxMDJhOTI5OTciCiAgICB9LAogICAgImZpcnN0X2NvbXBsZXRlZF9zdGVwIjogNSwKICAgICJmaXJzdF9yZXN1bWVkX2JhdGNoX3N0ZXAiOiA0LAogICAgInJlc3RvcmVkX2dsb2JhbF9zdGVwIjogNCwKICAgICJzY2hlbWFfdmVyc2lvbiI6ICJyZWNvdmVyeS13b3JrZXItcmVzdWx0LXYxIiwKICAgICJzdGFydGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjk6MTAuOTk4MjE2WiIsCiAgICAic3RyYXRlZ3kiOiAic2FmZV9hZGFwdGVyX2F3YXJlIiwKICAgICJ3b3JrZXJfcGlkIjogMzEzOTYKICB9LAogICJyZWNvdmVyeV9wcm9jZXNzIjogewogICAgImNvbXBsZXRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjEyLjkwOTY5NFoiLAogICAgImV4aXRfY29kZSI6IDAsCiAgICAiZXhpdF92ZXJpZmllZCI6IHRydWUsCiAgICAic3RhcnRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjA4Ljk0NDIzOVoiLAogICAgIndvcmtlcl9waWQiOiAzMTM5NgogIH0sCiAgInJlc3VsdF9wYXRoIjogInJlc3VsdC5qc29uIiwKICAicnVuX2lkIjogInJlcGFpcmVkIiwKICAic2NoZW1hX3ZlcnNpb24iOiAiY3Jhc2gtZXhwZXJpbWVudC12MSIsCiAgInN0cmF0ZWd5IjogInNhZmVfYWRhcHRlcl9hd2FyZSIKfQo=",
   "repaired/strategy/repaired-strategy.json": "ewogICJpbmNsdWRlX251bXB5X3JuZyI6IHRydWUsCiAgImluY2x1ZGVfb3B0aW1pemVyIjogdHJ1ZSwKICAiaW5jbHVkZV9weXRob25fcm5nIjogdHJ1ZSwKICAiaW5jbHVkZV9zY2hlZHVsZXIiOiB0cnVlLAogICJpbmNsdWRlX3RvcmNoX3JuZyI6IHRydWUsCiAgInJlc3RvcmVfYmVmb3JlX25leHRfYmF0Y2giOiB0cnVlLAogICJzY2hlbWFfdmVyc2lvbiI6ICJjaGVja3BvaW50LXN0cmF0ZWd5LWNvbmZpZy12MSIsCiAgInN0cmF0ZWd5X2lkIjogIm5hdGl2ZS1yZXBhaXJlZC1jb21wbGV0ZS12MSIKfQo=",
   "repaired/workers/recovery-result.json": "ewogICJhZnRlcl9yZXN0b3JlIjogewogICAgImV2YWx1YXRpb25fc2hhMjU2IjogImQ2MDU3MmFlYTEyZjkxOTYwZjNmMDAzMGJkZmRjYTU1ZmRhZmUwNTkxNDZjNzIzMGFmOTA5NDkyMzgxMWQzMTIiLAogICAgImdsb2JhbF9zdGVwIjogNCwKICAgICJsb3NzX2hpc3RvcnkiOiBbCiAgICAgIDMuNTM3MTk3NTg5ODc0MjY3NiwKICAgICAgMy40MzQ0NTc1NDA1MTIwODUsCiAgICAgIDMuNTk3NzA2NTU2MzIwMTkwNCwKICAgICAgMy41NjA3NDY2Njk3NjkyODcKICAgIF0sCiAgICAib3B0aW1pemVyX3NoYTI1NiI6ICI5ZDc0YzJhYjFkMDA2NWI5YTI3MDA4MGNiYWNkM2NjZGYyOTM3ZThjMmFlZTExMmQ1MDE3MWRlYzQyM2EwYTNhIiwKICAgICJzY2hlZHVsZXJfc2hhMjU2IjogImNhYTgxN2ZiMzE5MWFiMTQ1NmFkZTAwMzIwNTY1ZmIzZGZiN2U3ZTY0OGExMjA3ZjNmMjJmMDQ4OTNkZWM3NzAiLAogICAgInRyYWluYWJsZV9zdGF0ZV9zaGEyNTYiOiAiNDNiYTc1ODA4OTA2OTMyYTAwNWIwZDNlMTg2YjU3ODZhYjY0YTI1ZmRjZTU1NDI2NTVkMmQwOTUxZmM2ZWViNSIKICB9LAogICJhZnRlcl9yZXN0b3JlX3JuZyI6IHsKICAgICJudW1weV9zaGEyNTYiOiAiYWRjN2U1NDVlYzA1MzBlYWU5ZjFkYTcyNWU4M2Y0OGIxNDZiZDRlYzc5Zjk4NDUxMzY3Y2EzZDE4ZTk5NGRiNSIsCiAgICAicHl0aG9uX3NoYTI1NiI6ICJkZDhhZWMxY2NmMzA1M2RlNjFlZDZhNDU5ZTI2NjhjMzg1Yjc5OTZlYWVkZDk0NzQ0NDAwNjIwOTk5NWE3MDYzIiwKICAgICJ0b3JjaF9zaGEyNTYiOiAiZmExNjNjNjdiZGM2YmQzMDhlNzM3OTk3MDFlZmY2MDNiMDdlNjE5NmIwOTc0OGFmM2EwNTFhMTZkMjU3Y2E2MiIKICB9LAogICJjaGVja3BvaW50X3BhdGgiOiAiY2hlY2twb2ludHMvcmVwYWlyZWQvbmF0aXZlLXJlcGFpcmVkLWNvbXBsZXRlLXYxL2NoZWNrcG9pbnQtc3RlcC0wMDAwMDQiLAogICJjb21wbGV0ZWRfYXQiOiAiMjAyNi0wNy0yMFQwMToyOToxMi40MTgxMDVaIiwKICAiZmluYWwiOiB7CiAgICAiZXZhbHVhdGlvbl9zaGEyNTYiOiAiYTQyYTZkMjVjOGFhZjY2NzQxMzBlZjYzNDM5ZjZmZDQxNTgyNGJkMjNmZjljZDZhN2MwY2EwMzA1YmUzZWY5YSIsCiAgICAiZ2xvYmFsX3N0ZXAiOiA4LAogICAgImxvc3NfaGlzdG9yeSI6IFsKICAgICAgMy41MzcxOTc1ODk4NzQyNjc2LAogICAgICAzLjQzNDQ1NzU0MDUxMjA4NSwKICAgICAgMy41OTc3MDY1NTYzMjAxOTA0LAogICAgICAzLjU2MDc0NjY2OTc2OTI4NywKICAgICAgMy42NzA4MjM1NzQwNjYxNjIsCiAgICAgIDMuNjI3MjUzMjkzOTkxMDg5LAogICAgICAzLjUwODYzOTMzNTYzMjMyNCwKICAgICAgMy44MjQ4MTQzMTk2MTA1OTU3CiAgICBdLAogICAgIm9wdGltaXplcl9zaGEyNTYiOiAiYzAzZGZjOGI2NmU2NjQ1ZmI1NTIyMjM0MjhhZDg2YTg1NWM5NzA0OWQxMzNiMDg5ODQ2MDRmNmU3ZDU1YTA1MCIsCiAgICAic2NoZWR1bGVyX3NoYTI1NiI6ICJlMDdmZmQ2YTg5ZmVmYjYxZTgwZDFjYTU2MDI1YTkyNzIyMmE4MzE4MGZmY2VkNzc4Nzg5NjA2ZDNhN2JlYzgxIiwKICAgICJ0cmFpbmFibGVfc3RhdGVfc2hhMjU2IjogIjFmYzcyZmRmMjE0ODdhZmU3YjMyZGE4MzNkMjMwMGNkOWE2OGYwYzBjNmYzY2UxNDU2OTEwYTUxMDJhOTI5OTciCiAgfSwKICAiZmlyc3RfY29tcGxldGVkX3N0ZXAiOiA1LAogICJmaXJzdF9yZXN1bWVkX2JhdGNoX3N0ZXAiOiA0LAogICJyZXN0b3JlZF9nbG9iYWxfc3RlcCI6IDQsCiAgInNjaGVtYV92ZXJzaW9uIjogInJlY292ZXJ5LXdvcmtlci1yZXN1bHQtdjEiLAogICJzdGFydGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjk6MTAuOTk4MjE2WiIsCiAgInN0cmF0ZWd5IjogInNhZmVfYWRhcHRlcl9hd2FyZSIsCiAgIndvcmtlcl9waWQiOiAzMTM5Ngp9Cg==",
   "report.html": "PCFkb2N0eXBlIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KPGhlYWQ+CjxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KPG1ldGEgbmFtZT0idmlld3BvcnQiIGNvbnRlbnQ9IndpZHRoPWRldmljZS13aWR0aCwgaW5pdGlhbC1zY2FsZT0xIj4KPHRpdGxlPkZsYXNoUGlsb3QgYm91bmRlZCByZXBhaXIgcmVwb3J0PC90aXRsZT4KPHN0eWxlPgo6cm9vdCB7IGNvbG9yLXNjaGVtZTogZGFyazsgLS1iZzojMGIxMDIwOyAtLWNhcmQ6IzEyMWEyZjsgLS10ZXh0OiNlOGVkZjg7Ci0tbXV0ZWQ6IzljYTljNjsgLS1wYXNzOiM0NmQxN2Q7IC0tZmFpbDojZmY2NTc3OyAtLXdhcm46I2Y2Yzg1ZjsgLS1pbmZvOiM3MWI3ZmY7IH0KKiB7IGJveC1zaXppbmc6Ym9yZGVyLWJveDsgfSBib2R5IHsgbWFyZ2luOjA7IGJhY2tncm91bmQ6dmFyKC0tYmcpOyBjb2xvcjp2YXIoLS10ZXh0KTsKZm9udDoxNnB4LzEuNSBzeXN0ZW0tdWksc2Fucy1zZXJpZjsgfSBtYWluIHsgbWF4LXdpZHRoOjExMDBweDsgbWFyZ2luOmF1dG87IHBhZGRpbmc6MzJweCAyMHB4OyB9CnNlY3Rpb24geyBiYWNrZ3JvdW5kOnZhcigtLWNhcmQpOyBib3JkZXI6MXB4IHNvbGlkICMyNjMzNTE7IGJvcmRlci1yYWRpdXM6MTJweDsKcGFkZGluZzoyMHB4OyBtYXJnaW46MThweCAwOyB9IGgxLGgyIHsgbWFyZ2luLXRvcDowOyB9IC5leWVicm93IHsgY29sb3I6dmFyKC0taW5mbyk7CmZvbnQtd2VpZ2h0OjcwMDsgbGV0dGVyLXNwYWNpbmc6LjA4ZW07IHRleHQtdHJhbnNmb3JtOnVwcGVyY2FzZTsgfSAudmVyaWZpZWQsLnBhc3MgeyBjb2xvcjp2YXIoLS1wYXNzKTsgfQouZmFpbCB7IGNvbG9yOnZhcigtLWZhaWwpOyB9IC51bnN1cHBvcnRlZCB7IGNvbG9yOnZhcigtLXdhcm4pOyB9IC5hY2NlcHRlZCB7IGNvbG9yOnZhcigtLWluZm8pOyB9Ci5oZWFkbGluZSB7IGZvbnQtc2l6ZToxLjZyZW07IGZvbnQtd2VpZ2h0OjgwMDsgfSB0YWJsZSB7IGJvcmRlci1jb2xsYXBzZTpjb2xsYXBzZTsgd2lkdGg6MTAwJTsgfQp0aCx0ZCB7IGJvcmRlci1ib3R0b206MXB4IHNvbGlkICMyYjM4NTg7IHBhZGRpbmc6MTBweDsgdGV4dC1hbGlnbjpsZWZ0OyB2ZXJ0aWNhbC1hbGlnbjp0b3A7IH0KY29kZSB7IGNvbG9yOiNjOWQ3ZmY7IH0gZGwgeyBkaXNwbGF5OmdyaWQ7IGdyaWQtdGVtcGxhdGUtY29sdW1uczoyZnIgMWZyOyBnYXA6OHB4IDE4cHg7IH0KZHQgeyBjb2xvcjp2YXIoLS1tdXRlZCk7IH0gZGQgeyBtYXJnaW46MDsgZm9udC13ZWlnaHQ6NzAwOyB9IC5kaXNjbGFpbWVyIHsgY29sb3I6dmFyKC0td2Fybik7IH0KPC9zdHlsZT4KPC9oZWFkPgo8Ym9keT48bWFpbj4KPHAgY2xhc3M9ImV5ZWJyb3ciPkNoZWNrcG9pbnQgcmVjb3ZlcnkgcXVhbGlmaWNhdGlvbiBhbmQgdmVyaWZpY2F0aW9uIGhhcm5lc3M8L3A+CjxoMT5GbGFzaFBpbG90IGJvdW5kZWQgcmVwYWlyIHJlcG9ydDwvaDE+CjxwPkZpbmFsIHZlcmRpY3Q6IDxzdHJvbmcgY2xhc3M9InZlcmlmaWVkIj4KVkVSSUZJRUQ8L3N0cm9uZz4uIE9ubHkgdGhlIGRldGVybWluaXN0aWMgUmVjb3ZlcnkgR2F0ZSBzZXRzIHRoaXMgdmVyZGljdC48L3A+CjxzZWN0aW9uPjxoMj5Jbml0aWFsIGRlc2lnbmVkIGZhaWx1cmU8L2gyPgo8cD5Xb3JrZXIgUElEIDMxNDEyIHdhcyB0ZXJtaW5hdGVkOyByZWNvdmVyeSB1c2VkIFBJRAoxNjYwMC4gVGhlIHZhbGlkIGNoZWNrcG9pbnQgbG9hZGVkIGFuZCB0aGUgZ2F0ZSBmYWlsZWQ6PC9wPgo8dWw+PGxpPjxjb2RlPnN0YXRlLm9wdGltaXplcjwvY29kZT48L2xpPjxsaT48Y29kZT5zdGF0ZS5zY2hlZHVsZXI8L2NvZGU+PC9saT48bGk+PGNvZGU+c3RhdGUucHl0aG9uX3JuZzwvY29kZT48L2xpPjxsaT48Y29kZT5zdGF0ZS5udW1weV9ybmc8L2NvZGU+PC9saT48bGk+PGNvZGU+c3RhdGUudG9yY2hfcm5nPC9jb2RlPjwvbGk+PGxpPjxjb2RlPnRyYWplY3RvcnkuZmluYWxfdHJhaW5hYmxlPC9jb2RlPjwvbGk+PGxpPjxjb2RlPnRyYWplY3RvcnkuZmluYWxfZXZhbHVhdGlvbjwvY29kZT48L2xpPjxsaT48Y29kZT50cmFqZWN0b3J5Lmxvc3NfaGlzdG9yeTwvY29kZT48L2xpPjxsaT48Y29kZT5jb250cmFjdC5ub19tYW5kYXRvcnlfb21pc3Npb248L2NvZGU+PC9saT48L3VsPjwvc2VjdGlvbj4KPHNlY3Rpb24+PGgyPkdQVC01LjYgY2FwdHVyZWQtcmVzcG9uc2UgZml4dHVyZS9yZXBsYXk8L2gyPgo8cD48c3Ryb25nPkdQVCBzb3VyY2U6PC9zdHJvbmc+IEdQVC01LjYgY2FwdHVyZWQtcmVzcG9uc2UgZml4dHVyZS9yZXBsYXk8L3A+CjxwPlRoZSByZWNvbW1lbmRhdGlvbiBpcyBldmlkZW5jZS1ib3VuZGVkIGFuZCBjYW5ub3QgZGVjbGFyZSByZWNvdmVyeSBvciBleGVjdXRlIGNoYW5nZXMuPC9wPgo8dGFibGU+PHRoZWFkPjx0cj48dGg+UHJvcG9zZWQgYWN0aW9uPC90aD48dGg+R3VhcmRyYWlsIGRlY2lzaW9uPC90aD48dGg+UmVhc29uPC90aD48L3RyPjwvdGhlYWQ+Cjx0Ym9keT48dHI+PHRkPjxjb2RlPmNoYW5nZV9zdXBwb3J0ZWRfY2hlY2twb2ludF9zdHJhdGVneTwvY29kZT48L3RkPjx0ZCBjbGFzcz0idW5zdXBwb3J0ZWQiPlVOU1VQUE9SVEVEPC90ZD48dGQ+S25vd24gYWN0aW9uIGlzIHVuc3VwcG9ydGVkIGJ5IE5hdGl2ZVB5VG9yY2hBZGFwdGVyIGluIFAwLjwvdGQ+PC90cj48dHI+PHRkPjxjb2RlPnBlcnNpc3Rfb3B0aW1pemVyX3N0YXRlPC9jb2RlPjwvdGQ+PHRkIGNsYXNzPSJhY2NlcHRlZCI+QUNDRVBURUQ8L3RkPjx0ZD5UeXBlZCBhY3Rpb24gaXMgc3VwcG9ydGVkIGFuZCBsaW5rZWQgdG8gcmVxdWVzdCBldmlkZW5jZS48L3RkPjwvdHI+PHRyPjx0ZD48Y29kZT5wZXJzaXN0X3NjaGVkdWxlcl9zdGF0ZTwvY29kZT48L3RkPjx0ZCBjbGFzcz0iYWNjZXB0ZWQiPkFDQ0VQVEVEPC90ZD48dGQ+VHlwZWQgYWN0aW9uIGlzIHN1cHBvcnRlZCBhbmQgbGlua2VkIHRvIHJlcXVlc3QgZXZpZGVuY2UuPC90ZD48L3RyPjx0cj48dGQ+PGNvZGU+cGVyc2lzdF9weXRob25fcm5nX3N0YXRlPC9jb2RlPjwvdGQ+PHRkIGNsYXNzPSJhY2NlcHRlZCI+QUNDRVBURUQ8L3RkPjx0ZD5UeXBlZCBhY3Rpb24gaXMgc3VwcG9ydGVkIGFuZCBsaW5rZWQgdG8gcmVxdWVzdCBldmlkZW5jZS48L3RkPjwvdHI+PHRyPjx0ZD48Y29kZT5wZXJzaXN0X251bXB5X3JuZ19zdGF0ZTwvY29kZT48L3RkPjx0ZCBjbGFzcz0iYWNjZXB0ZWQiPkFDQ0VQVEVEPC90ZD48dGQ+VHlwZWQgYWN0aW9uIGlzIHN1cHBvcnRlZCBhbmQgbGlua2VkIHRvIHJlcXVlc3QgZXZpZGVuY2UuPC90ZD48L3RyPjx0cj48dGQ+PGNvZGU+cGVyc2lzdF90b3JjaF9ybmdfc3RhdGU8L2NvZGU+PC90ZD48dGQgY2xhc3M9ImFjY2VwdGVkIj5BQ0NFUFRFRDwvdGQ+PHRkPlR5cGVkIGFjdGlvbiBpcyBzdXBwb3J0ZWQgYW5kIGxpbmtlZCB0byByZXF1ZXN0IGV2aWRlbmNlLjwvdGQ+PC90cj48dHI+PHRkPjxjb2RlPnJlc3RvcmVfc3RhdGVfYmVmb3JlX25leHRfYmF0Y2g8L2NvZGU+PC90ZD48dGQgY2xhc3M9ImFjY2VwdGVkIj5BQ0NFUFRFRDwvdGQ+PHRkPlR5cGVkIGFjdGlvbiBpcyBzdXBwb3J0ZWQgYW5kIGxpbmtlZCB0byByZXF1ZXN0IGV2aWRlbmNlLjwvdGQ+PC90cj48L3Rib2R5PjwvdGFibGU+PC9zZWN0aW9uPgo8c2VjdGlvbj48aDI+RGV0ZXJtaW5pc3RpYyBib3VuZGVkIHJlcGFpcjwvaDI+CjxwPkF0dGVtcHQgMSBjcmVhdGVkIHN0cmF0ZWd5Cjxjb2RlPm5hdGl2ZS1yZXBhaXJlZC1jb21wbGV0ZS12MTwvY29kZT4gd2l0aG91dCBtb2RpZnlpbmcgdGhlCmhpc3RvcmljYWwgZmFpbGVkIGNoZWNrcG9pbnQuPC9wPjwvc2VjdGlvbj4KPHNlY3Rpb24+PGgyPkZpbmFsIFJlY292ZXJ5IEdhdGU8L2gyPgo8cD5Xb3JrZXIgUElEIDI3NjMyIHdhcyB0ZXJtaW5hdGVkOyByZWNvdmVyeSB1c2VkIFBJRAozMTM5Ni4gQ29tcGFyaXNvbiByZW1haW5lZCBleGFjdCBhdAphdG9sPTAuMCwKcnRvbD0wLjAuPC9wPgo8dGFibGU+PHRoZWFkPjx0cj48dGg+Q2F0ZWdvcnk8L3RoPjx0aD5DaGVjayBJRDwvdGg+PHRoPlN0YXR1czwvdGg+PHRoPkNoZWNrPC90aD48L3RyPjwvdGhlYWQ+Cjx0Ym9keT48dHI+PHRkPkludGVncml0eTwvdGQ+PHRkPjxjb2RlPmludGVncml0eS5tYW5pZmVzdF9zY2hlbWE8L2NvZGU+PC90ZD48dGQgY2xhc3M9InBhc3MiPlBBU1M8L3RkPjx0ZD5NYW5pZmVzdCBzY2hlbWEgdmFsaWQ8L3RkPjwvdHI+PHRyPjx0ZD5JbnRlZ3JpdHk8L3RkPjx0ZD48Y29kZT5pbnRlZ3JpdHkuY29tcGxldGlvbl9tYXJrZXI8L2NvZGU+PC90ZD48dGQgY2xhc3M9InBhc3MiPlBBU1M8L3RkPjx0ZD5Db21wbGV0aW9uIG1hcmtlciBwcmVzZW50PC90ZD48L3RyPjx0cj48dGQ+SW50ZWdyaXR5PC90ZD48dGQ+PGNvZGU+aW50ZWdyaXR5LmNoZWNrc3VtczwvY29kZT48L3RkPjx0ZCBjbGFzcz0icGFzcyI+UEFTUzwvdGQ+PHRkPkFsbCBwYXlsb2FkIGNoZWNrc3VtcyB2YWxpZDwvdGQ+PC90cj48dHI+PHRkPkludGVncml0eTwvdGQ+PHRkPjxjb2RlPmludGVncml0eS5iYXNlX3ByZXNlbnQ8L2NvZGU+PC90ZD48dGQgY2xhc3M9InBhc3MiPlBBU1M8L3RkPjx0ZD5CYXNlIGFydGlmYWN0IHByZXNlbnQgd2hlbiByZXF1aXJlZDwvdGQ+PC90cj48dHI+PHRkPkludGVncml0eTwvdGQ+PHRkPjxjb2RlPmludGVncml0eS5iYXNlX2hhc2g8L2NvZGU+PC90ZD48dGQgY2xhc3M9InBhc3MiPlBBU1M8L3RkPjx0ZD5CYXNlIGFydGlmYWN0IGhhc2ggbWF0Y2hlczwvdGQ+PC90cj48dHI+PHRkPlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlPC90ZD48dGQ+PGNvZGU+c3RhdGUuZ2xvYmFsX3N0ZXA8L2NvZGU+PC90ZD48dGQgY2xhc3M9InBhc3MiPlBBU1M8L3RkPjx0ZD5DaGVja3BvaW50IGdsb2JhbCBzdGVwIGlzIHZhbGlkPC90ZD48L3RyPjx0cj48dGQ+UmVxdWlyZWQgdHJhaW5pbmcgc3RhdGU8L3RkPjx0ZD48Y29kZT5zdGF0ZS5tb2RlbF9vcl9hZGFwdGVyPC9jb2RlPjwvdGQ+PHRkIGNsYXNzPSJwYXNzIj5QQVNTPC90ZD48dGQ+TW9kZWwgb3IgYWRhcHRlciBzdGF0ZSByZXN0b3JlczwvdGQ+PC90cj48dHI+PHRkPlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlPC90ZD48dGQ+PGNvZGU+c3RhdGUub3B0aW1pemVyPC9jb2RlPjwvdGQ+PHRkIGNsYXNzPSJwYXNzIj5QQVNTPC90ZD48dGQ+T3B0aW1pemVyIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQ8L3RkPjwvdHI+PHRyPjx0ZD5SZXF1aXJlZCB0cmFpbmluZyBzdGF0ZTwvdGQ+PHRkPjxjb2RlPnN0YXRlLnNjaGVkdWxlcjwvY29kZT48L3RkPjx0ZCBjbGFzcz0icGFzcyI+UEFTUzwvdGQ+PHRkPlNjaGVkdWxlciBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkPC90ZD48L3RyPjx0cj48dGQ+UmVxdWlyZWQgdHJhaW5pbmcgc3RhdGU8L3RkPjx0ZD48Y29kZT5zdGF0ZS5weXRob25fcm5nPC9jb2RlPjwvdGQ+PHRkIGNsYXNzPSJwYXNzIj5QQVNTPC90ZD48dGQ+UHl0aG9uIFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkPC90ZD48L3RyPjx0cj48dGQ+UmVxdWlyZWQgdHJhaW5pbmcgc3RhdGU8L3RkPjx0ZD48Y29kZT5zdGF0ZS5udW1weV9ybmc8L2NvZGU+PC90ZD48dGQgY2xhc3M9InBhc3MiPlBBU1M8L3RkPjx0ZD5OdW1QeSBSTkcgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZDwvdGQ+PC90cj48dHI+PHRkPlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlPC90ZD48dGQ+PGNvZGU+c3RhdGUudG9yY2hfcm5nPC9jb2RlPjwvdGQ+PHRkIGNsYXNzPSJwYXNzIj5QQVNTPC90ZD48dGQ+VG9yY2ggUk5HIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQ8L3RkPjwvdHI+PHRyPjx0ZD5Qcm9jZXNzIHJlY292ZXJ5PC90ZD48dGQ+PGNvZGU+cHJvY2Vzcy5uZXh0X3N0ZXA8L2NvZGU+PC90ZD48dGQgY2xhc3M9InBhc3MiPlBBU1M8L3RkPjx0ZD5SZXN1bWVkIHJ1biBjb250aW51ZXMgZnJvbSB0aGUgZXhwZWN0ZWQgbmV4dCBzdGVwPC90ZD48L3RyPjx0cj48dGQ+UHJvY2VzcyByZWNvdmVyeTwvdGQ+PHRkPjxjb2RlPnByb2Nlc3Mub3JpZ2luYWxfcGlkPC9jb2RlPjwvdGQ+PHRkIGNsYXNzPSJwYXNzIj5QQVNTPC90ZD48dGQ+T3JpZ2luYWwgd29ya2VyIFBJRCBpcyByZWNvcmRlZDwvdGQ+PC90cj48dHI+PHRkPlByb2Nlc3MgcmVjb3Zlcnk8L3RkPjx0ZD48Y29kZT5wcm9jZXNzLmV4cGVjdGVkX3Rlcm1pbmF0aW9uPC9jb2RlPjwvdGQ+PHRkIGNsYXNzPSJwYXNzIj5QQVNTPC90ZD48dGQ+T3JpZ2luYWwgd29ya2VyIHRlcm1pbmF0aW9uIGlzIHZlcmlmaWVkPC90ZD48L3RyPjx0cj48dGQ+UHJvY2VzcyByZWNvdmVyeTwvdGQ+PHRkPjxjb2RlPnByb2Nlc3MubmV3X3JlY292ZXJ5X3BpZDwvY29kZT48L3RkPjx0ZCBjbGFzcz0icGFzcyI+UEFTUzwvdGQ+PHRkPlJlY292ZXJ5IHVzZXMgYSBkaWZmZXJlbnQgUElEPC90ZD48L3RyPjx0cj48dGQ+UHJvY2VzcyByZWNvdmVyeTwvdGQ+PHRkPjxjb2RlPnByb2Nlc3MucmVjb3ZlcnlfZXhpdDwvY29kZT48L3RkPjx0ZCBjbGFzcz0icGFzcyI+UEFTUzwvdGQ+PHRkPlJlY292ZXJ5IHdvcmtlciBleGl0cyBzdWNjZXNzZnVsbHk8L3RkPjwvdHI+PHRyPjx0ZD5TYWZldHkgYW5kIHJvbGxiYWNrPC90ZD48dGQ+PGNvZGU+cm9sbGJhY2suaGFyZF9saW1pdDwvY29kZT48L3RkPjx0ZCBjbGFzcz0icGFzcyI+UEFTUzwvdGQ+PHRkPkFjaGlldmVkIHJvbGxiYWNrIGlzIHdpdGhpbiB0aGUgaGFyZCBsaW1pdDwvdGQ+PC90cj48dHI+PHRkPlRyYWplY3RvcnkgY29ycmVjdG5lc3M8L3RkPjx0ZD48Y29kZT50cmFqZWN0b3J5LmNoZWNrcG9pbnRfZXZhbHVhdGlvbjwvY29kZT48L3RkPjx0ZCBjbGFzcz0icGFzcyI+UEFTUzwvdGQ+PHRkPkZpeGVkIGV2YWx1YXRpb24gYWZ0ZXIgcmVzdG9yZSBtYXRjaGVzPC90ZD48L3RyPjx0cj48dGQ+VHJhamVjdG9yeSBjb3JyZWN0bmVzczwvdGQ+PHRkPjxjb2RlPnRyYWplY3RvcnkuZmluYWxfdHJhaW5hYmxlPC9jb2RlPjwvdGQ+PHRkIGNsYXNzPSJwYXNzIj5QQVNTPC90ZD48dGQ+RmluYWwgdHJhaW5hYmxlIHBhcmFtZXRlcnMgbWF0Y2ggY29udHJvbDwvdGQ+PC90cj48dHI+PHRkPlRyYWplY3RvcnkgY29ycmVjdG5lc3M8L3RkPjx0ZD48Y29kZT50cmFqZWN0b3J5LmZpbmFsX2V2YWx1YXRpb248L2NvZGU+PC90ZD48dGQgY2xhc3M9InBhc3MiPlBBU1M8L3RkPjx0ZD5GaW5hbCBldmFsdWF0aW9uIGxvZ2l0cyBtYXRjaCBjb250cm9sPC90ZD48L3RyPjx0cj48dGQ+VHJhamVjdG9yeSBjb3JyZWN0bmVzczwvdGQ+PHRkPjxjb2RlPnRyYWplY3RvcnkubG9zc19oaXN0b3J5PC9jb2RlPjwvdGQ+PHRkIGNsYXNzPSJwYXNzIj5QQVNTPC90ZD48dGQ+Q29udGludWVkIGxvc3MgdHJhamVjdG9yeSBtYXRjaGVzIGNvbnRyb2w8L3RkPjwvdHI+PHRyPjx0ZD5TYWZldHkgYW5kIHJvbGxiYWNrPC90ZD48dGQ+PGNvZGU+c2FmZXR5LnBhdGhfY29udGFpbm1lbnQ8L2NvZGU+PC90ZD48dGQgY2xhc3M9InBhc3MiPlBBU1M8L3RkPjx0ZD5BbGwgbWFuYWdlZCB3cml0ZSBwYXRocyBwYXNzZWQgY29udGFpbm1lbnQ8L3RkPjwvdHI+PHRyPjx0ZD5TYWZldHkgYW5kIHJvbGxiYWNrPC90ZD48dGQ+PGNvZGU+Y29udHJhY3Qubm9fbWFuZGF0b3J5X29taXNzaW9uPC9jb2RlPjwvdGQ+PHRkIGNsYXNzPSJwYXNzIj5QQVNTPC90ZD48dGQ+Tm8gbWFuZGF0b3J5IGNvbnRyYWN0IHJlcXVpcmVtZW50IHdhcyBzaWxlbnRseSBvbWl0dGVkPC90ZD48L3RyPjwvdGJvZHk+PC90YWJsZT48L3NlY3Rpb24+CjxzZWN0aW9uPjxoMj5WZXJpZmllZCBzdG9yYWdlIGNvbXBhcmlzb248L2gyPjxwIGNsYXNzPSJ2ZXJpZmllZCBoZWFkbGluZSI+MTcsMzE3IGZld2VyIHJlY3VycmluZyBsb2dpY2FsIGJ5dGVzICgzOC40OCUpPC9wPjxkbD48ZHQ+c2FmZV9mdWxsIHJlY3VycmluZyBsb2dpY2FsIGJ5dGVzPC9kdD48ZGQ+NDQsOTk4PC9kZD48ZHQ+UmVwYWlyZWQgcmVjdXJyaW5nIGxvZ2ljYWwgYnl0ZXM8L2R0PjxkZD4yNyw2ODE8L2RkPjxkdD5PbmUtdGltZSBmcm96ZW4tYmFzZSBjb3N0PC9kdD48ZGQ+MTgsNDc1PC9kZD48L2RsPjxwPlRoZSBmaXJzdCBhZGFwdGVyLWF3YXJlIHdyaXRlIGlzIG5vdCBwcmVzZW50ZWQgYXMgc2F2aW5nczsgdGhlIGltbXV0YWJsZSBiYXNlIGlzIGEgc2VwYXJhdGUgb25lLXRpbWUgY29zdC48L3A+PC9zZWN0aW9uPgo8c2VjdGlvbiBjbGFzcz0iZGlzY2xhaW1lciI+PHN0cm9uZz5NZWFzdXJlbWVudCBsaW1pdGF0aW9uOjwvc3Ryb25nPiBMb2dpY2FsIGNoZWNrcG9pbnQgYnl0ZXMgd2VyZQptZWFzdXJlZCBpbiB0aGUgY29udHJvbGxlZCBkZW1vLiBQaHlzaWNhbCBOQU5EIHdyaXRlcywgd3JpdGUgYW1wbGlmaWNhdGlvbiwgYW5kIFNTRCBsaWZldGltZSB3ZXJlCm5vdCBtZWFzdXJlZC48L3NlY3Rpb24+CjwvbWFpbj48L2JvZHk+PC9odG1sPgo=",
   "report.md": "IyBGbGFzaFBpbG90IGJvdW5kZWQgcmVwYWlyIHJlcG9ydAoKVGhlIGZhaWx1cmUgaXMgaW50ZW50aW9uYWwgYW5kIGRldGVybWluaXN0aWMsIGJ1dCBHUFQtNS42IGRvZXMgbm90IHJlY2VpdmUgdGhlIGluamVjdGlvbiBsYWJlbC4gSXQgcmVjZWl2ZXMgb25seSB0aGUgc2FuaXRpemVkIGNoZWNrcG9pbnQgbWFuaWZlc3QsIHJlc3RvcmUgYmVoYXZpb3IsIGZhaWxlZCBSZWNvdmVyeSBHYXRlIGNoZWNrcywgYW5kIHRyYWplY3RvcnkgZXZpZGVuY2UuCgpGaW5hbCB2ZXJkaWN0OiAqKlZFUklGSUVEKioKCk9ubHkgdGhlIGRldGVybWluaXN0aWMgUmVjb3ZlcnkgR2F0ZSBzZXRzIHRoaXMgdmVyZGljdDsgdGhlIHJlcGxheWVkIEdQVC01LjYgcmVzcG9uc2UgZG9lcyBub3QgZGVjbGFyZSByZWNvdmVyeS4KCiMjIEluaXRpYWwgZmFpbHVyZQoKLSBXb3JrZXIgUElEOiAzMTQxMgotIFJlY292ZXJ5IFBJRDogMTY2MDAKLSBHYXRlIHBhc3NlZDogRmFsc2UKLSBGYWlsZWQgY2hlY2tzOiBzdGF0ZS5vcHRpbWl6ZXIsIHN0YXRlLnNjaGVkdWxlciwgc3RhdGUucHl0aG9uX3JuZywgc3RhdGUubnVtcHlfcm5nLCBzdGF0ZS50b3JjaF9ybmcsIHRyYWplY3RvcnkuZmluYWxfdHJhaW5hYmxlLCB0cmFqZWN0b3J5LmZpbmFsX2V2YWx1YXRpb24sIHRyYWplY3RvcnkubG9zc19oaXN0b3J5LCBjb250cmFjdC5ub19tYW5kYXRvcnlfb21pc3Npb24KCiMjIEJvdW5kZWQgcmVwYWlyCgotIFByb3ZpZGVyIG1vZGU6IGZpeHR1cmUgcmVwbGF5IG9mIGFuIGFjY2VwdGVkIHNlY3JldC1mcmVlIEdQVC01LjYgc3RydWN0dXJlZCByZXNwb25zZQotIENhcHR1cmVkIHJlc3BvbnNlIElEOiByZXNwXzBkN2U4MDhjZDcyMmY5N2YwMTZhNWE5MGYwMzAwNDgxOTA4ZDIyZTdiZWZhMTVlM2ZlCi0gUHJvcG9zZWQgYWN0aW9uczogY2hhbmdlX3N1cHBvcnRlZF9jaGVja3BvaW50X3N0cmF0ZWd5LCBwZXJzaXN0X29wdGltaXplcl9zdGF0ZSwgcGVyc2lzdF9zY2hlZHVsZXJfc3RhdGUsIHBlcnNpc3RfcHl0aG9uX3JuZ19zdGF0ZSwgcGVyc2lzdF9udW1weV9ybmdfc3RhdGUsIHBlcnNpc3RfdG9yY2hfcm5nX3N0YXRlLCByZXN0b3JlX3N0YXRlX2JlZm9yZV9uZXh0X2JhdGNoCi0gQXBwbGllZCBhY3Rpb25zOiBwZXJzaXN0X29wdGltaXplcl9zdGF0ZSwgcGVyc2lzdF9zY2hlZHVsZXJfc3RhdGUsIHBlcnNpc3RfcHl0aG9uX3JuZ19zdGF0ZSwgcGVyc2lzdF9udW1weV9ybmdfc3RhdGUsIHBlcnNpc3RfdG9yY2hfcm5nX3N0YXRlLCByZXN0b3JlX3N0YXRlX2JlZm9yZV9uZXh0X2JhdGNoCi0gVW5zdXBwb3J0ZWQgYWN0aW9uczogY2hhbmdlX3N1cHBvcnRlZF9jaGVja3BvaW50X3N0cmF0ZWd5Ci0gUmVqZWN0ZWQgYWN0aW9uczogbm9uZQotIFJlcGFpciBhdHRlbXB0czogMQotIE5ldyBzdHJhdGVneSBJRDogbmF0aXZlLXJlcGFpcmVkLWNvbXBsZXRlLXYxCi0gaW5jbHVkZV9vcHRpbWl6ZXI6IFRydWUKLSBpbmNsdWRlX3NjaGVkdWxlcjogVHJ1ZQotIGluY2x1ZGVfcHl0aG9uX3JuZzogVHJ1ZQotIGluY2x1ZGVfbnVtcHlfcm5nOiBUcnVlCi0gaW5jbHVkZV90b3JjaF9ybmc6IFRydWUKLSByZXN0b3JlX2JlZm9yZV9uZXh0X2JhdGNoOiBUcnVlCgojIyBSZXBhaXJlZCB2ZXJpZmljYXRpb24KCi0gV29ya2VyIFBJRDogMjc2MzIKLSBSZWNvdmVyeSBQSUQ6IDMxMzk2Ci0gR2F0ZSBwYXNzZWQ6IFRydWUKLSBFeGFjdCBhdG9sL3J0b2w6IDAuMC8wLjAKLSBPcmlnaW5hbCBmYWlsZWQgY2hlY2twb2ludCB1bm1vZGlmaWVkOiBUcnVlCgojIyBQb3N0LXZlcmlmaWNhdGlvbiBzdG9yYWdlIG1lYXN1cmVtZW50CgotIHNhZmVfZnVsbCByZWN1cnJpbmcgbG9naWNhbCBieXRlczogNDQ5OTgKLSByZXBhaXJlZCByZWN1cnJpbmcgbG9naWNhbCBieXRlczogMjc2ODEKLSBvbmUtdGltZSBmcm96ZW4gYmFzZSBieXRlczogMTg0NzUKLSBzdHJ1Y3R1cmFsIHJlZHVjdGlvbjogMTczMTcgYnl0ZXMgKDM4LjQ4JSkKCiMjIE1lYXN1cmVtZW50IGxpbWl0YXRpb24KCkxvZ2ljYWwgY2hlY2twb2ludCBieXRlcyB3ZXJlIG1lYXN1cmVkIGluIHRoZSBjb250cm9sbGVkIGRlbW8uIFBoeXNpY2FsIE5BTkQgd3JpdGVzLCB3cml0ZSBhbXBsaWZpY2F0aW9uLCBhbmQgU1NEIGxpZmV0aW1lIHdlcmUgbm90IG1lYXN1cmVkLgo=",
   "result.json": "ewogICJjYXB0dXJlZF9saXZlX2ZhaWx1cmVfbWV0YWRhdGEiOiB7CiAgICAiZml4dHVyZV9wcm92ZW5hbmNlIjogIm5vdF9hcHBsaWNhYmxlIiwKICAgICJsaXZlX29yX2ZpeHR1cmUiOiAibGl2ZSIsCiAgICAibW9kZWwiOiAiZ3B0LTUuNiIsCiAgICAib3V0cHV0X3NjaGVtYV92ZXJzaW9uIjogImZhaWx1cmUtYW5hbHlzaXMtdjIiLAogICAgInByb21wdF92ZXJzaW9uIjogInYyIiwKICAgICJwcm92aWRlciI6ICJvcGVuYWkiLAogICAgInJlcXVlc3Rfc2hhMjU2IjogImVhYTZmNzgxOGVjZGFmNDgyNTI1MDgxNTE0ZGNjZmJmZTc0OGFlNzliMGQxN2MxYTcxOWE1ZTYwYmZjNWJhMmUiLAogICAgInJlc3BvbnNlX2lkIjogInJlc3BfMGQ3ZTgwOGNkNzIyZjk3ZjAxNmE1YTkwZjAzMDA0ODE5MDhkMjJlN2JlZmExNWUzZmUiLAogICAgInJvbGUiOiAiZmFpbHVyZS1hbmFseXNpcyIsCiAgICAic2NoZW1hX3ZlcnNpb24iOiAiYWdlbnQtY2FsbC1tZXRhZGF0YS12MSIsCiAgICAic291cmNlIjogImNhcHR1cmVkX2xpdmVfcmVzcG9uc2UiLAogICAgInN0b3JlIjogZmFsc2UsCiAgICAidGltZXN0YW1wIjogIjIwMjYtMDctMTdUMjA6MzE6MDkuNzcxODIwWiIsCiAgICAidmFsaWRhdGlvbl9zdGF0dXMiOiAiYWNjZXB0ZWQiCiAgfSwKICAiY3JlYXRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjEzLjA3NjY0NVoiLAogICJmYWxsYmFja19zdGF0dXMiOiAibm90X3JlcXVpcmVkIiwKICAiZmluYWxfdmVyZGljdCI6ICJWRVJJRklFRCIsCiAgImh0bWxfcmVwb3J0X3BhdGgiOiAicmVwb3J0Lmh0bWwiLAogICJpbml0aWFsX2ZhaWx1cmUiOiB7CiAgICAiY29udHJvbCI6IHsKICAgICAgImV2YWx1YXRpb25fc2hhMjU2IjogImE0MmE2ZDI1YzhhYWY2Njc0MTMwZWY2MzQzOWY2ZmQ0MTU4MjRiZDIzZmY5Y2Q2YTdjMGNhMDMwNWJlM2VmOWEiLAogICAgICAiZ2xvYmFsX3N0ZXAiOiA4LAogICAgICAibG9zc19oaXN0b3J5IjogWwogICAgICAgIDMuNTM3MTk3NTg5ODc0MjY3NiwKICAgICAgICAzLjQzNDQ1NzU0MDUxMjA4NSwKICAgICAgICAzLjU5NzcwNjU1NjMyMDE5MDQsCiAgICAgICAgMy41NjA3NDY2Njk3NjkyODcsCiAgICAgICAgMy42NzA4MjM1NzQwNjYxNjIsCiAgICAgICAgMy42MjcyNTMyOTM5OTEwODksCiAgICAgICAgMy41MDg2MzkzMzU2MzIzMjQsCiAgICAgICAgMy44MjQ4MTQzMTk2MTA1OTU3CiAgICAgIF0sCiAgICAgICJvcHRpbWl6ZXJfc2hhMjU2IjogImMwM2RmYzhiNjZlNjY0NWZiNTUyMjIzNDI4YWQ4NmE4NTVjOTcwNDlkMTMzYjA4OTg0NjA0ZjZlN2Q1NWEwNTAiLAogICAgICAic2NoZWR1bGVyX3NoYTI1NiI6ICJlMDdmZmQ2YTg5ZmVmYjYxZTgwZDFjYTU2MDI1YTkyNzIyMmE4MzE4MGZmY2VkNzc4Nzg5NjA2ZDNhN2JlYzgxIiwKICAgICAgInRyYWluYWJsZV9zdGF0ZV9zaGEyNTYiOiAiMWZjNzJmZGYyMTQ4N2FmZTdiMzJkYTgzM2QyMzAwY2Q5YTY4ZjBjMGM2ZjNjZTE0NTY5MTBhNTEwMmE5Mjk5NyIKICAgIH0sCiAgICAiY3Jhc2giOiB7CiAgICAgICJjaGVja3BvaW50X3BhdGgiOiAiY2hlY2twb2ludHMvbWlzc2luZy10cmFpbmluZy1zdGF0ZS9jaGVja3BvaW50LXN0ZXAtMDAwMDA0IiwKICAgICAgImNoZWNrcG9pbnRfc3RlcCI6IDQsCiAgICAgICJldmVudF9yZWNlaXZlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI4OjU5LjEzMjAzOFoiLAogICAgICAibGFzdF9jb21wbGV0ZWRfc3RlcCI6IDQsCiAgICAgICJ0ZXJtaW5hdGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjg6NTkuMTc0MjAyWiIsCiAgICAgICJ0ZXJtaW5hdGlvbl9leGl0X2NvZGUiOiAxLAogICAgICAidGVybWluYXRpb25fbWV0aG9kIjogIlRlcm1pbmF0ZVByb2Nlc3MgdmlhIHN1YnByb2Nlc3MuUG9wZW4ua2lsbCIsCiAgICAgICJ0ZXJtaW5hdGlvbl92ZXJpZmllZCI6IHRydWUsCiAgICAgICJ3b3JrZXJfcGlkIjogMzE0MTIKICAgIH0sCiAgICAiY3JlYXRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjA1LjExOTkyMVoiLAogICAgImZhaWx1cmVfYXJ0aWZhY3RfcGF0aCI6ICJhZ2VudC9yZXF1ZXN0LnJlZGFjdGVkLmpzb24iLAogICAgImdhdGUiOiB7CiAgICAgICJhY2hpZXZlZF9yb2xsYmFja19zdGVwcyI6IDAsCiAgICAgICJjaGVja3MiOiBbCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJjaGVja3BvaW50LW1hbmlmZXN0LXYxIiwKICAgICAgICAgICJjYXRlZ29yeSI6ICJJbnRlZ3JpdHkiLAogICAgICAgICAgImNoZWNrX2lkIjogImludGVncml0eS5tYW5pZmVzdF9zY2hlbWEiLAogICAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICAgIm1hbmlmZXN0OnNjaGVtYSIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiY2hlY2twb2ludC1tYW5pZmVzdC12MSIsCiAgICAgICAgICAibGFiZWwiOiAiTWFuaWZlc3Qgc2NoZW1hIHZhbGlkIiwKICAgICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAicHJlc2VudCIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgICAgICJjaGVja19pZCI6ICJpbnRlZ3JpdHkuY29tcGxldGlvbl9tYXJrZXIiLAogICAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICAgImludGVncml0eTpjb21wbGV0aW9uLW1hcmtlciIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiQ09NUExFVEUgcHJlc2VudCBpbiBmaW5hbCBjaGVja3BvaW50IiwKICAgICAgICAgICJsYWJlbCI6ICJDb21wbGV0aW9uIG1hcmtlciBwcmVzZW50IiwKICAgICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAiMiBwYXlsb2FkcyB2YWxpZGF0ZWQiLAogICAgICAgICAgImNhdGVnb3J5IjogIkludGVncml0eSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAiaW50ZWdyaXR5LmNoZWNrc3VtcyIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAiaW50ZWdyaXR5OnNoYTI1NiIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiZXZlcnkgbWFuaWZlc3QgcGF5bG9hZCBtYXRjaGVzIFNIQS0yNTYgYW5kIHNpemUiLAogICAgICAgICAgImxhYmVsIjogIkFsbCBwYXlsb2FkIGNoZWNrc3VtcyB2YWxpZCIsCiAgICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogInByZXNlbnQiLAogICAgICAgICAgImNhdGVnb3J5IjogIkludGVncml0eSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAiaW50ZWdyaXR5LmJhc2VfcHJlc2VudCIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAiYmFzZTpwcmVzZW5jZSIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiY29udGFpbmVkIGltbXV0YWJsZSBiYXNlIGFydGlmYWN0IiwKICAgICAgICAgICJsYWJlbCI6ICJCYXNlIGFydGlmYWN0IHByZXNlbnQgd2hlbiByZXF1aXJlZCIsCiAgICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogImMxN2NjODk5NGM4ZjBmZTZkZWYzMjQyM2IwZTVkOWVmZWRmZmIzY2Q3MWM3ZGU5NjMxZjI2Y2Y1MDU5MjVkODYiLAogICAgICAgICAgImNhdGVnb3J5IjogIkludGVncml0eSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAiaW50ZWdyaXR5LmJhc2VfaGFzaCIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAiYmFzZTpzaGEyNTYiCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogImMxN2NjODk5NGM4ZjBmZTZkZWYzMjQyM2IwZTVkOWVmZWRmZmIzY2Q3MWM3ZGU5NjMxZjI2Y2Y1MDU5MjVkODYiLAogICAgICAgICAgImxhYmVsIjogIkJhc2UgYXJ0aWZhY3QgaGFzaCBtYXRjaGVzIiwKICAgICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAibWFuaWZlc3Q9NCwgZXZlbnQ9NCwgcmVzdG9yZWQ9NCIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiUmVxdWlyZWQgdHJhaW5pbmcgc3RhdGUiLAogICAgICAgICAgImNoZWNrX2lkIjogInN0YXRlLmdsb2JhbF9zdGVwIiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJtYW5pZmVzdDpnbG9iYWwtc3RlcCIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiMCA8IHN0ZXAgPCA4LCBjb25zaXN0ZW50IGFjcm9zcyByZXN0b3JlIiwKICAgICAgICAgICJsYWJlbCI6ICJDaGVja3BvaW50IGdsb2JhbCBzdGVwIGlzIHZhbGlkIiwKICAgICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAic2VyaWFsaXplZD1UcnVlLCBkaWdlc3RfbWF0Y2g9VHJ1ZSIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiUmVxdWlyZWQgdHJhaW5pbmcgc3RhdGUiLAogICAgICAgICAgImNoZWNrX2lkIjogInN0YXRlLm1vZGVsX29yX2FkYXB0ZXIiLAogICAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICAgInJlc3RvcmU6bW9kZWwtc3RhdGUiCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogInNlcmlhbGl6ZWQgYWRhcHRlciBhbmQgZXhhY3QgdHJhaW5hYmxlLXN0YXRlIGRpZ2VzdCIsCiAgICAgICAgICAibGFiZWwiOiAiTW9kZWwgb3IgYWRhcHRlciBzdGF0ZSByZXN0b3JlcyIsCiAgICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1GYWxzZSIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiUmVxdWlyZWQgdHJhaW5pbmcgc3RhdGUiLAogICAgICAgICAgImNoZWNrX2lkIjogInN0YXRlLm9wdGltaXplciIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAicmVzdG9yZTpvcHRpbWl6ZXItc3RhdGUiCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogInNlcmlhbGl6ZWQgb3B0aW1pemVyIHdpdGggZXhhY3QgZGlnZXN0IiwKICAgICAgICAgICJsYWJlbCI6ICJPcHRpbWl6ZXIgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAgICAgICAic3RhdHVzIjogImZhaWwiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1GYWxzZSIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiUmVxdWlyZWQgdHJhaW5pbmcgc3RhdGUiLAogICAgICAgICAgImNoZWNrX2lkIjogInN0YXRlLnNjaGVkdWxlciIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAicmVzdG9yZTpzY2hlZHVsZXItc3RhdGUiCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogInNlcmlhbGl6ZWQgc2NoZWR1bGVyIHdpdGggZXhhY3QgZGlnZXN0IiwKICAgICAgICAgICJsYWJlbCI6ICJTY2hlZHVsZXIgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAgICAgICAic3RhdHVzIjogImZhaWwiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9RmFsc2UsIGRpZ2VzdF9tYXRjaD1UcnVlIiwKICAgICAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUucHl0aG9uX3JuZyIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAicmVzdG9yZTpweXRob24tcm5nIgogICAgICAgICAgXSwKICAgICAgICAgICJleHBlY3RlZCI6ICJzZXJpYWxpemVkIHN0YXRlIHdpdGggZXhhY3QgZGlnZXN0IiwKICAgICAgICAgICJsYWJlbCI6ICJQeXRob24gUk5HIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAgICAgInN0YXR1cyI6ICJmYWlsIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJzZXJpYWxpemVkPUZhbHNlLCBkaWdlc3RfbWF0Y2g9VHJ1ZSIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiUmVxdWlyZWQgdHJhaW5pbmcgc3RhdGUiLAogICAgICAgICAgImNoZWNrX2lkIjogInN0YXRlLm51bXB5X3JuZyIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAicmVzdG9yZTpudW1weS1ybmciCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogInNlcmlhbGl6ZWQgc3RhdGUgd2l0aCBleGFjdCBkaWdlc3QiLAogICAgICAgICAgImxhYmVsIjogIk51bVB5IFJORyBzdGF0ZSByZXN0b3JlcyB3aGVuIHJlcXVpcmVkIiwKICAgICAgICAgICJzdGF0dXMiOiAiZmFpbCIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAic2VyaWFsaXplZD1GYWxzZSwgZGlnZXN0X21hdGNoPUZhbHNlIiwKICAgICAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUudG9yY2hfcm5nIiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJyZXN0b3JlOnRvcmNoLXJuZyIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBzdGF0ZSB3aXRoIGV4YWN0IGRpZ2VzdCIsCiAgICAgICAgICAibGFiZWwiOiAiVG9yY2ggUk5HIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAgICAgInN0YXR1cyI6ICJmYWlsIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJmaXJzdCBiYXRjaCBhdCA0LCBmaXJzdCBjb21wbGV0aW9uIGF0IDUiLAogICAgICAgICAgImNhdGVnb3J5IjogIlByb2Nlc3MgcmVjb3ZlcnkiLAogICAgICAgICAgImNoZWNrX2lkIjogInByb2Nlc3MubmV4dF9zdGVwIiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJwcm9jZXNzOm5leHQtc3RlcCIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiZmlyc3QgYmF0Y2ggYXQgNCwgZmlyc3QgY29tcGxldGlvbiBhdCA1IiwKICAgICAgICAgICJsYWJlbCI6ICJSZXN1bWVkIHJ1biBjb250aW51ZXMgZnJvbSB0aGUgZXhwZWN0ZWQgbmV4dCBzdGVwIiwKICAgICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAiMzE0MTIiLAogICAgICAgICAgImNhdGVnb3J5IjogIlByb2Nlc3MgcmVjb3ZlcnkiLAogICAgICAgICAgImNoZWNrX2lkIjogInByb2Nlc3Mub3JpZ2luYWxfcGlkIiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJwcm9jZXNzOm9yaWdpbmFsLXBpZCIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiMzE0MTIiLAogICAgICAgICAgImxhYmVsIjogIk9yaWdpbmFsIHdvcmtlciBQSUQgaXMgcmVjb3JkZWQiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJtZXRob2Q9VGVybWluYXRlUHJvY2VzcyB2aWEgc3VicHJvY2Vzcy5Qb3Blbi5raWxsLCBleGl0PTEsIHZlcmlmaWVkPVRydWUiLAogICAgICAgICAgImNhdGVnb3J5IjogIlByb2Nlc3MgcmVjb3ZlcnkiLAogICAgICAgICAgImNoZWNrX2lkIjogInByb2Nlc3MuZXhwZWN0ZWRfdGVybWluYXRpb24iLAogICAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICAgInByb2Nlc3M6dGVybWluYXRpb24iCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogInBhcmVudCB0ZXJtaW5hdGlvbiB3aXRoIG5vbnplcm8gZXhpdCBjb2RlIiwKICAgICAgICAgICJsYWJlbCI6ICJPcmlnaW5hbCB3b3JrZXIgdGVybWluYXRpb24gaXMgdmVyaWZpZWQiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICIxNjYwMCIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAicHJvY2Vzcy5uZXdfcmVjb3ZlcnlfcGlkIiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJwcm9jZXNzOnJlY292ZXJ5LXBpZCIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiUElEIGRpZmZlcmVudCBmcm9tIDMxNDEyIiwKICAgICAgICAgICJsYWJlbCI6ICJSZWNvdmVyeSB1c2VzIGEgZGlmZmVyZW50IFBJRCIsCiAgICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogImV4aXQ9MCwgdmVyaWZpZWQ9VHJ1ZSIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAicHJvY2Vzcy5yZWNvdmVyeV9leGl0IiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJwcm9jZXNzOnJlY292ZXJ5LWV4aXQiCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogImV4aXQgY29kZSAwIiwKICAgICAgICAgICJsYWJlbCI6ICJSZWNvdmVyeSB3b3JrZXIgZXhpdHMgc3VjY2Vzc2Z1bGx5IiwKICAgICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAiMCBzdGVwcyIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiU2FmZXR5IGFuZCByb2xsYmFjayIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAicm9sbGJhY2suaGFyZF9saW1pdCIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAicm9sbGJhY2s6YWNoaWV2ZWQiCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogIjw9IDAgc3RlcHMiLAogICAgICAgICAgImxhYmVsIjogIkFjaGlldmVkIHJvbGxiYWNrIGlzIHdpdGhpbiB0aGUgaGFyZCBsaW1pdCIsCiAgICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogImQ2MDU3MmFlYTEyZjkxOTYwZjNmMDAzMGJkZmRjYTU1ZmRhZmUwNTkxNDZjNzIzMGFmOTA5NDkyMzgxMWQzMTIiLAogICAgICAgICAgImNhdGVnb3J5IjogIlRyYWplY3RvcnkgY29ycmVjdG5lc3MiLAogICAgICAgICAgImNoZWNrX2lkIjogInRyYWplY3RvcnkuY2hlY2twb2ludF9ldmFsdWF0aW9uIiwKICAgICAgICAgICJkZXRhaWxzIjogIkV4YWN0IFNIQS0yNTYgY29tcGFyaXNvbjsgbm8gbnVtZXJpY2FsIHRvbGVyYW5jZSBpcyBhcHBsaWVkLiIsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAidHJhamVjdG9yeTpjaGVja3BvaW50LWV2YWx1YXRpb24iCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogImQ2MDU3MmFlYTEyZjkxOTYwZjNmMDAzMGJkZmRjYTU1ZmRhZmUwNTkxNDZjNzIzMGFmOTA5NDkyMzgxMWQzMTIiLAogICAgICAgICAgImxhYmVsIjogIkZpeGVkIGV2YWx1YXRpb24gYWZ0ZXIgcmVzdG9yZSBtYXRjaGVzIiwKICAgICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAiZDI4NTQ3ZTgyZGM0MTJkNTgwNjBlOGJlNjRkZWI1MjE5MWI3YjI1ODU2MWJlNDc4NzQ2OTRiMWM1NDZlY2E2NiIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiVHJhamVjdG9yeSBjb3JyZWN0bmVzcyIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAidHJhamVjdG9yeS5maW5hbF90cmFpbmFibGUiLAogICAgICAgICAgImRldGFpbHMiOiAiRXhhY3QgU0hBLTI1NiBjb21wYXJpc29uOyBubyBudW1lcmljYWwgdG9sZXJhbmNlIGlzIGFwcGxpZWQuIiwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJ0cmFqZWN0b3J5OmZpbmFsLXRyYWluYWJsZSIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiMWZjNzJmZGYyMTQ4N2FmZTdiMzJkYTgzM2QyMzAwY2Q5YTY4ZjBjMGM2ZjNjZTE0NTY5MTBhNTEwMmE5Mjk5NyIsCiAgICAgICAgICAibGFiZWwiOiAiRmluYWwgdHJhaW5hYmxlIHBhcmFtZXRlcnMgbWF0Y2ggY29udHJvbCIsCiAgICAgICAgICAic3RhdHVzIjogImZhaWwiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogIjQzNDZhMmQ3N2IzNzA3NmI4NTNkNDUyOTk4MTgyNGVkZDU0OTUzOGY5MzhkNDk2NDIyMDg5OTE0OWRkNWI0Y2QiLAogICAgICAgICAgImNhdGVnb3J5IjogIlRyYWplY3RvcnkgY29ycmVjdG5lc3MiLAogICAgICAgICAgImNoZWNrX2lkIjogInRyYWplY3RvcnkuZmluYWxfZXZhbHVhdGlvbiIsCiAgICAgICAgICAiZGV0YWlscyI6ICJFeGFjdCBTSEEtMjU2IGNvbXBhcmlzb247IG5vIG51bWVyaWNhbCB0b2xlcmFuY2UgaXMgYXBwbGllZC4iLAogICAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICAgInRyYWplY3Rvcnk6ZmluYWwtZXZhbHVhdGlvbiIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiYTQyYTZkMjVjOGFhZjY2NzQxMzBlZjYzNDM5ZjZmZDQxNTgyNGJkMjNmZjljZDZhN2MwY2EwMzA1YmUzZWY5YSIsCiAgICAgICAgICAibGFiZWwiOiAiRmluYWwgZXZhbHVhdGlvbiBsb2dpdHMgbWF0Y2ggY29udHJvbCIsCiAgICAgICAgICAic3RhdHVzIjogImZhaWwiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogInNlcXVlbmNlIGRpZmZlcnMiLAogICAgICAgICAgImNhdGVnb3J5IjogIlRyYWplY3RvcnkgY29ycmVjdG5lc3MiLAogICAgICAgICAgImNoZWNrX2lkIjogInRyYWplY3RvcnkubG9zc19oaXN0b3J5IiwKICAgICAgICAgICJkZXRhaWxzIjogIkV4YWN0IGZsb2F0IHNlcXVlbmNlIGNvbXBhcmlzb247IG5vIG51bWVyaWNhbCB0b2xlcmFuY2UgaXMgYXBwbGllZC4iLAogICAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICAgInRyYWplY3Rvcnk6bG9zcy1oaXN0b3J5IgogICAgICAgICAgXSwKICAgICAgICAgICJleHBlY3RlZCI6ICJleGFjdCBsb3NzIHNlcXVlbmNlIGVxdWFsaXR5IiwKICAgICAgICAgICJsYWJlbCI6ICJDb250aW51ZWQgbG9zcyB0cmFqZWN0b3J5IG1hdGNoZXMgY29udHJvbCIsCiAgICAgICAgICAic3RhdHVzIjogImZhaWwiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogImNvbnRhaW5lZCIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiU2FmZXR5IGFuZCByb2xsYmFjayIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAic2FmZXR5LnBhdGhfY29udGFpbm1lbnQiLAogICAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICAgInNhZmV0eTpwYXRoLWNvbnRhaW5tZW50IgogICAgICAgICAgXSwKICAgICAgICAgICJleHBlY3RlZCI6ICJhbGwgcGF0aHMgY29udGFpbmVkOyBzeW1saW5rIGVzY2FwZXMgcmVqZWN0ZWQiLAogICAgICAgICAgImxhYmVsIjogIkFsbCBtYW5hZ2VkIHdyaXRlIHBhdGhzIHBhc3NlZCBjb250YWlubWVudCIsCiAgICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogIm1hbmlmZXN0IGxhY2tzOiBudW1weV9ybmcsIG9wdGltaXplciwgcHl0aG9uX3JuZywgc2NoZWR1bGVyLCB0b3JjaF9ybmciLAogICAgICAgICAgImNhdGVnb3J5IjogIlNhZmV0eSBhbmQgcm9sbGJhY2siLAogICAgICAgICAgImNoZWNrX2lkIjogImNvbnRyYWN0Lm5vX21hbmRhdG9yeV9vbWlzc2lvbiIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIgogICAgICAgICAgXSwKICAgICAgICAgICJleHBlY3RlZCI6ICJhbGwgbWFuZGF0b3J5IGNvbnRpbnVhdGlvbiBzdGF0ZSBkZWNsYXJlZCIsCiAgICAgICAgICAibGFiZWwiOiAiTm8gbWFuZGF0b3J5IGNvbnRyYWN0IHJlcXVpcmVtZW50IHdhcyBzaWxlbnRseSBvbWl0dGVkIiwKICAgICAgICAgICJzdGF0dXMiOiAiZmFpbCIKICAgICAgICB9CiAgICAgIF0sCiAgICAgICJjb21wYXJpc29uX3BvbGljeSI6IHsKICAgICAgICAiYXRvbCI6IDAuMCwKICAgICAgICAiZXZhbHVhdGlvbl9sb2dpdHMiOiAic2hhMjU2X2V4YWN0IiwKICAgICAgICAiZXZpZGVuY2UiOiAiVGhlIGNvbnRyb2xsZWQgQ1BVIHdvcmtsb2FkIHVzZXMgZGV0ZXJtaW5pc3RpYyBhbGdvcml0aG1zLCBvbmUgVG9yY2ggdGhyZWFkLCBmaXhlZCBzZWVkcywgYW5kIHN0ZXAtZGVyaXZlZCBiYXRjaGVzLiBDcm9zcy1wcm9jZXNzIGNvbXBhcmlzb25zIGZhaWwgb24gYW55IGRpZ2VzdCBvciBsb3NzLXNlcXVlbmNlIGRpZmZlcmVuY2UuIiwKICAgICAgICAibG9zc19oaXN0b3J5IjogInNlcXVlbmNlX2V4YWN0IiwKICAgICAgICAibW9kZSI6ICJleGFjdCIsCiAgICAgICAgIm9wdGltaXplcl9zdGF0ZSI6ICJzaGEyNTZfZXhhY3QiLAogICAgICAgICJybmdfc3RhdGUiOiAic2hhMjU2X2V4YWN0IiwKICAgICAgICAicnRvbCI6IDAuMCwKICAgICAgICAic2NoZWR1bGVyX3N0YXRlIjogInNoYTI1Nl9leGFjdCIsCiAgICAgICAgInRyYWluYWJsZV9wYXJhbWV0ZXJzIjogInNoYTI1Nl9leGFjdCIKICAgICAgfSwKICAgICAgImZhaWxlZF9jaGVja19pZHMiOiBbCiAgICAgICAgInN0YXRlLm9wdGltaXplciIsCiAgICAgICAgInN0YXRlLnNjaGVkdWxlciIsCiAgICAgICAgInN0YXRlLnB5dGhvbl9ybmciLAogICAgICAgICJzdGF0ZS5udW1weV9ybmciLAogICAgICAgICJzdGF0ZS50b3JjaF9ybmciLAogICAgICAgICJ0cmFqZWN0b3J5LmZpbmFsX3RyYWluYWJsZSIsCiAgICAgICAgInRyYWplY3RvcnkuZmluYWxfZXZhbHVhdGlvbiIsCiAgICAgICAgInRyYWplY3RvcnkubG9zc19oaXN0b3J5IiwKICAgICAgICAiY29udHJhY3Qubm9fbWFuZGF0b3J5X29taXNzaW9uIgogICAgICBdLAogICAgICAiaGFyZF9yb2xsYmFja19saW1pdF9zdGVwcyI6IDAsCiAgICAgICJwYXNzZWQiOiBmYWxzZSwKICAgICAgInNjaGVtYV92ZXJzaW9uIjogInJlY292ZXJ5LWdhdGUtdjEiCiAgICB9LAogICAgImxpbWl0YXRpb25zIjogWwogICAgICAiUGh5c2ljYWwgTkFORCB3cml0ZXMsIHdyaXRlIGFtcGxpZmljYXRpb24sIGFuZCBTU0QgbGlmZXRpbWUgd2VyZSBub3QgbWVhc3VyZWQuIiwKICAgICAgIk5vIEdQVCBwcm92aWRlciwgZGlhZ25vc2lzLCByZXBhaXIgZXhlY3V0aW9uLCBIVE1MLCBvciBwYWNrYWdpbmcgaXMgcGFydCBvZiBQcm9tcHQgMy4iCiAgICBdLAogICAgInBsYXRmb3JtX3N1cHBvcnRfbm90ZSI6ICJXaW5kb3dzOiBwYXlsb2FkIGFuZCBtZXRhZGF0YSBmaWxlcyBhcmUgZnN5bmNlZCBhbmQgZGlyZWN0b3J5IHJlbmFtZSBpcyBhdG9taWM7IGRpcmVjdG9yeSBmc3luYyBpcyB1bmF2YWlsYWJsZSB0aHJvdWdoIFB5dGhvbiBhbmQgcmVtYWlucyBiZXN0LWVmZm9ydC4iLAogICAgInByb2ZpbGUiOiAiY2kiLAogICAgInJlY292ZXJ5IjogewogICAgICAiYWZ0ZXJfcmVzdG9yZSI6IHsKICAgICAgICAiZXZhbHVhdGlvbl9zaGEyNTYiOiAiZDYwNTcyYWVhMTJmOTE5NjBmM2YwMDMwYmRmZGNhNTVmZGFmZTA1OTE0NmM3MjMwYWY5MDk0OTIzODExZDMxMiIsCiAgICAgICAgImdsb2JhbF9zdGVwIjogNCwKICAgICAgICAibG9zc19oaXN0b3J5IjogWwogICAgICAgICAgMy41MzcxOTc1ODk4NzQyNjc2LAogICAgICAgICAgMy40MzQ0NTc1NDA1MTIwODUsCiAgICAgICAgICAzLjU5NzcwNjU1NjMyMDE5MDQsCiAgICAgICAgICAzLjU2MDc0NjY2OTc2OTI4NwogICAgICAgIF0sCiAgICAgICAgIm9wdGltaXplcl9zaGEyNTYiOiAiM2ZkMGY1MGUwYjQ4M2ZkNTQ5NTIwMjk2Zjg4ZWM2MTY0YzYwZGQ4ZTc1M2RhNTQzYmZmN2JhNTM1ZDllNmRlMyIsCiAgICAgICAgInNjaGVkdWxlcl9zaGEyNTYiOiAiNzhhMDMzOWUxMmFiZWQzMjcyYmJiYWFiMWYzYWU2NzU5YjU1ZWFmM2YzZWU4MDdmOTk4YzVjYzkyMTEzY2ZhOCIsCiAgICAgICAgInRyYWluYWJsZV9zdGF0ZV9zaGEyNTYiOiAiNDNiYTc1ODA4OTA2OTMyYTAwNWIwZDNlMTg2YjU3ODZhYjY0YTI1ZmRjZTU1NDI2NTVkMmQwOTUxZmM2ZWViNSIKICAgICAgfSwKICAgICAgImFmdGVyX3Jlc3RvcmVfcm5nIjogewogICAgICAgICJudW1weV9zaGEyNTYiOiAiYWRjN2U1NDVlYzA1MzBlYWU5ZjFkYTcyNWU4M2Y0OGIxNDZiZDRlYzc5Zjk4NDUxMzY3Y2EzZDE4ZTk5NGRiNSIsCiAgICAgICAgInB5dGhvbl9zaGEyNTYiOiAiZGQ4YWVjMWNjZjMwNTNkZTYxZWQ2YTQ1OWUyNjY4YzM4NWI3OTk2ZWFlZGQ5NDc0NDQwMDYyMDk5OTVhNzA2MyIsCiAgICAgICAgInRvcmNoX3NoYTI1NiI6ICI1NmE1OWVlNDE1NGM4NzYzODZkOWFmYTk2YTI0MjdmNzlhNzM2ZTk4ODg3Y2M2MDc3YTY0MDlkMGFmZmVlMjkwIgogICAgICB9LAogICAgICAiY2hlY2twb2ludF9wYXRoIjogImNoZWNrcG9pbnRzL21pc3NpbmctdHJhaW5pbmctc3RhdGUvY2hlY2twb2ludC1zdGVwLTAwMDAwNCIsCiAgICAgICJjb21wbGV0ZWRfYXQiOiAiMjAyNi0wNy0yMFQwMToyOTowNC42Njk2NDVaIiwKICAgICAgImZpbmFsIjogewogICAgICAgICJldmFsdWF0aW9uX3NoYTI1NiI6ICI0MzQ2YTJkNzdiMzcwNzZiODUzZDQ1Mjk5ODE4MjRlZGQ1NDk1MzhmOTM4ZDQ5NjQyMjA4OTkxNDlkZDViNGNkIiwKICAgICAgICAiZ2xvYmFsX3N0ZXAiOiA4LAogICAgICAgICJsb3NzX2hpc3RvcnkiOiBbCiAgICAgICAgICAzLjUzNzE5NzU4OTg3NDI2NzYsCiAgICAgICAgICAzLjQzNDQ1NzU0MDUxMjA4NSwKICAgICAgICAgIDMuNTk3NzA2NTU2MzIwMTkwNCwKICAgICAgICAgIDMuNTYwNzQ2NjY5NzY5Mjg3LAogICAgICAgICAgMy41OTA0NzkxMzU1MTMzMDU3LAogICAgICAgICAgMy42MDkxMTA4MzIyMTQzNTU1LAogICAgICAgICAgMy41MjEzNjYxMTkzODQ3NjU2LAogICAgICAgICAgMy44NjU5MzUwODcyMDM5Nzk1CiAgICAgICAgXSwKICAgICAgICAib3B0aW1pemVyX3NoYTI1NiI6ICJlODAzMTE0YjUwNTYwNzBkNzVhM2YwMmY2YTFjZDk4N2Y2MmIwZDg0ZmNiNTMzNTBiYjQzZTg0NzU3ZjI5ZWZhIiwKICAgICAgICAic2NoZWR1bGVyX3NoYTI1NiI6ICJjYWE4MTdmYjMxOTFhYjE0NTZhZGUwMDMyMDU2NWZiM2RmYjdlN2U2NDhhMTIwN2YzZjIyZjA0ODkzZGVjNzcwIiwKICAgICAgICAidHJhaW5hYmxlX3N0YXRlX3NoYTI1NiI6ICJkMjg1NDdlODJkYzQxMmQ1ODA2MGU4YmU2NGRlYjUyMTkxYjdiMjU4NTYxYmU0Nzg3NDY5NGIxYzU0NmVjYTY2IgogICAgICB9LAogICAgICAiZmlyc3RfY29tcGxldGVkX3N0ZXAiOiA1LAogICAgICAiZmlyc3RfcmVzdW1lZF9iYXRjaF9zdGVwIjogNCwKICAgICAgInJlc3RvcmVkX2dsb2JhbF9zdGVwIjogNCwKICAgICAgInNjaGVtYV92ZXJzaW9uIjogInJlY292ZXJ5LXdvcmtlci1yZXN1bHQtdjEiLAogICAgICAic3RhcnRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjAzLjE4NjY3MVoiLAogICAgICAic3RyYXRlZ3kiOiAibWlzc2luZ190cmFpbmluZ19zdGF0ZSIsCiAgICAgICJ3b3JrZXJfcGlkIjogMTY2MDAKICAgIH0sCiAgICAicmVjb3ZlcnlfcHJvY2VzcyI6IHsKICAgICAgImNvbXBsZXRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjA1LjA4ODYzMVoiLAogICAgICAiZXhpdF9jb2RlIjogMCwKICAgICAgImV4aXRfdmVyaWZpZWQiOiB0cnVlLAogICAgICAic3RhcnRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI4OjU5LjE3OTIwMVoiLAogICAgICAid29ya2VyX3BpZCI6IDE2NjAwCiAgICB9LAogICAgInJlc3VsdF9wYXRoIjogInJlc3VsdC5qc29uIiwKICAgICJydW5faWQiOiAiaW5pdGlhbCIsCiAgICAic2NoZW1hX3ZlcnNpb24iOiAiY3Jhc2gtZXhwZXJpbWVudC12MSIsCiAgICAic3RyYXRlZ3kiOiAibWlzc2luZ190cmFpbmluZ19zdGF0ZSIKICB9LAogICJsaW1pdGF0aW9ucyI6IFsKICAgICJObyBsaXZlIEFQSSBjYWxsIG9jY3VyczsgdGhlIGRpYWdub3NpcyBpcyBhbiBhY2NlcHRlZCBHUFQtNS42IGNhcHR1cmUgcmVwbGF5LiIsCiAgICAiQSBmYWlsZWQgcmVwYWlyZWQgZ2F0ZSBzdG9wcyBjbG9zZWQgd2l0aG91dCBhbm90aGVyIGRpYWdub3NpcyBvciByZXBhaXIgYXR0ZW1wdC4iLAogICAgInNhZmVfZnVsbCByZW1haW5zIHRoZSBkb2N1bWVudGVkIGNvbXBsZXRlLXN0YXRlIGZhbGxiYWNrIGFuZCBpcyBub3QgYXV0by1leGVjdXRlZC4iLAogICAgIldpbmRvd3MgZGlyZWN0b3J5IGZzeW5jIHJlbWFpbnMgYmVzdC1lZmZvcnQgYmVjYXVzZSBQeXRob24gZG9lcyBub3QgZXhwb3NlIGl0LiIKICBdLAogICJvcmlnaW5hbF9jaGVja3BvaW50X2FmdGVyIjogewogICAgImZpbGVfY291bnQiOiA1LAogICAgImxvZ2ljYWxfYnl0ZXMiOiA1MTY5LAogICAgInNoYTI1NiI6ICI3NTQ4YmE4OWVhMThiM2I3OGYxZWE4OTkwZGNjYTY2YTFiM2NiMDE5YzRjZmM3MTJjNDE4YjJkZTliYmVlY2FhIgogIH0sCiAgIm9yaWdpbmFsX2NoZWNrcG9pbnRfYmVmb3JlIjogewogICAgImZpbGVfY291bnQiOiA1LAogICAgImxvZ2ljYWxfYnl0ZXMiOiA1MTY5LAogICAgInNoYTI1NiI6ICI3NTQ4YmE4OWVhMThiM2I3OGYxZWE4OTkwZGNjYTY2YTFiM2NiMDE5YzRjZmM3MTJjNDE4YjJkZTliYmVlY2FhIgogIH0sCiAgIm9yaWdpbmFsX2NoZWNrcG9pbnRfdW5tb2RpZmllZCI6IHRydWUsCiAgInBsYW5fdmFsaWRhdGlvbiI6IHsKICAgICJhY2NlcHRlZF9hY3Rpb25zIjogWwogICAgICAicGVyc2lzdF9vcHRpbWl6ZXJfc3RhdGUiLAogICAgICAicGVyc2lzdF9zY2hlZHVsZXJfc3RhdGUiLAogICAgICAicGVyc2lzdF9weXRob25fcm5nX3N0YXRlIiwKICAgICAgInBlcnNpc3RfbnVtcHlfcm5nX3N0YXRlIiwKICAgICAgInBlcnNpc3RfdG9yY2hfcm5nX3N0YXRlIiwKICAgICAgInJlc3RvcmVfc3RhdGVfYmVmb3JlX25leHRfYmF0Y2giCiAgICBdLAogICAgImF0dGVtcHRfbnVtYmVyIjogMSwKICAgICJkZWNpc2lvbnMiOiBbCiAgICAgIHsKICAgICAgICAiYWN0aW9uIjogImNoYW5nZV9zdXBwb3J0ZWRfY2hlY2twb2ludF9zdHJhdGVneSIsCiAgICAgICAgImRpc3Bvc2l0aW9uIjogInVuc3VwcG9ydGVkIiwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgImNvbnRyYWN0Om1hbmRhdG9yeS1zdGF0ZSIKICAgICAgICBdLAogICAgICAgICJyZWFzb24iOiAiS25vd24gYWN0aW9uIGlzIHVuc3VwcG9ydGVkIGJ5IE5hdGl2ZVB5VG9yY2hBZGFwdGVyIGluIFAwLiIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3Rpb24iOiAicGVyc2lzdF9vcHRpbWl6ZXJfc3RhdGUiLAogICAgICAgICJkaXNwb3NpdGlvbiI6ICJhY2NlcHRlZCIsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJyZXN0b3JlOm9wdGltaXplci1zdGF0ZSIsCiAgICAgICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIiwKICAgICAgICAgICJ0cmFqZWN0b3J5OmZpbmFsLXRyYWluYWJsZSIsCiAgICAgICAgICAidHJhamVjdG9yeTpsb3NzLWhpc3RvcnkiCiAgICAgICAgXSwKICAgICAgICAicmVhc29uIjogIlR5cGVkIGFjdGlvbiBpcyBzdXBwb3J0ZWQgYW5kIGxpbmtlZCB0byByZXF1ZXN0IGV2aWRlbmNlLiIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3Rpb24iOiAicGVyc2lzdF9zY2hlZHVsZXJfc3RhdGUiLAogICAgICAgICJkaXNwb3NpdGlvbiI6ICJhY2NlcHRlZCIsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJyZXN0b3JlOnNjaGVkdWxlci1zdGF0ZSIsCiAgICAgICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIiwKICAgICAgICAgICJ0cmFqZWN0b3J5OmZpbmFsLXRyYWluYWJsZSIsCiAgICAgICAgICAidHJhamVjdG9yeTpsb3NzLWhpc3RvcnkiCiAgICAgICAgXSwKICAgICAgICAicmVhc29uIjogIlR5cGVkIGFjdGlvbiBpcyBzdXBwb3J0ZWQgYW5kIGxpbmtlZCB0byByZXF1ZXN0IGV2aWRlbmNlLiIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3Rpb24iOiAicGVyc2lzdF9weXRob25fcm5nX3N0YXRlIiwKICAgICAgICAiZGlzcG9zaXRpb24iOiAiYWNjZXB0ZWQiLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAicmVzdG9yZTpweXRob24tcm5nIiwKICAgICAgICAgICJjb250cmFjdDptYW5kYXRvcnktc3RhdGUiCiAgICAgICAgXSwKICAgICAgICAicmVhc29uIjogIlR5cGVkIGFjdGlvbiBpcyBzdXBwb3J0ZWQgYW5kIGxpbmtlZCB0byByZXF1ZXN0IGV2aWRlbmNlLiIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3Rpb24iOiAicGVyc2lzdF9udW1weV9ybmdfc3RhdGUiLAogICAgICAgICJkaXNwb3NpdGlvbiI6ICJhY2NlcHRlZCIsCiAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICJyZXN0b3JlOm51bXB5LXJuZyIsCiAgICAgICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIgogICAgICAgIF0sCiAgICAgICAgInJlYXNvbiI6ICJUeXBlZCBhY3Rpb24gaXMgc3VwcG9ydGVkIGFuZCBsaW5rZWQgdG8gcmVxdWVzdCBldmlkZW5jZS4iCiAgICAgIH0sCiAgICAgIHsKICAgICAgICAiYWN0aW9uIjogInBlcnNpc3RfdG9yY2hfcm5nX3N0YXRlIiwKICAgICAgICAiZGlzcG9zaXRpb24iOiAiYWNjZXB0ZWQiLAogICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAicmVzdG9yZTp0b3JjaC1ybmciLAogICAgICAgICAgImNvbnRyYWN0Om1hbmRhdG9yeS1zdGF0ZSIsCiAgICAgICAgICAidHJhamVjdG9yeTpmaW5hbC10cmFpbmFibGUiLAogICAgICAgICAgInRyYWplY3Rvcnk6ZmluYWwtZXZhbHVhdGlvbiIsCiAgICAgICAgICAidHJhamVjdG9yeTpsb3NzLWhpc3RvcnkiCiAgICAgICAgXSwKICAgICAgICAicmVhc29uIjogIlR5cGVkIGFjdGlvbiBpcyBzdXBwb3J0ZWQgYW5kIGxpbmtlZCB0byByZXF1ZXN0IGV2aWRlbmNlLiIKICAgICAgfSwKICAgICAgewogICAgICAgICJhY3Rpb24iOiAicmVzdG9yZV9zdGF0ZV9iZWZvcmVfbmV4dF9iYXRjaCIsCiAgICAgICAgImRpc3Bvc2l0aW9uIjogImFjY2VwdGVkIiwKICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgInJlc3RvcmU6b3B0aW1pemVyLXN0YXRlIiwKICAgICAgICAgICJyZXN0b3JlOnNjaGVkdWxlci1zdGF0ZSIsCiAgICAgICAgICAicmVzdG9yZTpweXRob24tcm5nIiwKICAgICAgICAgICJyZXN0b3JlOm51bXB5LXJuZyIsCiAgICAgICAgICAicmVzdG9yZTp0b3JjaC1ybmciLAogICAgICAgICAgInByb2Nlc3M6bmV4dC1zdGVwIgogICAgICAgIF0sCiAgICAgICAgInJlYXNvbiI6ICJUeXBlZCBhY3Rpb24gaXMgc3VwcG9ydGVkIGFuZCBsaW5rZWQgdG8gcmVxdWVzdCBldmlkZW5jZS4iCiAgICAgIH0KICAgIF0sCiAgICAiZXhlY3V0aW9uX3BlcmZvcm1lZCI6IGZhbHNlLAogICAgInJlamVjdGVkX2FjdGlvbnMiOiBbXSwKICAgICJzY2hlbWFfdmVyc2lvbiI6ICJyZXBhaXItcGxhbi12YWxpZGF0aW9uLXYxIiwKICAgICJ1bnN1cHBvcnRlZF9hY3Rpb25zIjogWwogICAgICAiY2hhbmdlX3N1cHBvcnRlZF9jaGVja3BvaW50X3N0cmF0ZWd5IgogICAgXQogIH0sCiAgInByb2ZpbGUiOiAiY2kiLAogICJwcm9wb3NlZF9hbmFseXNpcyI6IHsKICAgICJhZmZlY3RlZF9nYXRlX2NoZWNrcyI6IFsKICAgICAgInN0YXRlLm9wdGltaXplciIsCiAgICAgICJzdGF0ZS5zY2hlZHVsZXIiLAogICAgICAic3RhdGUucHl0aG9uX3JuZyIsCiAgICAgICJzdGF0ZS5udW1weV9ybmciLAogICAgICAic3RhdGUudG9yY2hfcm5nIiwKICAgICAgInRyYWplY3RvcnkuZmluYWxfdHJhaW5hYmxlIiwKICAgICAgInRyYWplY3RvcnkuZmluYWxfZXZhbHVhdGlvbiIsCiAgICAgICJ0cmFqZWN0b3J5Lmxvc3NfaGlzdG9yeSIsCiAgICAgICJjb250cmFjdC5ub19tYW5kYXRvcnlfb21pc3Npb24iCiAgICBdLAogICAgImNvbmZpZGVuY2UiOiAiaGlnaCIsCiAgICAiY29uZmlybWluZ19ldmlkZW5jZSI6IFsKICAgICAgInJlc3RvcmU6b3B0aW1pemVyLXN0YXRlIiwKICAgICAgInJlc3RvcmU6c2NoZWR1bGVyLXN0YXRlIiwKICAgICAgInJlc3RvcmU6cHl0aG9uLXJuZyIsCiAgICAgICJyZXN0b3JlOm51bXB5LXJuZyIsCiAgICAgICJyZXN0b3JlOnRvcmNoLXJuZyIsCiAgICAgICJ0cmFqZWN0b3J5OmZpbmFsLXRyYWluYWJsZSIsCiAgICAgICJ0cmFqZWN0b3J5OmZpbmFsLWV2YWx1YXRpb24iLAogICAgICAidHJhamVjdG9yeTpsb3NzLWhpc3RvcnkiLAogICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIgogICAgXSwKICAgICJsaW1pdGF0aW9ucyI6IFsKICAgICAgIlRoZSBwYWNrYWdlIGRlbW9uc3RyYXRlcyB0aGUgb21pc3Npb25zIGFuZCByZXN1bHRpbmcgZGl2ZXJnZW5jZSBidXQgZG9lcyBub3QgZXN0YWJsaXNoIHRoYXQgYW55IHByb3Bvc2VkIHJlcGFpciBoYXMgYmVlbiBpbXBsZW1lbnRlZCBvciB2YWxpZGF0ZWQuIiwKICAgICAgIkV4YWN0IHJlY292ZXJ5IHJlbWFpbnMgc3ViamVjdCB0byBkZXRlcm1pbmlzdGljIHZhbGlkYXRpb24gdXNpbmcgYSBuZXdseSBwcm9kdWNlZCBjaGVja3BvaW50IGNvbnRhaW5pbmcgYWxsIG1hbmRhdG9yeSBzdGF0ZS4iLAogICAgICAiVGhlIG1hdGNoaW5nIFB5dGhvbiBhbmQgTnVtUHkgUk5HIGRpZ2VzdHMgZG8gbm90IHNhdGlzZnkgdGhlIHNlcmlhbGl6YXRpb24gcmVxdWlyZW1lbnQgYmVjYXVzZSB0aG9zZSBzdGF0ZXMgd2VyZSBub3QgcHJlc2VudCBpbiB0aGUgY2hlY2twb2ludC4iCiAgICBdLAogICAgInJlcGFpcl9wbGFuIjogewogICAgICAiYWN0aW9ucyI6IFsKICAgICAgICB7CiAgICAgICAgICAiYWN0aW9uIjogImNoYW5nZV9zdXBwb3J0ZWRfY2hlY2twb2ludF9zdHJhdGVneSIsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIgogICAgICAgICAgXSwKICAgICAgICAgICJyZWFzb24iOiAiVGhlIGN1cnJlbnQgc3RyYXRlZ3kgYWR2ZXJ0aXNlcyBubyBzdXBwb3J0ZWQgcmVwYWlyIGFjdGlvbnMgYW5kIG11c3QgYmUgcmVwbGFjZWQgb3IgZXh0ZW5kZWQgdG8gc3VwcG9ydCBhbGwgbWFuZGF0b3J5IGNvbnRpbnVhdGlvbiBzdGF0ZS4iCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0aW9uIjogInBlcnNpc3Rfb3B0aW1pemVyX3N0YXRlIiwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJyZXN0b3JlOm9wdGltaXplci1zdGF0ZSIsCiAgICAgICAgICAgICJjb250cmFjdDptYW5kYXRvcnktc3RhdGUiLAogICAgICAgICAgICAidHJhamVjdG9yeTpmaW5hbC10cmFpbmFibGUiLAogICAgICAgICAgICAidHJhamVjdG9yeTpsb3NzLWhpc3RvcnkiCiAgICAgICAgICBdLAogICAgICAgICAgInJlYXNvbiI6ICJTZXJpYWxpemUgdGhlIGNvbXBsZXRlIG9wdGltaXplciBzdGF0ZSByZXF1aXJlZCBmb3IgZXhhY3QgY29udGludWF0aW9uLiIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3Rpb24iOiAicGVyc2lzdF9zY2hlZHVsZXJfc3RhdGUiLAogICAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICAgInJlc3RvcmU6c2NoZWR1bGVyLXN0YXRlIiwKICAgICAgICAgICAgImNvbnRyYWN0Om1hbmRhdG9yeS1zdGF0ZSIsCiAgICAgICAgICAgICJ0cmFqZWN0b3J5OmZpbmFsLXRyYWluYWJsZSIsCiAgICAgICAgICAgICJ0cmFqZWN0b3J5Omxvc3MtaGlzdG9yeSIKICAgICAgICAgIF0sCiAgICAgICAgICAicmVhc29uIjogIlNlcmlhbGl6ZSBzY2hlZHVsZXIgcHJvZ3Jlc3Mgc28gcmVzdW1lZCBsZWFybmluZy1yYXRlIGJlaGF2aW9yIG1hdGNoZXMgdGhlIHVuaW50ZXJydXB0ZWQgcnVuLiIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3Rpb24iOiAicGVyc2lzdF9weXRob25fcm5nX3N0YXRlIiwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJyZXN0b3JlOnB5dGhvbi1ybmciLAogICAgICAgICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIgogICAgICAgICAgXSwKICAgICAgICAgICJyZWFzb24iOiAiU2VyaWFsaXplIFB5dGhvbiBSTkcgc3RhdGUgYmVjYXVzZSB0aGUgd29ya2xvYWQgcmVxdWlyZXMgaXQgZm9yIHN0cmljdCBjb250aW51YXRpb24uIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdGlvbiI6ICJwZXJzaXN0X251bXB5X3JuZ19zdGF0ZSIsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAicmVzdG9yZTpudW1weS1ybmciLAogICAgICAgICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIgogICAgICAgICAgXSwKICAgICAgICAgICJyZWFzb24iOiAiU2VyaWFsaXplIE51bVB5IFJORyBzdGF0ZSBiZWNhdXNlIHRoZSB3b3JrbG9hZCB1c2VzIE51bVB5IHJhbmRvbW5lc3MuIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdGlvbiI6ICJwZXJzaXN0X3RvcmNoX3JuZ19zdGF0ZSIsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAicmVzdG9yZTp0b3JjaC1ybmciLAogICAgICAgICAgICAiY29udHJhY3Q6bWFuZGF0b3J5LXN0YXRlIiwKICAgICAgICAgICAgInRyYWplY3Rvcnk6ZmluYWwtdHJhaW5hYmxlIiwKICAgICAgICAgICAgInRyYWplY3Rvcnk6ZmluYWwtZXZhbHVhdGlvbiIsCiAgICAgICAgICAgICJ0cmFqZWN0b3J5Omxvc3MtaGlzdG9yeSIKICAgICAgICAgIF0sCiAgICAgICAgICAicmVhc29uIjogIlNlcmlhbGl6ZSBUb3JjaCBSTkcgc3RhdGUgYmVjYXVzZSB0aGUgd29ya2xvYWQgdXNlcyBUb3JjaCByYW5kb21uZXNzIGFuZCBkcm9wb3V0LiIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3Rpb24iOiAicmVzdG9yZV9zdGF0ZV9iZWZvcmVfbmV4dF9iYXRjaCIsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAicmVzdG9yZTpvcHRpbWl6ZXItc3RhdGUiLAogICAgICAgICAgICAicmVzdG9yZTpzY2hlZHVsZXItc3RhdGUiLAogICAgICAgICAgICAicmVzdG9yZTpweXRob24tcm5nIiwKICAgICAgICAgICAgInJlc3RvcmU6bnVtcHktcm5nIiwKICAgICAgICAgICAgInJlc3RvcmU6dG9yY2gtcm5nIiwKICAgICAgICAgICAgInByb2Nlc3M6bmV4dC1zdGVwIgogICAgICAgICAgXSwKICAgICAgICAgICJyZWFzb24iOiAiUmVzdG9yZSBhbGwgcGVyc2lzdGVkIG9wdGltaXplciwgc2NoZWR1bGVyLCBhbmQgUk5HIHN0YXRlIGJlZm9yZSBwcm9jZXNzaW5nIHRoZSBuZXh0IGJhdGNoLiIKICAgICAgICB9CiAgICAgIF0sCiAgICAgICJhc3N1bXB0aW9ucyI6IFsKICAgICAgICAiVGhlIGNvbnRyb2xsZWQgQ1BVLW9ubHkgd29ya2xvYWQgYW5kIGRlY2xhcmVkIHN0YXRlIHJlcXVpcmVtZW50cyByZW1haW4gdW5jaGFuZ2VkLiIsCiAgICAgICAgIk5vIENVREEgUk5HIHN0YXRlIGlzIHJlcXVpcmVkLiIsCiAgICAgICAgIkJhdGNoIHBvc2l0aW9uIHJlbWFpbnMgZGVyaXZhYmxlIGZyb20gdGhlIHJlc3RvcmVkIGdsb2JhbCBzdGVwLiIKICAgICAgXSwKICAgICAgImV4cGVjdGVkX2dhdGVfaW1wcm92ZW1lbnRzIjogWwogICAgICAgICJNYW5kYXRvcnkgY29udGludWF0aW9uIHN0YXRlIGlzIGRlY2xhcmVkIGFuZCBzZXJpYWxpemVkLiIsCiAgICAgICAgIk9wdGltaXplciwgc2NoZWR1bGVyLCBhbmQgcmVxdWlyZWQgUk5HIHN0YXRlcyBiZWNvbWUgcmVzdG9yYWJsZSB3aXRoIGV4YWN0IGRpZ2VzdHMuIiwKICAgICAgICAiQ29udGludWVkIGxvc3NlcywgZmluYWwgdHJhaW5hYmxlIHBhcmFtZXRlcnMsIGFuZCBmaW5hbCBldmFsdWF0aW9uIG91dHB1dHMgY2FuIGJlIHJlLWV2YWx1YXRlZCBmb3IgZXhhY3QgYWdyZWVtZW50LiIKICAgICAgXSwKICAgICAgInJpc2tzIjogWwogICAgICAgICJUaGUgY3VycmVudCBjaGVja3BvaW50IHN0cmF0ZWd5IGV4cG9zZXMgbm8gc3VwcG9ydGVkIHJlcGFpciBhY3Rpb25zLCBzbyBhIGNvbXBhdGlibGUgc3RyYXRlZ3kgb3IgaW1wbGVtZW50YXRpb24gY2hhbmdlIGlzIHJlcXVpcmVkIGJlZm9yZSB0aGVzZSBhY3Rpb25zIGNhbiBiZSB2YWxpZGF0ZWQuIiwKICAgICAgICAiRXhpc3RpbmcgY2hlY2twb2ludHMgbGFja2luZyB0aGUgb21pdHRlZCBzdGF0ZSBjYW5ub3QgcHJvdmlkZSBzdHJpY3QgY29udGludWF0aW9uIGZyb20gdGhvc2UgY2hlY2twb2ludHMuIiwKICAgICAgICAiUmVzdG9yYXRpb24gb3JkZXJpbmcgZXJyb3JzIGNvdWxkIHN0aWxsIHByb2R1Y2UgdHJhamVjdG9yeSBkaXZlcmdlbmNlIGV2ZW4gYWZ0ZXIgYWxsIHN0YXRlIGlzIHNlcmlhbGl6ZWQuIgogICAgICBdCiAgICB9LAogICAgInJvb3RfY2F1c2VfaHlwb3RoZXNpcyI6ICJUaGUgY2hlY2twb2ludCBzdHJhdGVneSBzZXJpYWxpemVkIHRoZSBhZGFwdGVyIGFuZCBnbG9iYWwgc3RlcCBidXQgb21pdHRlZCBtYW5kYXRvcnkgb3B0aW1pemVyLCBzY2hlZHVsZXIsIFB5dGhvbiBSTkcsIE51bVB5IFJORywgYW5kIFRvcmNoIFJORyBzdGF0ZS4gUmVjb3ZlcnkgdGhlcmVmb3JlIHJlc3VtZWQgd2l0aCBpbmNvbXBsZXRlIGNvbnRpbnVhdGlvbiBzdGF0ZSwgY2F1c2luZyBkaXZlcmdlbmNlIGluIGxvc3NlcywgZmluYWwgdHJhaW5hYmxlIHBhcmFtZXRlcnMsIGFuZCBmaW5hbCBldmFsdWF0aW9uIG91dHB1dHMuIiwKICAgICJzY2hlbWFfdmVyc2lvbiI6ICJmYWlsdXJlLWFuYWx5c2lzLXYyIgogIH0sCiAgInJlcGFpcl9hdHRlbXB0X2NvdW50IjogMSwKICAicmVwYWlyX2V4ZWN1dGlvbiI6IHsKICAgICJhZG1pdHRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjA1LjE5MTUwOVoiLAogICAgImFwcGxpZWRfYWN0aW9ucyI6IFsKICAgICAgInBlcnNpc3Rfb3B0aW1pemVyX3N0YXRlIiwKICAgICAgInBlcnNpc3Rfc2NoZWR1bGVyX3N0YXRlIiwKICAgICAgInBlcnNpc3RfcHl0aG9uX3JuZ19zdGF0ZSIsCiAgICAgICJwZXJzaXN0X251bXB5X3JuZ19zdGF0ZSIsCiAgICAgICJwZXJzaXN0X3RvcmNoX3JuZ19zdGF0ZSIsCiAgICAgICJyZXN0b3JlX3N0YXRlX2JlZm9yZV9uZXh0X2JhdGNoIgogICAgXSwKICAgICJhdHRlbXB0X251bWJlciI6IDEsCiAgICAiZXhlY3V0aW9uX3BlcmZvcm1lZCI6IHRydWUsCiAgICAib3JpZ2luYWxfY29uZmlnIjogewogICAgICAiaW5jbHVkZV9udW1weV9ybmciOiBmYWxzZSwKICAgICAgImluY2x1ZGVfb3B0aW1pemVyIjogZmFsc2UsCiAgICAgICJpbmNsdWRlX3B5dGhvbl9ybmciOiBmYWxzZSwKICAgICAgImluY2x1ZGVfc2NoZWR1bGVyIjogZmFsc2UsCiAgICAgICJpbmNsdWRlX3RvcmNoX3JuZyI6IGZhbHNlLAogICAgICAicmVzdG9yZV9iZWZvcmVfbmV4dF9iYXRjaCI6IGZhbHNlLAogICAgICAic2NoZW1hX3ZlcnNpb24iOiAiY2hlY2twb2ludC1zdHJhdGVneS1jb25maWctdjEiLAogICAgICAic3RyYXRlZ3lfaWQiOiAibmF0aXZlLWluY29tcGxldGUtdjEiCiAgICB9LAogICAgInJlamVjdGVkX2FjdGlvbnMiOiBbXSwKICAgICJyZXBhaXJlZF9jb25maWciOiB7CiAgICAgICJpbmNsdWRlX251bXB5X3JuZyI6IHRydWUsCiAgICAgICJpbmNsdWRlX29wdGltaXplciI6IHRydWUsCiAgICAgICJpbmNsdWRlX3B5dGhvbl9ybmciOiB0cnVlLAogICAgICAiaW5jbHVkZV9zY2hlZHVsZXIiOiB0cnVlLAogICAgICAiaW5jbHVkZV90b3JjaF9ybmciOiB0cnVlLAogICAgICAicmVzdG9yZV9iZWZvcmVfbmV4dF9iYXRjaCI6IHRydWUsCiAgICAgICJzY2hlbWFfdmVyc2lvbiI6ICJjaGVja3BvaW50LXN0cmF0ZWd5LWNvbmZpZy12MSIsCiAgICAgICJzdHJhdGVneV9pZCI6ICJuYXRpdmUtcmVwYWlyZWQtY29tcGxldGUtdjEiCiAgICB9LAogICAgInNjaGVtYV92ZXJzaW9uIjogInJlcGFpci1leGVjdXRpb24tdjEiLAogICAgInVuc3VwcG9ydGVkX2FjdGlvbnMiOiBbCiAgICAgICJjaGFuZ2Vfc3VwcG9ydGVkX2NoZWNrcG9pbnRfc3RyYXRlZ3kiCiAgICBdCiAgfSwKICAicmVwYWlyZWRfcnVuIjogewogICAgImNvbnRyb2wiOiB7CiAgICAgICJldmFsdWF0aW9uX3NoYTI1NiI6ICJhNDJhNmQyNWM4YWFmNjY3NDEzMGVmNjM0MzlmNmZkNDE1ODI0YmQyM2ZmOWNkNmE3YzBjYTAzMDViZTNlZjlhIiwKICAgICAgImdsb2JhbF9zdGVwIjogOCwKICAgICAgImxvc3NfaGlzdG9yeSI6IFsKICAgICAgICAzLjUzNzE5NzU4OTg3NDI2NzYsCiAgICAgICAgMy40MzQ0NTc1NDA1MTIwODUsCiAgICAgICAgMy41OTc3MDY1NTYzMjAxOTA0LAogICAgICAgIDMuNTYwNzQ2NjY5NzY5Mjg3LAogICAgICAgIDMuNjcwODIzNTc0MDY2MTYyLAogICAgICAgIDMuNjI3MjUzMjkzOTkxMDg5LAogICAgICAgIDMuNTA4NjM5MzM1NjMyMzI0LAogICAgICAgIDMuODI0ODE0MzE5NjEwNTk1NwogICAgICBdLAogICAgICAib3B0aW1pemVyX3NoYTI1NiI6ICJjMDNkZmM4YjY2ZTY2NDVmYjU1MjIyMzQyOGFkODZhODU1Yzk3MDQ5ZDEzM2IwODk4NDYwNGY2ZTdkNTVhMDUwIiwKICAgICAgInNjaGVkdWxlcl9zaGEyNTYiOiAiZTA3ZmZkNmE4OWZlZmI2MWU4MGQxY2E1NjAyNWE5MjcyMjJhODMxODBmZmNlZDc3ODc4OTYwNmQzYTdiZWM4MSIsCiAgICAgICJ0cmFpbmFibGVfc3RhdGVfc2hhMjU2IjogIjFmYzcyZmRmMjE0ODdhZmU3YjMyZGE4MzNkMjMwMGNkOWE2OGYwYzBjNmYzY2UxNDU2OTEwYTUxMDJhOTI5OTciCiAgICB9LAogICAgImNyYXNoIjogewogICAgICAiY2hlY2twb2ludF9wYXRoIjogImNoZWNrcG9pbnRzL3JlcGFpcmVkL25hdGl2ZS1yZXBhaXJlZC1jb21wbGV0ZS12MS9jaGVja3BvaW50LXN0ZXAtMDAwMDA0IiwKICAgICAgImNoZWNrcG9pbnRfc3RlcCI6IDQsCiAgICAgICJldmVudF9yZWNlaXZlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjA4LjkyMTg1NloiLAogICAgICAibGFzdF9jb21wbGV0ZWRfc3RlcCI6IDQsCiAgICAgICJ0ZXJtaW5hdGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjk6MDguOTQ0MjM5WiIsCiAgICAgICJ0ZXJtaW5hdGlvbl9leGl0X2NvZGUiOiAxLAogICAgICAidGVybWluYXRpb25fbWV0aG9kIjogIlRlcm1pbmF0ZVByb2Nlc3MgdmlhIHN1YnByb2Nlc3MuUG9wZW4ua2lsbCIsCiAgICAgICJ0ZXJtaW5hdGlvbl92ZXJpZmllZCI6IHRydWUsCiAgICAgICJ3b3JrZXJfcGlkIjogMjc2MzIKICAgIH0sCiAgICAiY3JlYXRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjEyLjkyNTI0M1oiLAogICAgImZhaWx1cmVfYXJ0aWZhY3RfcGF0aCI6IG51bGwsCiAgICAiZ2F0ZSI6IHsKICAgICAgImFjaGlldmVkX3JvbGxiYWNrX3N0ZXBzIjogMCwKICAgICAgImNoZWNrcyI6IFsKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogImNoZWNrcG9pbnQtbWFuaWZlc3QtdjEiLAogICAgICAgICAgImNhdGVnb3J5IjogIkludGVncml0eSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAiaW50ZWdyaXR5Lm1hbmlmZXN0X3NjaGVtYSIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAibWFuaWZlc3Q6c2NoZW1hIgogICAgICAgICAgXSwKICAgICAgICAgICJleHBlY3RlZCI6ICJjaGVja3BvaW50LW1hbmlmZXN0LXYxIiwKICAgICAgICAgICJsYWJlbCI6ICJNYW5pZmVzdCBzY2hlbWEgdmFsaWQiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJwcmVzZW50IiwKICAgICAgICAgICJjYXRlZ29yeSI6ICJJbnRlZ3JpdHkiLAogICAgICAgICAgImNoZWNrX2lkIjogImludGVncml0eS5jb21wbGV0aW9uX21hcmtlciIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAiaW50ZWdyaXR5OmNvbXBsZXRpb24tbWFya2VyIgogICAgICAgICAgXSwKICAgICAgICAgICJleHBlY3RlZCI6ICJDT01QTEVURSBwcmVzZW50IGluIGZpbmFsIGNoZWNrcG9pbnQiLAogICAgICAgICAgImxhYmVsIjogIkNvbXBsZXRpb24gbWFya2VyIHByZXNlbnQiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICI1IHBheWxvYWRzIHZhbGlkYXRlZCIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgICAgICJjaGVja19pZCI6ICJpbnRlZ3JpdHkuY2hlY2tzdW1zIiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJpbnRlZ3JpdHk6c2hhMjU2IgogICAgICAgICAgXSwKICAgICAgICAgICJleHBlY3RlZCI6ICJldmVyeSBtYW5pZmVzdCBwYXlsb2FkIG1hdGNoZXMgU0hBLTI1NiBhbmQgc2l6ZSIsCiAgICAgICAgICAibGFiZWwiOiAiQWxsIHBheWxvYWQgY2hlY2tzdW1zIHZhbGlkIiwKICAgICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAicHJlc2VudCIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgICAgICJjaGVja19pZCI6ICJpbnRlZ3JpdHkuYmFzZV9wcmVzZW50IiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJiYXNlOnByZXNlbmNlIgogICAgICAgICAgXSwKICAgICAgICAgICJleHBlY3RlZCI6ICJjb250YWluZWQgaW1tdXRhYmxlIGJhc2UgYXJ0aWZhY3QiLAogICAgICAgICAgImxhYmVsIjogIkJhc2UgYXJ0aWZhY3QgcHJlc2VudCB3aGVuIHJlcXVpcmVkIiwKICAgICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAiYzE3Y2M4OTk0YzhmMGZlNmRlZjMyNDIzYjBlNWQ5ZWZlZGZmYjNjZDcxYzdkZTk2MzFmMjZjZjUwNTkyNWQ4NiIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiSW50ZWdyaXR5IiwKICAgICAgICAgICJjaGVja19pZCI6ICJpbnRlZ3JpdHkuYmFzZV9oYXNoIiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJiYXNlOnNoYTI1NiIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiYzE3Y2M4OTk0YzhmMGZlNmRlZjMyNDIzYjBlNWQ5ZWZlZGZmYjNjZDcxYzdkZTk2MzFmMjZjZjUwNTkyNWQ4NiIsCiAgICAgICAgICAibGFiZWwiOiAiQmFzZSBhcnRpZmFjdCBoYXNoIG1hdGNoZXMiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJtYW5pZmVzdD00LCBldmVudD00LCByZXN0b3JlZD00IiwKICAgICAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUuZ2xvYmFsX3N0ZXAiLAogICAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICAgIm1hbmlmZXN0Omdsb2JhbC1zdGVwIgogICAgICAgICAgXSwKICAgICAgICAgICJleHBlY3RlZCI6ICIwIDwgc3RlcCA8IDgsIGNvbnNpc3RlbnQgYWNyb3NzIHJlc3RvcmUiLAogICAgICAgICAgImxhYmVsIjogIkNoZWNrcG9pbnQgZ2xvYmFsIHN0ZXAgaXMgdmFsaWQiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJzZXJpYWxpemVkPVRydWUsIGRpZ2VzdF9tYXRjaD1UcnVlIiwKICAgICAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUubW9kZWxfb3JfYWRhcHRlciIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAicmVzdG9yZTptb2RlbC1zdGF0ZSIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBhZGFwdGVyIGFuZCBleGFjdCB0cmFpbmFibGUtc3RhdGUgZGlnZXN0IiwKICAgICAgICAgICJsYWJlbCI6ICJNb2RlbCBvciBhZGFwdGVyIHN0YXRlIHJlc3RvcmVzIiwKICAgICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAic2VyaWFsaXplZD1UcnVlLCBkaWdlc3RfbWF0Y2g9VHJ1ZSIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiUmVxdWlyZWQgdHJhaW5pbmcgc3RhdGUiLAogICAgICAgICAgImNoZWNrX2lkIjogInN0YXRlLm9wdGltaXplciIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAicmVzdG9yZTpvcHRpbWl6ZXItc3RhdGUiCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogInNlcmlhbGl6ZWQgb3B0aW1pemVyIHdpdGggZXhhY3QgZGlnZXN0IiwKICAgICAgICAgICJsYWJlbCI6ICJPcHRpbWl6ZXIgc3RhdGUgcmVzdG9yZXMgd2hlbiByZXF1aXJlZCIsCiAgICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogInNlcmlhbGl6ZWQ9VHJ1ZSwgZGlnZXN0X21hdGNoPVRydWUiLAogICAgICAgICAgImNhdGVnb3J5IjogIlJlcXVpcmVkIHRyYWluaW5nIHN0YXRlIiwKICAgICAgICAgICJjaGVja19pZCI6ICJzdGF0ZS5zY2hlZHVsZXIiLAogICAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICAgInJlc3RvcmU6c2NoZWR1bGVyLXN0YXRlIgogICAgICAgICAgXSwKICAgICAgICAgICJleHBlY3RlZCI6ICJzZXJpYWxpemVkIHNjaGVkdWxlciB3aXRoIGV4YWN0IGRpZ2VzdCIsCiAgICAgICAgICAibGFiZWwiOiAiU2NoZWR1bGVyIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJzZXJpYWxpemVkPVRydWUsIGRpZ2VzdF9tYXRjaD1UcnVlIiwKICAgICAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUucHl0aG9uX3JuZyIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAicmVzdG9yZTpweXRob24tcm5nIgogICAgICAgICAgXSwKICAgICAgICAgICJleHBlY3RlZCI6ICJzZXJpYWxpemVkIHN0YXRlIHdpdGggZXhhY3QgZGlnZXN0IiwKICAgICAgICAgICJsYWJlbCI6ICJQeXRob24gUk5HIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJzZXJpYWxpemVkPVRydWUsIGRpZ2VzdF9tYXRjaD1UcnVlIiwKICAgICAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUubnVtcHlfcm5nIiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJyZXN0b3JlOm51bXB5LXJuZyIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBzdGF0ZSB3aXRoIGV4YWN0IGRpZ2VzdCIsCiAgICAgICAgICAibGFiZWwiOiAiTnVtUHkgUk5HIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJzZXJpYWxpemVkPVRydWUsIGRpZ2VzdF9tYXRjaD1UcnVlIiwKICAgICAgICAgICJjYXRlZ29yeSI6ICJSZXF1aXJlZCB0cmFpbmluZyBzdGF0ZSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAic3RhdGUudG9yY2hfcm5nIiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJyZXN0b3JlOnRvcmNoLXJuZyIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAic2VyaWFsaXplZCBzdGF0ZSB3aXRoIGV4YWN0IGRpZ2VzdCIsCiAgICAgICAgICAibGFiZWwiOiAiVG9yY2ggUk5HIHN0YXRlIHJlc3RvcmVzIHdoZW4gcmVxdWlyZWQiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJmaXJzdCBiYXRjaCBhdCA0LCBmaXJzdCBjb21wbGV0aW9uIGF0IDUiLAogICAgICAgICAgImNhdGVnb3J5IjogIlByb2Nlc3MgcmVjb3ZlcnkiLAogICAgICAgICAgImNoZWNrX2lkIjogInByb2Nlc3MubmV4dF9zdGVwIiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJwcm9jZXNzOm5leHQtc3RlcCIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiZmlyc3QgYmF0Y2ggYXQgNCwgZmlyc3QgY29tcGxldGlvbiBhdCA1IiwKICAgICAgICAgICJsYWJlbCI6ICJSZXN1bWVkIHJ1biBjb250aW51ZXMgZnJvbSB0aGUgZXhwZWN0ZWQgbmV4dCBzdGVwIiwKICAgICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAiMjc2MzIiLAogICAgICAgICAgImNhdGVnb3J5IjogIlByb2Nlc3MgcmVjb3ZlcnkiLAogICAgICAgICAgImNoZWNrX2lkIjogInByb2Nlc3Mub3JpZ2luYWxfcGlkIiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJwcm9jZXNzOm9yaWdpbmFsLXBpZCIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiMjc2MzIiLAogICAgICAgICAgImxhYmVsIjogIk9yaWdpbmFsIHdvcmtlciBQSUQgaXMgcmVjb3JkZWQiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJtZXRob2Q9VGVybWluYXRlUHJvY2VzcyB2aWEgc3VicHJvY2Vzcy5Qb3Blbi5raWxsLCBleGl0PTEsIHZlcmlmaWVkPVRydWUiLAogICAgICAgICAgImNhdGVnb3J5IjogIlByb2Nlc3MgcmVjb3ZlcnkiLAogICAgICAgICAgImNoZWNrX2lkIjogInByb2Nlc3MuZXhwZWN0ZWRfdGVybWluYXRpb24iLAogICAgICAgICAgImRldGFpbHMiOiBudWxsLAogICAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICAgInByb2Nlc3M6dGVybWluYXRpb24iCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogInBhcmVudCB0ZXJtaW5hdGlvbiB3aXRoIG5vbnplcm8gZXhpdCBjb2RlIiwKICAgICAgICAgICJsYWJlbCI6ICJPcmlnaW5hbCB3b3JrZXIgdGVybWluYXRpb24gaXMgdmVyaWZpZWQiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICIzMTM5NiIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAicHJvY2Vzcy5uZXdfcmVjb3ZlcnlfcGlkIiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJwcm9jZXNzOnJlY292ZXJ5LXBpZCIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiUElEIGRpZmZlcmVudCBmcm9tIDI3NjMyIiwKICAgICAgICAgICJsYWJlbCI6ICJSZWNvdmVyeSB1c2VzIGEgZGlmZmVyZW50IFBJRCIsCiAgICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogImV4aXQ9MCwgdmVyaWZpZWQ9VHJ1ZSIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiUHJvY2VzcyByZWNvdmVyeSIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAicHJvY2Vzcy5yZWNvdmVyeV9leGl0IiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJwcm9jZXNzOnJlY292ZXJ5LWV4aXQiCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogImV4aXQgY29kZSAwIiwKICAgICAgICAgICJsYWJlbCI6ICJSZWNvdmVyeSB3b3JrZXIgZXhpdHMgc3VjY2Vzc2Z1bGx5IiwKICAgICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAiMCBzdGVwcyIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiU2FmZXR5IGFuZCByb2xsYmFjayIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAicm9sbGJhY2suaGFyZF9saW1pdCIsCiAgICAgICAgICAiZGV0YWlscyI6IG51bGwsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAicm9sbGJhY2s6YWNoaWV2ZWQiCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogIjw9IDAgc3RlcHMiLAogICAgICAgICAgImxhYmVsIjogIkFjaGlldmVkIHJvbGxiYWNrIGlzIHdpdGhpbiB0aGUgaGFyZCBsaW1pdCIsCiAgICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogImQ2MDU3MmFlYTEyZjkxOTYwZjNmMDAzMGJkZmRjYTU1ZmRhZmUwNTkxNDZjNzIzMGFmOTA5NDkyMzgxMWQzMTIiLAogICAgICAgICAgImNhdGVnb3J5IjogIlRyYWplY3RvcnkgY29ycmVjdG5lc3MiLAogICAgICAgICAgImNoZWNrX2lkIjogInRyYWplY3RvcnkuY2hlY2twb2ludF9ldmFsdWF0aW9uIiwKICAgICAgICAgICJkZXRhaWxzIjogIkV4YWN0IFNIQS0yNTYgY29tcGFyaXNvbjsgbm8gbnVtZXJpY2FsIHRvbGVyYW5jZSBpcyBhcHBsaWVkLiIsCiAgICAgICAgICAiZXZpZGVuY2VfaWRzIjogWwogICAgICAgICAgICAidHJhamVjdG9yeTpjaGVja3BvaW50LWV2YWx1YXRpb24iCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogImQ2MDU3MmFlYTEyZjkxOTYwZjNmMDAzMGJkZmRjYTU1ZmRhZmUwNTkxNDZjNzIzMGFmOTA5NDkyMzgxMWQzMTIiLAogICAgICAgICAgImxhYmVsIjogIkZpeGVkIGV2YWx1YXRpb24gYWZ0ZXIgcmVzdG9yZSBtYXRjaGVzIiwKICAgICAgICAgICJzdGF0dXMiOiAicGFzcyIKICAgICAgICB9LAogICAgICAgIHsKICAgICAgICAgICJhY3R1YWwiOiAiMWZjNzJmZGYyMTQ4N2FmZTdiMzJkYTgzM2QyMzAwY2Q5YTY4ZjBjMGM2ZjNjZTE0NTY5MTBhNTEwMmE5Mjk5NyIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiVHJhamVjdG9yeSBjb3JyZWN0bmVzcyIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAidHJhamVjdG9yeS5maW5hbF90cmFpbmFibGUiLAogICAgICAgICAgImRldGFpbHMiOiAiRXhhY3QgU0hBLTI1NiBjb21wYXJpc29uOyBubyBudW1lcmljYWwgdG9sZXJhbmNlIGlzIGFwcGxpZWQuIiwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJ0cmFqZWN0b3J5OmZpbmFsLXRyYWluYWJsZSIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiMWZjNzJmZGYyMTQ4N2FmZTdiMzJkYTgzM2QyMzAwY2Q5YTY4ZjBjMGM2ZjNjZTE0NTY5MTBhNTEwMmE5Mjk5NyIsCiAgICAgICAgICAibGFiZWwiOiAiRmluYWwgdHJhaW5hYmxlIHBhcmFtZXRlcnMgbWF0Y2ggY29udHJvbCIsCiAgICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogImE0MmE2ZDI1YzhhYWY2Njc0MTMwZWY2MzQzOWY2ZmQ0MTU4MjRiZDIzZmY5Y2Q2YTdjMGNhMDMwNWJlM2VmOWEiLAogICAgICAgICAgImNhdGVnb3J5IjogIlRyYWplY3RvcnkgY29ycmVjdG5lc3MiLAogICAgICAgICAgImNoZWNrX2lkIjogInRyYWplY3RvcnkuZmluYWxfZXZhbHVhdGlvbiIsCiAgICAgICAgICAiZGV0YWlscyI6ICJFeGFjdCBTSEEtMjU2IGNvbXBhcmlzb247IG5vIG51bWVyaWNhbCB0b2xlcmFuY2UgaXMgYXBwbGllZC4iLAogICAgICAgICAgImV2aWRlbmNlX2lkcyI6IFsKICAgICAgICAgICAgInRyYWplY3Rvcnk6ZmluYWwtZXZhbHVhdGlvbiIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiYTQyYTZkMjVjOGFhZjY2NzQxMzBlZjYzNDM5ZjZmZDQxNTgyNGJkMjNmZjljZDZhN2MwY2EwMzA1YmUzZWY5YSIsCiAgICAgICAgICAibGFiZWwiOiAiRmluYWwgZXZhbHVhdGlvbiBsb2dpdHMgbWF0Y2ggY29udHJvbCIsCiAgICAgICAgICAic3RhdHVzIjogInBhc3MiCiAgICAgICAgfSwKICAgICAgICB7CiAgICAgICAgICAiYWN0dWFsIjogImV4YWN0IG1hdGNoIiwKICAgICAgICAgICJjYXRlZ29yeSI6ICJUcmFqZWN0b3J5IGNvcnJlY3RuZXNzIiwKICAgICAgICAgICJjaGVja19pZCI6ICJ0cmFqZWN0b3J5Lmxvc3NfaGlzdG9yeSIsCiAgICAgICAgICAiZGV0YWlscyI6ICJFeGFjdCBmbG9hdCBzZXF1ZW5jZSBjb21wYXJpc29uOyBubyBudW1lcmljYWwgdG9sZXJhbmNlIGlzIGFwcGxpZWQuIiwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJ0cmFqZWN0b3J5Omxvc3MtaGlzdG9yeSIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiZXhhY3QgbG9zcyBzZXF1ZW5jZSBlcXVhbGl0eSIsCiAgICAgICAgICAibGFiZWwiOiAiQ29udGludWVkIGxvc3MgdHJhamVjdG9yeSBtYXRjaGVzIGNvbnRyb2wiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJjb250YWluZWQiLAogICAgICAgICAgImNhdGVnb3J5IjogIlNhZmV0eSBhbmQgcm9sbGJhY2siLAogICAgICAgICAgImNoZWNrX2lkIjogInNhZmV0eS5wYXRoX2NvbnRhaW5tZW50IiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJzYWZldHk6cGF0aC1jb250YWlubWVudCIKICAgICAgICAgIF0sCiAgICAgICAgICAiZXhwZWN0ZWQiOiAiYWxsIHBhdGhzIGNvbnRhaW5lZDsgc3ltbGluayBlc2NhcGVzIHJlamVjdGVkIiwKICAgICAgICAgICJsYWJlbCI6ICJBbGwgbWFuYWdlZCB3cml0ZSBwYXRocyBwYXNzZWQgY29udGFpbm1lbnQiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgImFjdHVhbCI6ICJjb21wbGV0ZSIsCiAgICAgICAgICAiY2F0ZWdvcnkiOiAiU2FmZXR5IGFuZCByb2xsYmFjayIsCiAgICAgICAgICAiY2hlY2tfaWQiOiAiY29udHJhY3Qubm9fbWFuZGF0b3J5X29taXNzaW9uIiwKICAgICAgICAgICJkZXRhaWxzIjogbnVsbCwKICAgICAgICAgICJldmlkZW5jZV9pZHMiOiBbCiAgICAgICAgICAgICJjb250cmFjdDptYW5kYXRvcnktc3RhdGUiCiAgICAgICAgICBdLAogICAgICAgICAgImV4cGVjdGVkIjogImFsbCBtYW5kYXRvcnkgY29udGludWF0aW9uIHN0YXRlIGRlY2xhcmVkIiwKICAgICAgICAgICJsYWJlbCI6ICJObyBtYW5kYXRvcnkgY29udHJhY3QgcmVxdWlyZW1lbnQgd2FzIHNpbGVudGx5IG9taXR0ZWQiLAogICAgICAgICAgInN0YXR1cyI6ICJwYXNzIgogICAgICAgIH0KICAgICAgXSwKICAgICAgImNvbXBhcmlzb25fcG9saWN5IjogewogICAgICAgICJhdG9sIjogMC4wLAogICAgICAgICJldmFsdWF0aW9uX2xvZ2l0cyI6ICJzaGEyNTZfZXhhY3QiLAogICAgICAgICJldmlkZW5jZSI6ICJUaGUgY29udHJvbGxlZCBDUFUgd29ya2xvYWQgdXNlcyBkZXRlcm1pbmlzdGljIGFsZ29yaXRobXMsIG9uZSBUb3JjaCB0aHJlYWQsIGZpeGVkIHNlZWRzLCBhbmQgc3RlcC1kZXJpdmVkIGJhdGNoZXMuIENyb3NzLXByb2Nlc3MgY29tcGFyaXNvbnMgZmFpbCBvbiBhbnkgZGlnZXN0IG9yIGxvc3Mtc2VxdWVuY2UgZGlmZmVyZW5jZS4iLAogICAgICAgICJsb3NzX2hpc3RvcnkiOiAic2VxdWVuY2VfZXhhY3QiLAogICAgICAgICJtb2RlIjogImV4YWN0IiwKICAgICAgICAib3B0aW1pemVyX3N0YXRlIjogInNoYTI1Nl9leGFjdCIsCiAgICAgICAgInJuZ19zdGF0ZSI6ICJzaGEyNTZfZXhhY3QiLAogICAgICAgICJydG9sIjogMC4wLAogICAgICAgICJzY2hlZHVsZXJfc3RhdGUiOiAic2hhMjU2X2V4YWN0IiwKICAgICAgICAidHJhaW5hYmxlX3BhcmFtZXRlcnMiOiAic2hhMjU2X2V4YWN0IgogICAgICB9LAogICAgICAiZmFpbGVkX2NoZWNrX2lkcyI6IFtdLAogICAgICAiaGFyZF9yb2xsYmFja19saW1pdF9zdGVwcyI6IDAsCiAgICAgICJwYXNzZWQiOiB0cnVlLAogICAgICAic2NoZW1hX3ZlcnNpb24iOiAicmVjb3ZlcnktZ2F0ZS12MSIKICAgIH0sCiAgICAibGltaXRhdGlvbnMiOiBbCiAgICAgICJQaHlzaWNhbCBOQU5EIHdyaXRlcywgd3JpdGUgYW1wbGlmaWNhdGlvbiwgYW5kIFNTRCBsaWZldGltZSB3ZXJlIG5vdCBtZWFzdXJlZC4iLAogICAgICAiTm8gR1BUIHByb3ZpZGVyLCBkaWFnbm9zaXMsIHJlcGFpciBleGVjdXRpb24sIEhUTUwsIG9yIHBhY2thZ2luZyBpcyBwYXJ0IG9mIFByb21wdCAzLiIKICAgIF0sCiAgICAicGxhdGZvcm1fc3VwcG9ydF9ub3RlIjogIldpbmRvd3M6IHBheWxvYWQgYW5kIG1ldGFkYXRhIGZpbGVzIGFyZSBmc3luY2VkIGFuZCBkaXJlY3RvcnkgcmVuYW1lIGlzIGF0b21pYzsgZGlyZWN0b3J5IGZzeW5jIGlzIHVuYXZhaWxhYmxlIHRocm91Z2ggUHl0aG9uIGFuZCByZW1haW5zIGJlc3QtZWZmb3J0LiIsCiAgICAicHJvZmlsZSI6ICJjaSIsCiAgICAicmVjb3ZlcnkiOiB7CiAgICAgICJhZnRlcl9yZXN0b3JlIjogewogICAgICAgICJldmFsdWF0aW9uX3NoYTI1NiI6ICJkNjA1NzJhZWExMmY5MTk2MGYzZjAwMzBiZGZkY2E1NWZkYWZlMDU5MTQ2YzcyMzBhZjkwOTQ5MjM4MTFkMzEyIiwKICAgICAgICAiZ2xvYmFsX3N0ZXAiOiA0LAogICAgICAgICJsb3NzX2hpc3RvcnkiOiBbCiAgICAgICAgICAzLjUzNzE5NzU4OTg3NDI2NzYsCiAgICAgICAgICAzLjQzNDQ1NzU0MDUxMjA4NSwKICAgICAgICAgIDMuNTk3NzA2NTU2MzIwMTkwNCwKICAgICAgICAgIDMuNTYwNzQ2NjY5NzY5Mjg3CiAgICAgICAgXSwKICAgICAgICAib3B0aW1pemVyX3NoYTI1NiI6ICI5ZDc0YzJhYjFkMDA2NWI5YTI3MDA4MGNiYWNkM2NjZGYyOTM3ZThjMmFlZTExMmQ1MDE3MWRlYzQyM2EwYTNhIiwKICAgICAgICAic2NoZWR1bGVyX3NoYTI1NiI6ICJjYWE4MTdmYjMxOTFhYjE0NTZhZGUwMDMyMDU2NWZiM2RmYjdlN2U2NDhhMTIwN2YzZjIyZjA0ODkzZGVjNzcwIiwKICAgICAgICAidHJhaW5hYmxlX3N0YXRlX3NoYTI1NiI6ICI0M2JhNzU4MDg5MDY5MzJhMDA1YjBkM2UxODZiNTc4NmFiNjRhMjVmZGNlNTU0MjY1NWQyZDA5NTFmYzZlZWI1IgogICAgICB9LAogICAgICAiYWZ0ZXJfcmVzdG9yZV9ybmciOiB7CiAgICAgICAgIm51bXB5X3NoYTI1NiI6ICJhZGM3ZTU0NWVjMDUzMGVhZTlmMWRhNzI1ZTgzZjQ4YjE0NmJkNGVjNzlmOTg0NTEzNjdjYTNkMThlOTk0ZGI1IiwKICAgICAgICAicHl0aG9uX3NoYTI1NiI6ICJkZDhhZWMxY2NmMzA1M2RlNjFlZDZhNDU5ZTI2NjhjMzg1Yjc5OTZlYWVkZDk0NzQ0NDAwNjIwOTk5NWE3MDYzIiwKICAgICAgICAidG9yY2hfc2hhMjU2IjogImZhMTYzYzY3YmRjNmJkMzA4ZTczNzk5NzAxZWZmNjAzYjA3ZTYxOTZiMDk3NDhhZjNhMDUxYTE2ZDI1N2NhNjIiCiAgICAgIH0sCiAgICAgICJjaGVja3BvaW50X3BhdGgiOiAiY2hlY2twb2ludHMvcmVwYWlyZWQvbmF0aXZlLXJlcGFpcmVkLWNvbXBsZXRlLXYxL2NoZWNrcG9pbnQtc3RlcC0wMDAwMDQiLAogICAgICAiY29tcGxldGVkX2F0IjogIjIwMjYtMDctMjBUMDE6Mjk6MTIuNDE4MTA1WiIsCiAgICAgICJmaW5hbCI6IHsKICAgICAgICAiZXZhbHVhdGlvbl9zaGEyNTYiOiAiYTQyYTZkMjVjOGFhZjY2NzQxMzBlZjYzNDM5ZjZmZDQxNTgyNGJkMjNmZjljZDZhN2MwY2EwMzA1YmUzZWY5YSIsCiAgICAgICAgImdsb2JhbF9zdGVwIjogOCwKICAgICAgICAibG9zc19oaXN0b3J5IjogWwogICAgICAgICAgMy41MzcxOTc1ODk4NzQyNjc2LAogICAgICAgICAgMy40MzQ0NTc1NDA1MTIwODUsCiAgICAgICAgICAzLjU5NzcwNjU1NjMyMDE5MDQsCiAgICAgICAgICAzLjU2MDc0NjY2OTc2OTI4NywKICAgICAgICAgIDMuNjcwODIzNTc0MDY2MTYyLAogICAgICAgICAgMy42MjcyNTMyOTM5OTEwODksCiAgICAgICAgICAzLjUwODYzOTMzNTYzMjMyNCwKICAgICAgICAgIDMuODI0ODE0MzE5NjEwNTk1NwogICAgICAgIF0sCiAgICAgICAgIm9wdGltaXplcl9zaGEyNTYiOiAiYzAzZGZjOGI2NmU2NjQ1ZmI1NTIyMjM0MjhhZDg2YTg1NWM5NzA0OWQxMzNiMDg5ODQ2MDRmNmU3ZDU1YTA1MCIsCiAgICAgICAgInNjaGVkdWxlcl9zaGEyNTYiOiAiZTA3ZmZkNmE4OWZlZmI2MWU4MGQxY2E1NjAyNWE5MjcyMjJhODMxODBmZmNlZDc3ODc4OTYwNmQzYTdiZWM4MSIsCiAgICAgICAgInRyYWluYWJsZV9zdGF0ZV9zaGEyNTYiOiAiMWZjNzJmZGYyMTQ4N2FmZTdiMzJkYTgzM2QyMzAwY2Q5YTY4ZjBjMGM2ZjNjZTE0NTY5MTBhNTEwMmE5Mjk5NyIKICAgICAgfSwKICAgICAgImZpcnN0X2NvbXBsZXRlZF9zdGVwIjogNSwKICAgICAgImZpcnN0X3Jlc3VtZWRfYmF0Y2hfc3RlcCI6IDQsCiAgICAgICJyZXN0b3JlZF9nbG9iYWxfc3RlcCI6IDQsCiAgICAgICJzY2hlbWFfdmVyc2lvbiI6ICJyZWNvdmVyeS13b3JrZXItcmVzdWx0LXYxIiwKICAgICAgInN0YXJ0ZWRfYXQiOiAiMjAyNi0wNy0yMFQwMToyOToxMC45OTgyMTZaIiwKICAgICAgInN0cmF0ZWd5IjogInNhZmVfYWRhcHRlcl9hd2FyZSIsCiAgICAgICJ3b3JrZXJfcGlkIjogMzEzOTYKICAgIH0sCiAgICAicmVjb3ZlcnlfcHJvY2VzcyI6IHsKICAgICAgImNvbXBsZXRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjEyLjkwOTY5NFoiLAogICAgICAiZXhpdF9jb2RlIjogMCwKICAgICAgImV4aXRfdmVyaWZpZWQiOiB0cnVlLAogICAgICAic3RhcnRlZF9hdCI6ICIyMDI2LTA3LTIwVDAxOjI5OjA4Ljk0NDIzOVoiLAogICAgICAid29ya2VyX3BpZCI6IDMxMzk2CiAgICB9LAogICAgInJlc3VsdF9wYXRoIjogInJlc3VsdC5qc29uIiwKICAgICJydW5faWQiOiAicmVwYWlyZWQiLAogICAgInNjaGVtYV92ZXJzaW9uIjogImNyYXNoLWV4cGVyaW1lbnQtdjEiLAogICAgInN0cmF0ZWd5IjogInNhZmVfYWRhcHRlcl9hd2FyZSIKICB9LAogICJyZXBsYXlfY2FsbF9tZXRhZGF0YSI6IHsKICAgICJmaXh0dXJlX3Byb3ZlbmFuY2UiOiAibGl2ZV9ncHRfNV82X2NhcHR1cmUiLAogICAgImxpdmVfb3JfZml4dHVyZSI6ICJmaXh0dXJlIiwKICAgICJtb2RlbCI6ICJncHQtNS42IiwKICAgICJvdXRwdXRfc2NoZW1hX3ZlcnNpb24iOiAiZmFpbHVyZS1hbmFseXNpcy12MiIsCiAgICAicHJvbXB0X3ZlcnNpb24iOiAidjIiLAogICAgInByb3ZpZGVyIjogImZpeHR1cmUiLAogICAgInJlcXVlc3Rfc2hhMjU2IjogImFlMGFiOWVhNjRkYWQ1ZGQ2OGQzNDM3ZDI3NjQ5OTg3Mjk1NjM3NjMwZDQ3NjQ3ZDliMmYyN2Y5ZGIwNmIxNzgiLAogICAgInJlc3BvbnNlX2lkIjogbnVsbCwKICAgICJyb2xlIjogImZhaWx1cmUtYW5hbHlzaXMiLAogICAgInNjaGVtYV92ZXJzaW9uIjogImFnZW50LWNhbGwtbWV0YWRhdGEtdjEiLAogICAgInNvdXJjZSI6ICJjYXB0dXJlZF9saXZlX3Jlc3BvbnNlX3JlcGxheSIsCiAgICAic3RvcmUiOiBmYWxzZSwKICAgICJ0aW1lc3RhbXAiOiAiMjAyNi0wNy0yMFQwMToyOTowNS4xNjAzOTZaIiwKICAgICJ2YWxpZGF0aW9uX3N0YXR1cyI6ICJhY2NlcHRlZCIKICB9LAogICJyZXBvcnRfcGF0aCI6ICJyZXBvcnQubWQiLAogICJyZXN1bHRfcGF0aCI6ICJyZXN1bHQuanNvbiIsCiAgInJ1bl9pZCI6ICJtaWxlc3RvbmUxMy1uYXRpdmUiLAogICJzY2hlbWFfdmVyc2lvbiI6ICJyZXBhaXItbG9vcC1yZXN1bHQtdjEiLAogICJzdG9yYWdlX2NvbXBhcmlzb24iOiB7CiAgICAiY2hlY2twb2ludF9zdGVwIjogNCwKICAgICJsaW1pdGF0aW9ucyI6IFsKICAgICAgIlRoZSByZXBhaXJlZCByZWN1cnJpbmcgdG90YWwgZXhjbHVkZXMgdGhlIGltbXV0YWJsZSBiYXNlIGFydGlmYWN0IHN0b3JlZCBvbmNlIHBlciBydW4uIiwKICAgICAgIkxvZ2ljYWwgZmlsZSBieXRlcyBhcmUgbWVhc3VyZWQ7IHBoeXNpY2FsIE5BTkQgd3JpdGVzIGFuZCB3cml0ZSBhbXBsaWZpY2F0aW9uIGFyZSBub3QuIiwKICAgICAgIlRoZSBzYWZlX2Z1bGwgc291cmNlIGlzIHRoZSB1bmNoYW5nZWQgZGlyZWN0LXJlc3RvcmUgbWVhc3VyZW1lbnQgaW1wbGVtZW50YXRpb24uIgogICAgXSwKICAgICJtZWFzdXJlbWVudF9zY29wZSI6ICJsb2dpY2FsX2NoZWNrcG9pbnRfZGlyZWN0b3J5X2J5dGVzIiwKICAgICJwcm9maWxlIjogImNpIiwKICAgICJyZXBhaXJlZF9vbmVfdGltZV9iYXNlX2J5dGVzIjogMTg0NzUsCiAgICAicmVwYWlyZWRfcmVjdXJyaW5nX2J5dGVzIjogMjc2ODEsCiAgICAicmVwb3J0ZWRfYWZ0ZXJfcmVjb3ZlcnlfcGFzc2VkIjogdHJ1ZSwKICAgICJzYWZlX2Z1bGxfYnl0ZXMiOiA0NDk5OCwKICAgICJzYWZlX2Z1bGxfbWVhc3VyZW1lbnRfc291cmNlIjogInVuY2hhbmdlZF9zYWZlX2Z1bGxfZGlyZWN0X3Jlc3RvcmVfYmFzZWxpbmUiLAogICAgInNjaGVtYV92ZXJzaW9uIjogInN0b3JhZ2UtY29tcGFyaXNvbi12MSIsCiAgICAic3RydWN0dXJhbF9yZWR1Y3Rpb25fYnl0ZXMiOiAxNzMxNywKICAgICJzdHJ1Y3R1cmFsX3JlZHVjdGlvbl9wZXJjZW50IjogMzguNDgzOTMyNjE5MjI3NTI0CiAgfQp9Cg=="
  },
  "evidence_missing": [],
  "id": "native-repair",
  "job_summary": "# FlashPilot CI summary\n\n- Outcome: **VERIFIED**\n- Evidence kind: `native-qualification`\n- Framework: `native-pytorch`\n- Qualification profile: `exact-training-resume`\n- Checks: `24/24` non-failing\n- RPO: `0` steps\n- RTO: `3.965455` seconds\n\n## Exact failed requirements\n\n- None\n\nThis summary is derived from the same typed evidence used by the local CLI.\n",
  "junit": "<?xml version='1.0' encoding='utf-8'?>\n<testsuite name=\"flashpilot.native-qualification\" tests=\"24\" failures=\"0\" errors=\"0\" skipped=\"0\">\n  <properties>\n    <property name=\"status\" value=\"VERIFIED\" />\n    <property name=\"framework\" value=\"native-pytorch\" />\n    <property name=\"qualification_profile\" value=\"exact-training-resume\" />\n    <property name=\"rpo_steps\" value=\"0\" />\n    <property name=\"rto_seconds\" value=\"3.965455\" />\n  </properties>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"integrity.manifest_schema\">\n    <system-out>Manifest schema valid Expected=checkpoint-manifest-v1; actual=checkpoint-manifest-v1.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"integrity.completion_marker\">\n    <system-out>Completion marker present Expected=COMPLETE present in final checkpoint; actual=present.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"integrity.checksums\">\n    <system-out>All payload checksums valid Expected=every manifest payload matches SHA-256 and size; actual=5 payloads validated.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"integrity.base_present\">\n    <system-out>Base artifact present when required Expected=contained immutable base artifact; actual=present.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"integrity.base_hash\">\n    <system-out>Base artifact hash matches Expected=c17cc8994c8f0fe6def32423b0e5d9efedffb3cd71c7de9631f26cf505925d86; actual=c17cc8994c8f0fe6def32423b0e5d9efedffb3cd71c7de9631f26cf505925d86.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"state.global_step\">\n    <system-out>Checkpoint global step is valid Expected=0 &lt; step &lt; 8, consistent across restore; actual=manifest=4, event=4, restored=4.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"state.model_or_adapter\">\n    <system-out>Model or adapter state restores Expected=serialized adapter and exact trainable-state digest; actual=serialized=True, digest_match=True.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"state.optimizer\">\n    <system-out>Optimizer state restores when required Expected=serialized optimizer with exact digest; actual=serialized=True, digest_match=True.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"state.scheduler\">\n    <system-out>Scheduler state restores when required Expected=serialized scheduler with exact digest; actual=serialized=True, digest_match=True.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"state.python_rng\">\n    <system-out>Python RNG state restores when required Expected=serialized state with exact digest; actual=serialized=True, digest_match=True.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"state.numpy_rng\">\n    <system-out>NumPy RNG state restores when required Expected=serialized state with exact digest; actual=serialized=True, digest_match=True.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"state.torch_rng\">\n    <system-out>Torch RNG state restores when required Expected=serialized state with exact digest; actual=serialized=True, digest_match=True.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"process.next_step\">\n    <system-out>Resumed run continues from the expected next step Expected=first batch at 4, first completion at 5; actual=first batch at 4, first completion at 5.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"process.original_pid\">\n    <system-out>Original worker PID is recorded Expected=27632; actual=27632.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"process.expected_termination\">\n    <system-out>Original worker termination is verified Expected=parent termination with nonzero exit code; actual=method=TerminateProcess via subprocess.Popen.kill, exit=1, verified=True.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"process.new_recovery_pid\">\n    <system-out>Recovery uses a different PID Expected=PID different from 27632; actual=31396.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"process.recovery_exit\">\n    <system-out>Recovery worker exits successfully Expected=exit code 0; actual=exit=0, verified=True.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"rollback.hard_limit\">\n    <system-out>Achieved rollback is within the hard limit Expected=&lt;= 0 steps; actual=0 steps.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"trajectory.checkpoint_evaluation\">\n    <system-out>Fixed evaluation after restore matches Expected=d60572aea12f91960f3f0030bdfdca55fdafe059146c7230af9094923811d312; actual=d60572aea12f91960f3f0030bdfdca55fdafe059146c7230af9094923811d312.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"trajectory.final_trainable\">\n    <system-out>Final trainable parameters match control Expected=1fc72fdf21487afe7b32da833d2300cd9a68f0c0c6f3ce1456910a5102a92997; actual=1fc72fdf21487afe7b32da833d2300cd9a68f0c0c6f3ce1456910a5102a92997.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"trajectory.final_evaluation\">\n    <system-out>Final evaluation logits match control Expected=a42a6d25c8aaf6674130ef63439f6fd415824bd23ff9cd6a7c0ca0305be3ef9a; actual=a42a6d25c8aaf6674130ef63439f6fd415824bd23ff9cd6a7c0ca0305be3ef9a.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"trajectory.loss_history\">\n    <system-out>Continued loss trajectory matches control Expected=exact loss sequence equality; actual=exact match.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"safety.path_containment\">\n    <system-out>All managed write paths passed containment Expected=all paths contained; symlink escapes rejected; actual=contained.</system-out>\n  </testcase>\n  <testcase classname=\"flashpilot.native-pytorch\" name=\"contract.no_mandatory_omission\">\n    <system-out>No mandatory contract requirement was silently omitted Expected=all mandatory continuation state declared; actual=complete.</system-out>\n  </testcase>\n</testsuite>\n",
  "kind": "repair",
  "manifest": {
   "entries": [
    {
     "path": "agent/failure/captured-live-metadata.json",
     "sha256": "adb92f36e454c33be35b9ba7793cc0e6201e3375889918332da07f34a95a2987",
     "size_bytes": 573
    },
    {
     "path": "agent/failure/metadata.json",
     "sha256": "ae7a1f6cbf8ce8c7e4489425499f9b8bf1cd80bc04daa4e8c4e6ba1665145d99",
     "size_bytes": 537
    },
    {
     "path": "agent/failure/request.redacted.json",
     "sha256": "da5d268138d74b6a178f78318e10ecdd584393bcf6fa7372b1076803868f7fd2",
     "size_bytes": 14235
    },
    {
     "path": "agent/failure/response.parsed.json",
     "sha256": "7733b94365c27f791a602bebf9d71a33ce0350313591b7941510770c5f795e27",
     "size_bytes": 4831
    },
    {
     "path": "agent/failure/validation.json",
     "sha256": "1989796c0cad0dacb76de5a326c0dcbc9490bb44e7c03ba8ef67c8b972269f31",
     "size_bytes": 2676
    },
    {
     "path": "agent/repair-attempt-admission.json",
     "sha256": "02f9f15c1733553581fabdebaafc6d90ff4e91843d5685b84e929c7c340ba2c7",
     "size_bytes": 157
    },
    {
     "path": "agent/repair/execution.json",
     "sha256": "8b0b79a65972ab189b6f68797836b7c7fc1d41a1102369ab3e21208a9c6f5095",
     "size_bytes": 1124
    },
    {
     "path": "agent/repair/repaired-strategy.json",
     "sha256": "f631fb57e4bedc70d8feeadb81cd0f43a805a1a23bd371a9c4df4b2956b0cc5a",
     "size_bytes": 287
    },
    {
     "path": "agent/request.redacted.json",
     "sha256": "da5d268138d74b6a178f78318e10ecdd584393bcf6fa7372b1076803868f7fd2",
     "size_bytes": 14235
    },
    {
     "path": "environment.json",
     "sha256": "4c7fbf342a03801607f693b045f2ed7be58048a67347d8c8595732a0b30075ae",
     "size_bytes": 776
    },
    {
     "path": "initial/agent/request.redacted.json",
     "sha256": "da5d268138d74b6a178f78318e10ecdd584393bcf6fa7372b1076803868f7fd2",
     "size_bytes": 14235
    },
    {
     "path": "initial/artifacts/frozen-base/COMPLETE",
     "sha256": "ce65117826b8b76a7480b8789b41c698c0865b64c6b51f93be8bdc28719d3a46",
     "size_bytes": 83
    },
    {
     "path": "initial/artifacts/frozen-base/base.json",
     "sha256": "81dcc20c7c340e2fd8c33e388a1774dbd268446fa9e3286785cc6a60bcd9d3e4",
     "size_bytes": 372
    },
    {
     "path": "initial/artifacts/frozen-base/base.pt",
     "sha256": "c17cc8994c8f0fe6def32423b0e5d9efedffb3cd71c7de9631f26cf505925d86",
     "size_bytes": 18475
    },
    {
     "path": "initial/checkpoints/missing-training-state/checkpoint-step-000004/COMPLETE",
     "sha256": "b4babcb4704ae078c54e0adec79602bbcf0927dacd2149cd4f8207ef70f13009",
     "size_bytes": 92
    },
    {
     "path": "initial/checkpoints/missing-training-state/checkpoint-step-000004/adapter.pt",
     "sha256": "cc6681b215e8106c3801b59582e57e2a6c73d96a54b97e398ece8aa186859bf1",
     "size_bytes": 2781
    },
    {
     "path": "initial/checkpoints/missing-training-state/checkpoint-step-000004/checksums.json",
     "sha256": "9373ddd51d88d63d3e4ea283e696eba6e1ba2ad21b0bb553ff943077bbed3bd0",
     "size_bytes": 355
    },
    {
     "path": "initial/checkpoints/missing-training-state/checkpoint-step-000004/manifest.json",
     "sha256": "56281b789f24d88fa0d3522a3509b09f15c8c3980f72587c08e48723123d498f",
     "size_bytes": 1080
    },
    {
     "path": "initial/checkpoints/missing-training-state/checkpoint-step-000004/state.json",
     "sha256": "76e527e70d42be77d0759b1c6229c56baab37b757a3fd0954025bb717927c0f3",
     "size_bytes": 861
    },
    {
     "path": "initial/logs/checkpoint-worker.stderr.log",
     "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
     "size_bytes": 0
    },
    {
     "path": "initial/logs/recovery-worker.stderr.log",
     "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
     "size_bytes": 0
    },
    {
     "path": "initial/result.json",
     "sha256": "6447dfffa7e0f2d948efacf27d0ba005a4d5f768bdaeb4b6119637b88b2d6e2b",
     "size_bytes": 14743
    },
    {
     "path": "initial/workers/recovery-result.json",
     "sha256": "4198109bae15976c7980558262074987fa504a3ba98935f2291207366b07cf3f",
     "size_bytes": 1878
    },
    {
     "path": "job-summary.md",
     "sha256": "38de9a45234fabaa2a39f07e15f20862f8dca39d998f8cf38e0ccb6fde3bf75a",
     "size_bytes": 356
    },
    {
     "path": "junit.xml",
     "sha256": "5523648af42dbf09cb5b51d58e8e9da9e294560b05b70b83ca987f1576b90ad1",
     "size_bytes": 6430
    },
    {
     "path": "measurements/safe-full/checkpoints/checkpoint-step-000004/COMPLETE",
     "sha256": "b4babcb4704ae078c54e0adec79602bbcf0927dacd2149cd4f8207ef70f13009",
     "size_bytes": 92
    },
    {
     "path": "measurements/safe-full/checkpoints/checkpoint-step-000004/checksums.json",
     "sha256": "627bdfb1699094e8993e2f809600d59c3110b9aaedbea21f50fbdb75d2f89786",
     "size_bytes": 805
    },
    {
     "path": "measurements/safe-full/checkpoints/checkpoint-step-000004/manifest.json",
     "sha256": "3e7e95f43bef2c8e5ccde9838c7d8a169adee016187070d63f1bb5a438a6afa6",
     "size_bytes": 1305
    },
    {
     "path": "measurements/safe-full/checkpoints/checkpoint-step-000004/model.pt",
     "sha256": "2bbdd47b7e346ed7d8f3ee443897ce9884dbe4517d06da2bbd371f02f43f3d1b",
     "size_bytes": 20718
    },
    {
     "path": "measurements/safe-full/checkpoints/checkpoint-step-000004/optimizer.pt",
     "sha256": "ce1a57f6b5ed144f5ffed0a73b27cda66f49caa19f06124984dbb9eedabf4baf",
     "size_bytes": 5795
    },
    {
     "path": "measurements/safe-full/checkpoints/checkpoint-step-000004/rng.pt",
     "sha256": "71ed181a88f9f4250fa37088ace6e502308b66f72dae3e4c085514511630f97e",
     "size_bytes": 14285
    },
    {
     "path": "measurements/safe-full/checkpoints/checkpoint-step-000004/scheduler.pt",
     "sha256": "4b06758dd8c53f4479c37b7e5b5ff7a5850408ec7e9a519d30c58cb8b61a6759",
     "size_bytes": 1465
    },
    {
     "path": "measurements/safe-full/checkpoints/checkpoint-step-000004/state.json",
     "sha256": "6dffd484aceb5285169fc1726547b1f3cd1215b412e6252c8cfb0643f0df5d9f",
     "size_bytes": 533
    },
    {
     "path": "measurements/storage-comparison.json",
     "sha256": "791cf1bfd1fb9d81868c0fc6b2d8bd0d1927a462a65eb763843b42ee86aeebf3",
     "size_bytes": 773
    },
    {
     "path": "persistence-contract.json",
     "sha256": "a6d17a5cccbe0f7f709f2c36cb87332b819ffe12938b74cced568f01acdf86a1",
     "size_bytes": 2766
    },
    {
     "path": "repaired/artifacts/frozen-base/COMPLETE",
     "sha256": "ce65117826b8b76a7480b8789b41c698c0865b64c6b51f93be8bdc28719d3a46",
     "size_bytes": 83
    },
    {
     "path": "repaired/artifacts/frozen-base/base.json",
     "sha256": "81dcc20c7c340e2fd8c33e388a1774dbd268446fa9e3286785cc6a60bcd9d3e4",
     "size_bytes": 372
    },
    {
     "path": "repaired/artifacts/frozen-base/base.pt",
     "sha256": "c17cc8994c8f0fe6def32423b0e5d9efedffb3cd71c7de9631f26cf505925d86",
     "size_bytes": 18475
    },
    {
     "path": "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/COMPLETE",
     "sha256": "b4babcb4704ae078c54e0adec79602bbcf0927dacd2149cd4f8207ef70f13009",
     "size_bytes": 92
    },
    {
     "path": "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/adapter.pt",
     "sha256": "cc6681b215e8106c3801b59582e57e2a6c73d96a54b97e398ece8aa186859bf1",
     "size_bytes": 2781
    },
    {
     "path": "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/checksums.json",
     "sha256": "61dd3d31d8b901309f7eec3f81fa33e9b0e78a7152ce3f1ee2ae3d1d2cd48c09",
     "size_bytes": 806
    },
    {
     "path": "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/manifest.json",
     "sha256": "f2b5a02749131bb4076695da7b05cfc27cb716cb777709ecdbc0e447ac4f83e2",
     "size_bytes": 1600
    },
    {
     "path": "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/optimizer.pt",
     "sha256": "ce1a57f6b5ed144f5ffed0a73b27cda66f49caa19f06124984dbb9eedabf4baf",
     "size_bytes": 5795
    },
    {
     "path": "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/rng.pt",
     "sha256": "71ed181a88f9f4250fa37088ace6e502308b66f72dae3e4c085514511630f97e",
     "size_bytes": 14285
    },
    {
     "path": "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/scheduler.pt",
     "sha256": "4b06758dd8c53f4479c37b7e5b5ff7a5850408ec7e9a519d30c58cb8b61a6759",
     "size_bytes": 1465
    },
    {
     "path": "repaired/checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004/state.json",
     "sha256": "42f0ffd09aff687c6d363e67efdb6b4093bc30b5feb1955ac94ad455352b19a1",
     "size_bytes": 857
    },
    {
     "path": "repaired/logs/checkpoint-worker.stderr.log",
     "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
     "size_bytes": 0
    },
    {
     "path": "repaired/logs/recovery-worker.stderr.log",
     "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
     "size_bytes": 0
    },
    {
     "path": "repaired/result.json",
     "sha256": "71b42eed50c722780b4b51ea19b99c275baffaadcedfdc6dbf6bddddbda479b1",
     "size_bytes": 14384
    },
    {
     "path": "repaired/strategy/repaired-strategy.json",
     "sha256": "f631fb57e4bedc70d8feeadb81cd0f43a805a1a23bd371a9c4df4b2956b0cc5a",
     "size_bytes": 287
    },
    {
     "path": "repaired/workers/recovery-result.json",
     "sha256": "1219b5b4bfbf0f864bf2e4076865b7eaffa466564ad6b28f7da420adb0942b9a",
     "size_bytes": 1885
    },
    {
     "path": "report.html",
     "sha256": "43c695256ef0776b346acfb675928672abebb7a042e8ab4de5d651386a762e3c",
     "size_bytes": 8315
    },
    {
     "path": "report.md",
     "sha256": "8305c897f63192e5e2ee4f4f7fac1b0c1db85f681de0d3f4f6326305112913e7",
     "size_bytes": 2138
    },
    {
     "path": "result.json",
     "sha256": "abe4141f060a4fd87e68e5bbc974518908d85c865e314cc336100b151c727d97",
     "size_bytes": 43147
    }
   ],
   "excluded_statement_artifacts": [
    "attestation.junit.xml",
    "evidence-manifest.json",
    "recovery.attestation.json"
   ],
   "root_scope": "attestation-directory",
   "schema_version": "flashpilot-evidence-manifest-v1"
  },
  "result": {
   "captured_live_failure_metadata": {
    "fixture_provenance": "not_applicable",
    "live_or_fixture": "live",
    "model": "gpt-5.6",
    "output_schema_version": "failure-analysis-v2",
    "prompt_version": "v2",
    "provider": "openai",
    "request_sha256": "eaa6f7818ecdaf482525081514dccfbfe748ae79b0d17c1a719a5e60bfc5ba2e",
    "response_id": "resp_0d7e808cd722f97f016a5a90f0300481908d22e7befa15e3fe",
    "role": "failure-analysis",
    "schema_version": "agent-call-metadata-v1",
    "source": "captured_live_response",
    "store": false,
    "timestamp": "2026-07-17T20:31:09.771820Z",
    "validation_status": "accepted"
   },
   "created_at": "2026-07-20T01:29:13.076645Z",
   "fallback_status": "not_required",
   "final_verdict": "VERIFIED",
   "html_report_path": "report.html",
   "initial_failure": {
    "control": {
     "evaluation_sha256": "a42a6d25c8aaf6674130ef63439f6fd415824bd23ff9cd6a7c0ca0305be3ef9a",
     "global_step": 8,
     "loss_history": [
      3.5371975898742676,
      3.434457540512085,
      3.5977065563201904,
      3.560746669769287,
      3.670823574066162,
      3.627253293991089,
      3.508639335632324,
      3.8248143196105957
     ],
     "optimizer_sha256": "c03dfc8b66e6645fb552223428ad86a855c97049d133b08984604f6e7d55a050",
     "scheduler_sha256": "e07ffd6a89fefb61e80d1ca56025a927222a83180ffced778789606d3a7bec81",
     "trainable_state_sha256": "1fc72fdf21487afe7b32da833d2300cd9a68f0c0c6f3ce1456910a5102a92997"
    },
    "crash": {
     "checkpoint_path": "checkpoints/missing-training-state/checkpoint-step-000004",
     "checkpoint_step": 4,
     "event_received_at": "2026-07-20T01:28:59.132038Z",
     "last_completed_step": 4,
     "terminated_at": "2026-07-20T01:28:59.174202Z",
     "termination_exit_code": 1,
     "termination_method": "TerminateProcess via subprocess.Popen.kill",
     "termination_verified": true,
     "worker_pid": 31412
    },
    "created_at": "2026-07-20T01:29:05.119921Z",
    "failure_artifact_path": "agent/request.redacted.json",
    "gate": {
     "achieved_rollback_steps": 0,
     "checks": [
      {
       "actual": "checkpoint-manifest-v1",
       "category": "Integrity",
       "check_id": "integrity.manifest_schema",
       "details": null,
       "evidence_ids": [
        "manifest:schema"
       ],
       "expected": "checkpoint-manifest-v1",
       "label": "Manifest schema valid",
       "status": "pass"
      },
      {
       "actual": "present",
       "category": "Integrity",
       "check_id": "integrity.completion_marker",
       "details": null,
       "evidence_ids": [
        "integrity:completion-marker"
       ],
       "expected": "COMPLETE present in final checkpoint",
       "label": "Completion marker present",
       "status": "pass"
      },
      {
       "actual": "2 payloads validated",
       "category": "Integrity",
       "check_id": "integrity.checksums",
       "details": null,
       "evidence_ids": [
        "integrity:sha256"
       ],
       "expected": "every manifest payload matches SHA-256 and size",
       "label": "All payload checksums valid",
       "status": "pass"
      },
      {
       "actual": "present",
       "category": "Integrity",
       "check_id": "integrity.base_present",
       "details": null,
       "evidence_ids": [
        "base:presence"
       ],
       "expected": "contained immutable base artifact",
       "label": "Base artifact present when required",
       "status": "pass"
      },
      {
       "actual": "c17cc8994c8f0fe6def32423b0e5d9efedffb3cd71c7de9631f26cf505925d86",
       "category": "Integrity",
       "check_id": "integrity.base_hash",
       "details": null,
       "evidence_ids": [
        "base:sha256"
       ],
       "expected": "c17cc8994c8f0fe6def32423b0e5d9efedffb3cd71c7de9631f26cf505925d86",
       "label": "Base artifact hash matches",
       "status": "pass"
      },
      {
       "actual": "manifest=4, event=4, restored=4",
       "category": "Required training state",
       "check_id": "state.global_step",
       "details": null,
       "evidence_ids": [
        "manifest:global-step"
       ],
       "expected": "0 < step < 8, consistent across restore",
       "label": "Checkpoint global step is valid",
       "status": "pass"
      },
      {
       "actual": "serialized=True, digest_match=True",
       "category": "Required training state",
       "check_id": "state.model_or_adapter",
       "details": null,
       "evidence_ids": [
        "restore:model-state"
       ],
       "expected": "serialized adapter and exact trainable-state digest",
       "label": "Model or adapter state restores",
       "status": "pass"
      },
      {
       "actual": "serialized=False, digest_match=False",
       "category": "Required training state",
       "check_id": "state.optimizer",
       "details": null,
       "evidence_ids": [
        "restore:optimizer-state"
       ],
       "expected": "serialized optimizer with exact digest",
       "label": "Optimizer state restores when required",
       "status": "fail"
      },
      {
       "actual": "serialized=False, digest_match=False",
       "category": "Required training state",
       "check_id": "state.scheduler",
       "details": null,
       "evidence_ids": [
        "restore:scheduler-state"
       ],
       "expected": "serialized scheduler with exact digest",
       "label": "Scheduler state restores when required",
       "status": "fail"
      },
      {
       "actual": "serialized=False, digest_match=True",
       "category": "Required training state",
       "check_id": "state.python_rng",
       "details": null,
       "evidence_ids": [
        "restore:python-rng"
       ],
       "expected": "serialized state with exact digest",
       "label": "Python RNG state restores when required",
       "status": "fail"
      },
      {
       "actual": "serialized=False, digest_match=True",
       "category": "Required training state",
       "check_id": "state.numpy_rng",
       "details": null,
       "evidence_ids": [
        "restore:numpy-rng"
       ],
       "expected": "serialized state with exact digest",
       "label": "NumPy RNG state restores when required",
       "status": "fail"
      },
      {
       "actual": "serialized=False, digest_match=False",
       "category": "Required training state",
       "check_id": "state.torch_rng",
       "details": null,
       "evidence_ids": [
        "restore:torch-rng"
       ],
       "expected": "serialized state with exact digest",
       "label": "Torch RNG state restores when required",
       "status": "fail"
      },
      {
       "actual": "first batch at 4, first completion at 5",
       "category": "Process recovery",
       "check_id": "process.next_step",
       "details": null,
       "evidence_ids": [
        "process:next-step"
       ],
       "expected": "first batch at 4, first completion at 5",
       "label": "Resumed run continues from the expected next step",
       "status": "pass"
      },
      {
       "actual": "31412",
       "category": "Process recovery",
       "check_id": "process.original_pid",
       "details": null,
       "evidence_ids": [
        "process:original-pid"
       ],
       "expected": "31412",
       "label": "Original worker PID is recorded",
       "status": "pass"
      },
      {
       "actual": "method=TerminateProcess via subprocess.Popen.kill, exit=1, verified=True",
       "category": "Process recovery",
       "check_id": "process.expected_termination",
       "details": null,
       "evidence_ids": [
        "process:termination"
       ],
       "expected": "parent termination with nonzero exit code",
       "label": "Original worker termination is verified",
       "status": "pass"
      },
      {
       "actual": "16600",
       "category": "Process recovery",
       "check_id": "process.new_recovery_pid",
       "details": null,
       "evidence_ids": [
        "process:recovery-pid"
       ],
       "expected": "PID different from 31412",
       "label": "Recovery uses a different PID",
       "status": "pass"
      },
      {
       "actual": "exit=0, verified=True",
       "category": "Process recovery",
       "check_id": "process.recovery_exit",
       "details": null,
       "evidence_ids": [
        "process:recovery-exit"
       ],
       "expected": "exit code 0",
       "label": "Recovery worker exits successfully",
       "status": "pass"
      },
      {
       "actual": "0 steps",
       "category": "Safety and rollback",
       "check_id": "rollback.hard_limit",
       "details": null,
       "evidence_ids": [
        "rollback:achieved"
       ],
       "expected": "<= 0 steps",
       "label": "Achieved rollback is within the hard limit",
       "status": "pass"
      },
      {
       "actual": "d60572aea12f91960f3f0030bdfdca55fdafe059146c7230af9094923811d312",
       "category": "Trajectory correctness",
       "check_id": "trajectory.checkpoint_evaluation",
       "details": "Exact SHA-256 comparison; no numerical tolerance is applied.",
       "evidence_ids": [
        "trajectory:checkpoint-evaluation"
       ],
       "expected": "d60572aea12f91960f3f0030bdfdca55fdafe059146c7230af9094923811d312",
       "label": "Fixed evaluation after restore matches",
       "status": "pass"
      },
      {
       "actual": "d28547e82dc412d58060e8be64deb52191b7b258561be47874694b1c546eca66",
       "category": "Trajectory correctness",
       "check_id": "trajectory.final_trainable",
       "details": "Exact SHA-256 comparison; no numerical tolerance is applied.",
       "evidence_ids": [
        "trajectory:final-trainable"
       ],
       "expected": "1fc72fdf21487afe7b32da833d2300cd9a68f0c0c6f3ce1456910a5102a92997",
       "label": "Final trainable parameters match control",
       "status": "fail"
      },
      {
       "actual": "4346a2d77b37076b853d4529981824edd549538f938d4964220899149dd5b4cd",
       "category": "Trajectory correctness",
       "check_id": "trajectory.final_evaluation",
       "details": "Exact SHA-256 comparison; no numerical tolerance is applied.",
       "evidence_ids": [
        "trajectory:final-evaluation"
       ],
       "expected": "a42a6d25c8aaf6674130ef63439f6fd415824bd23ff9cd6a7c0ca0305be3ef9a",
       "label": "Final evaluation logits match control",
       "status": "fail"
      },
      {
       "actual": "sequence differs",
       "category": "Trajectory correctness",
       "check_id": "trajectory.loss_history",
       "details": "Exact float sequence comparison; no numerical tolerance is applied.",
       "evidence_ids": [
        "trajectory:loss-history"
       ],
       "expected": "exact loss sequence equality",
       "label": "Continued loss trajectory matches control",
       "status": "fail"
      },
      {
       "actual": "contained",
       "category": "Safety and rollback",
       "check_id": "safety.path_containment",
       "details": null,
       "evidence_ids": [
        "safety:path-containment"
       ],
       "expected": "all paths contained; symlink escapes rejected",
       "label": "All managed write paths passed containment",
       "status": "pass"
      },
      {
       "actual": "manifest lacks: numpy_rng, optimizer, python_rng, scheduler, torch_rng",
       "category": "Safety and rollback",
       "check_id": "contract.no_mandatory_omission",
       "details": null,
       "evidence_ids": [
        "contract:mandatory-state"
       ],
       "expected": "all mandatory continuation state declared",
       "label": "No mandatory contract requirement was silently omitted",
       "status": "fail"
      }
     ],
     "comparison_policy": {
      "atol": 0.0,
      "evaluation_logits": "sha256_exact",
      "evidence": "The controlled CPU workload uses deterministic algorithms, one Torch thread, fixed seeds, and step-derived batches. Cross-process comparisons fail on any digest or loss-sequence difference.",
      "loss_history": "sequence_exact",
      "mode": "exact",
      "optimizer_state": "sha256_exact",
      "rng_state": "sha256_exact",
      "rtol": 0.0,
      "scheduler_state": "sha256_exact",
      "trainable_parameters": "sha256_exact"
     },
     "failed_check_ids": [
      "state.optimizer",
      "state.scheduler",
      "state.python_rng",
      "state.numpy_rng",
      "state.torch_rng",
      "trajectory.final_trainable",
      "trajectory.final_evaluation",
      "trajectory.loss_history",
      "contract.no_mandatory_omission"
     ],
     "hard_rollback_limit_steps": 0,
     "passed": false,
     "schema_version": "recovery-gate-v1"
    },
    "limitations": [
     "Physical NAND writes, write amplification, and SSD lifetime were not measured.",
     "No GPT provider, diagnosis, repair execution, HTML, or packaging is part of Prompt 3."
    ],
    "platform_support_note": "Windows: payload and metadata files are fsynced and directory rename is atomic; directory fsync is unavailable through Python and remains best-effort.",
    "profile": "ci",
    "recovery": {
     "after_restore": {
      "evaluation_sha256": "d60572aea12f91960f3f0030bdfdca55fdafe059146c7230af9094923811d312",
      "global_step": 4,
      "loss_history": [
       3.5371975898742676,
       3.434457540512085,
       3.5977065563201904,
       3.560746669769287
      ],
      "optimizer_sha256": "3fd0f50e0b483fd549520296f88ec6164c60dd8e753da543bff7ba535d9e6de3",
      "scheduler_sha256": "78a0339e12abed3272bbbaab1f3ae6759b55eaf3f3ee807f998c5cc92113cfa8",
      "trainable_state_sha256": "43ba75808906932a005b0d3e186b5786ab64a25fdce5542655d2d0951fc6eeb5"
     },
     "after_restore_rng": {
      "numpy_sha256": "adc7e545ec0530eae9f1da725e83f48b146bd4ec79f98451367ca3d18e994db5",
      "python_sha256": "dd8aec1ccf3053de61ed6a459e2668c385b7996eaedd947444006209995a7063",
      "torch_sha256": "56a59ee4154c876386d9afa96a2427f79a736e98887cc6077a6409d0affee290"
     },
     "checkpoint_path": "checkpoints/missing-training-state/checkpoint-step-000004",
     "completed_at": "2026-07-20T01:29:04.669645Z",
     "final": {
      "evaluation_sha256": "4346a2d77b37076b853d4529981824edd549538f938d4964220899149dd5b4cd",
      "global_step": 8,
      "loss_history": [
       3.5371975898742676,
       3.434457540512085,
       3.5977065563201904,
       3.560746669769287,
       3.5904791355133057,
       3.6091108322143555,
       3.5213661193847656,
       3.8659350872039795
      ],
      "optimizer_sha256": "e803114b5056070d75a3f02f6a1cd987f62b0d84fcb53350bb43e84757f29efa",
      "scheduler_sha256": "caa817fb3191ab1456ade00320565fb3dfb7e7e648a1207f3f22f04893dec770",
      "trainable_state_sha256": "d28547e82dc412d58060e8be64deb52191b7b258561be47874694b1c546eca66"
     },
     "first_completed_step": 5,
     "first_resumed_batch_step": 4,
     "restored_global_step": 4,
     "schema_version": "recovery-worker-result-v1",
     "started_at": "2026-07-20T01:29:03.186671Z",
     "strategy": "missing_training_state",
     "worker_pid": 16600
    },
    "recovery_process": {
     "completed_at": "2026-07-20T01:29:05.088631Z",
     "exit_code": 0,
     "exit_verified": true,
     "started_at": "2026-07-20T01:28:59.179201Z",
     "worker_pid": 16600
    },
    "result_path": "result.json",
    "run_id": "initial",
    "schema_version": "crash-experiment-v1",
    "strategy": "missing_training_state"
   },
   "limitations": [
    "No live API call occurs; the diagnosis is an accepted GPT-5.6 capture replay.",
    "A failed repaired gate stops closed without another diagnosis or repair attempt.",
    "safe_full remains the documented complete-state fallback and is not auto-executed.",
    "Windows directory fsync remains best-effort because Python does not expose it."
   ],
   "original_checkpoint_after": {
    "file_count": 5,
    "logical_bytes": 5169,
    "sha256": "7548ba89ea18b3b78f1ea8990dcca66a1b3cb019c4cfc712c418b2de9bbeecaa"
   },
   "original_checkpoint_before": {
    "file_count": 5,
    "logical_bytes": 5169,
    "sha256": "7548ba89ea18b3b78f1ea8990dcca66a1b3cb019c4cfc712c418b2de9bbeecaa"
   },
   "original_checkpoint_unmodified": true,
   "plan_validation": {
    "accepted_actions": [
     "persist_optimizer_state",
     "persist_scheduler_state",
     "persist_python_rng_state",
     "persist_numpy_rng_state",
     "persist_torch_rng_state",
     "restore_state_before_next_batch"
    ],
    "attempt_number": 1,
    "decisions": [
     {
      "action": "change_supported_checkpoint_strategy",
      "disposition": "unsupported",
      "evidence_ids": [
       "contract:mandatory-state"
      ],
      "reason": "Known action is unsupported by NativePyTorchAdapter in P0."
     },
     {
      "action": "persist_optimizer_state",
      "disposition": "accepted",
      "evidence_ids": [
       "restore:optimizer-state",
       "contract:mandatory-state",
       "trajectory:final-trainable",
       "trajectory:loss-history"
      ],
      "reason": "Typed action is supported and linked to request evidence."
     },
     {
      "action": "persist_scheduler_state",
      "disposition": "accepted",
      "evidence_ids": [
       "restore:scheduler-state",
       "contract:mandatory-state",
       "trajectory:final-trainable",
       "trajectory:loss-history"
      ],
      "reason": "Typed action is supported and linked to request evidence."
     },
     {
      "action": "persist_python_rng_state",
      "disposition": "accepted",
      "evidence_ids": [
       "restore:python-rng",
       "contract:mandatory-state"
      ],
      "reason": "Typed action is supported and linked to request evidence."
     },
     {
      "action": "persist_numpy_rng_state",
      "disposition": "accepted",
      "evidence_ids": [
       "restore:numpy-rng",
       "contract:mandatory-state"
      ],
      "reason": "Typed action is supported and linked to request evidence."
     },
     {
      "action": "persist_torch_rng_state",
      "disposition": "accepted",
      "evidence_ids": [
       "restore:torch-rng",
       "contract:mandatory-state",
       "trajectory:final-trainable",
       "trajectory:final-evaluation",
       "trajectory:loss-history"
      ],
      "reason": "Typed action is supported and linked to request evidence."
     },
     {
      "action": "restore_state_before_next_batch",
      "disposition": "accepted",
      "evidence_ids": [
       "restore:optimizer-state",
       "restore:scheduler-state",
       "restore:python-rng",
       "restore:numpy-rng",
       "restore:torch-rng",
       "process:next-step"
      ],
      "reason": "Typed action is supported and linked to request evidence."
     }
    ],
    "execution_performed": false,
    "rejected_actions": [],
    "schema_version": "repair-plan-validation-v1",
    "unsupported_actions": [
     "change_supported_checkpoint_strategy"
    ]
   },
   "profile": "ci",
   "proposed_analysis": {
    "affected_gate_checks": [
     "state.optimizer",
     "state.scheduler",
     "state.python_rng",
     "state.numpy_rng",
     "state.torch_rng",
     "trajectory.final_trainable",
     "trajectory.final_evaluation",
     "trajectory.loss_history",
     "contract.no_mandatory_omission"
    ],
    "confidence": "high",
    "confirming_evidence": [
     "restore:optimizer-state",
     "restore:scheduler-state",
     "restore:python-rng",
     "restore:numpy-rng",
     "restore:torch-rng",
     "trajectory:final-trainable",
     "trajectory:final-evaluation",
     "trajectory:loss-history",
     "contract:mandatory-state"
    ],
    "limitations": [
     "The package demonstrates the omissions and resulting divergence but does not establish that any proposed repair has been implemented or validated.",
     "Exact recovery remains subject to deterministic validation using a newly produced checkpoint containing all mandatory state.",
     "The matching Python and NumPy RNG digests do not satisfy the serialization requirement because those states were not present in the checkpoint."
    ],
    "repair_plan": {
     "actions": [
      {
       "action": "change_supported_checkpoint_strategy",
       "evidence_ids": [
        "contract:mandatory-state"
       ],
       "reason": "The current strategy advertises no supported repair actions and must be replaced or extended to support all mandatory continuation state."
      },
      {
       "action": "persist_optimizer_state",
       "evidence_ids": [
        "restore:optimizer-state",
        "contract:mandatory-state",
        "trajectory:final-trainable",
        "trajectory:loss-history"
       ],
       "reason": "Serialize the complete optimizer state required for exact continuation."
      },
      {
       "action": "persist_scheduler_state",
       "evidence_ids": [
        "restore:scheduler-state",
        "contract:mandatory-state",
        "trajectory:final-trainable",
        "trajectory:loss-history"
       ],
       "reason": "Serialize scheduler progress so resumed learning-rate behavior matches the uninterrupted run."
      },
      {
       "action": "persist_python_rng_state",
       "evidence_ids": [
        "restore:python-rng",
        "contract:mandatory-state"
       ],
       "reason": "Serialize Python RNG state because the workload requires it for strict continuation."
      },
      {
       "action": "persist_numpy_rng_state",
       "evidence_ids": [
        "restore:numpy-rng",
        "contract:mandatory-state"
       ],
       "reason": "Serialize NumPy RNG state because the workload uses NumPy randomness."
      },
      {
       "action": "persist_torch_rng_state",
       "evidence_ids": [
        "restore:torch-rng",
        "contract:mandatory-state",
        "trajectory:final-trainable",
        "trajectory:final-evaluation",
        "trajectory:loss-history"
       ],
       "reason": "Serialize Torch RNG state because the workload uses Torch randomness and dropout."
      },
      {
       "action": "restore_state_before_next_batch",
       "evidence_ids": [
        "restore:optimizer-state",
        "restore:scheduler-state",
        "restore:python-rng",
        "restore:numpy-rng",
        "restore:torch-rng",
        "process:next-step"
       ],
       "reason": "Restore all persisted optimizer, scheduler, and RNG state before processing the next batch."
      }
     ],
     "assumptions": [
      "The controlled CPU-only workload and declared state requirements remain unchanged.",
      "No CUDA RNG state is required.",
      "Batch position remains derivable from the restored global step."
     ],
     "expected_gate_improvements": [
      "Mandatory continuation state is declared and serialized.",
      "Optimizer, scheduler, and required RNG states become restorable with exact digests.",
      "Continued losses, final trainable parameters, and final evaluation outputs can be re-evaluated for exact agreement."
     ],
     "risks": [
      "The current checkpoint strategy exposes no supported repair actions, so a compatible strategy or implementation change is required before these actions can be validated.",
      "Existing checkpoints lacking the omitted state cannot provide strict continuation from those checkpoints.",
      "Restoration ordering errors could still produce trajectory divergence even after all state is serialized."
     ]
    },
    "root_cause_hypothesis": "The checkpoint strategy serialized the adapter and global step but omitted mandatory optimizer, scheduler, Python RNG, NumPy RNG, and Torch RNG state. Recovery therefore resumed with incomplete continuation state, causing divergence in losses, final trainable parameters, and final evaluation outputs.",
    "schema_version": "failure-analysis-v2"
   },
   "repair_attempt_count": 1,
   "repair_execution": {
    "admitted_at": "2026-07-20T01:29:05.191509Z",
    "applied_actions": [
     "persist_optimizer_state",
     "persist_scheduler_state",
     "persist_python_rng_state",
     "persist_numpy_rng_state",
     "persist_torch_rng_state",
     "restore_state_before_next_batch"
    ],
    "attempt_number": 1,
    "execution_performed": true,
    "original_config": {
     "include_numpy_rng": false,
     "include_optimizer": false,
     "include_python_rng": false,
     "include_scheduler": false,
     "include_torch_rng": false,
     "restore_before_next_batch": false,
     "schema_version": "checkpoint-strategy-config-v1",
     "strategy_id": "native-incomplete-v1"
    },
    "rejected_actions": [],
    "repaired_config": {
     "include_numpy_rng": true,
     "include_optimizer": true,
     "include_python_rng": true,
     "include_scheduler": true,
     "include_torch_rng": true,
     "restore_before_next_batch": true,
     "schema_version": "checkpoint-strategy-config-v1",
     "strategy_id": "native-repaired-complete-v1"
    },
    "schema_version": "repair-execution-v1",
    "unsupported_actions": [
     "change_supported_checkpoint_strategy"
    ]
   },
   "repaired_run": {
    "control": {
     "evaluation_sha256": "a42a6d25c8aaf6674130ef63439f6fd415824bd23ff9cd6a7c0ca0305be3ef9a",
     "global_step": 8,
     "loss_history": [
      3.5371975898742676,
      3.434457540512085,
      3.5977065563201904,
      3.560746669769287,
      3.670823574066162,
      3.627253293991089,
      3.508639335632324,
      3.8248143196105957
     ],
     "optimizer_sha256": "c03dfc8b66e6645fb552223428ad86a855c97049d133b08984604f6e7d55a050",
     "scheduler_sha256": "e07ffd6a89fefb61e80d1ca56025a927222a83180ffced778789606d3a7bec81",
     "trainable_state_sha256": "1fc72fdf21487afe7b32da833d2300cd9a68f0c0c6f3ce1456910a5102a92997"
    },
    "crash": {
     "checkpoint_path": "checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004",
     "checkpoint_step": 4,
     "event_received_at": "2026-07-20T01:29:08.921856Z",
     "last_completed_step": 4,
     "terminated_at": "2026-07-20T01:29:08.944239Z",
     "termination_exit_code": 1,
     "termination_method": "TerminateProcess via subprocess.Popen.kill",
     "termination_verified": true,
     "worker_pid": 27632
    },
    "created_at": "2026-07-20T01:29:12.925243Z",
    "failure_artifact_path": null,
    "gate": {
     "achieved_rollback_steps": 0,
     "checks": [
      {
       "actual": "checkpoint-manifest-v1",
       "category": "Integrity",
       "check_id": "integrity.manifest_schema",
       "details": null,
       "evidence_ids": [
        "manifest:schema"
       ],
       "expected": "checkpoint-manifest-v1",
       "label": "Manifest schema valid",
       "status": "pass"
      },
      {
       "actual": "present",
       "category": "Integrity",
       "check_id": "integrity.completion_marker",
       "details": null,
       "evidence_ids": [
        "integrity:completion-marker"
       ],
       "expected": "COMPLETE present in final checkpoint",
       "label": "Completion marker present",
       "status": "pass"
      },
      {
       "actual": "5 payloads validated",
       "category": "Integrity",
       "check_id": "integrity.checksums",
       "details": null,
       "evidence_ids": [
        "integrity:sha256"
       ],
       "expected": "every manifest payload matches SHA-256 and size",
       "label": "All payload checksums valid",
       "status": "pass"
      },
      {
       "actual": "present",
       "category": "Integrity",
       "check_id": "integrity.base_present",
       "details": null,
       "evidence_ids": [
        "base:presence"
       ],
       "expected": "contained immutable base artifact",
       "label": "Base artifact present when required",
       "status": "pass"
      },
      {
       "actual": "c17cc8994c8f0fe6def32423b0e5d9efedffb3cd71c7de9631f26cf505925d86",
       "category": "Integrity",
       "check_id": "integrity.base_hash",
       "details": null,
       "evidence_ids": [
        "base:sha256"
       ],
       "expected": "c17cc8994c8f0fe6def32423b0e5d9efedffb3cd71c7de9631f26cf505925d86",
       "label": "Base artifact hash matches",
       "status": "pass"
      },
      {
       "actual": "manifest=4, event=4, restored=4",
       "category": "Required training state",
       "check_id": "state.global_step",
       "details": null,
       "evidence_ids": [
        "manifest:global-step"
       ],
       "expected": "0 < step < 8, consistent across restore",
       "label": "Checkpoint global step is valid",
       "status": "pass"
      },
      {
       "actual": "serialized=True, digest_match=True",
       "category": "Required training state",
       "check_id": "state.model_or_adapter",
       "details": null,
       "evidence_ids": [
        "restore:model-state"
       ],
       "expected": "serialized adapter and exact trainable-state digest",
       "label": "Model or adapter state restores",
       "status": "pass"
      },
      {
       "actual": "serialized=True, digest_match=True",
       "category": "Required training state",
       "check_id": "state.optimizer",
       "details": null,
       "evidence_ids": [
        "restore:optimizer-state"
       ],
       "expected": "serialized optimizer with exact digest",
       "label": "Optimizer state restores when required",
       "status": "pass"
      },
      {
       "actual": "serialized=True, digest_match=True",
       "category": "Required training state",
       "check_id": "state.scheduler",
       "details": null,
       "evidence_ids": [
        "restore:scheduler-state"
       ],
       "expected": "serialized scheduler with exact digest",
       "label": "Scheduler state restores when required",
       "status": "pass"
      },
      {
       "actual": "serialized=True, digest_match=True",
       "category": "Required training state",
       "check_id": "state.python_rng",
       "details": null,
       "evidence_ids": [
        "restore:python-rng"
       ],
       "expected": "serialized state with exact digest",
       "label": "Python RNG state restores when required",
       "status": "pass"
      },
      {
       "actual": "serialized=True, digest_match=True",
       "category": "Required training state",
       "check_id": "state.numpy_rng",
       "details": null,
       "evidence_ids": [
        "restore:numpy-rng"
       ],
       "expected": "serialized state with exact digest",
       "label": "NumPy RNG state restores when required",
       "status": "pass"
      },
      {
       "actual": "serialized=True, digest_match=True",
       "category": "Required training state",
       "check_id": "state.torch_rng",
       "details": null,
       "evidence_ids": [
        "restore:torch-rng"
       ],
       "expected": "serialized state with exact digest",
       "label": "Torch RNG state restores when required",
       "status": "pass"
      },
      {
       "actual": "first batch at 4, first completion at 5",
       "category": "Process recovery",
       "check_id": "process.next_step",
       "details": null,
       "evidence_ids": [
        "process:next-step"
       ],
       "expected": "first batch at 4, first completion at 5",
       "label": "Resumed run continues from the expected next step",
       "status": "pass"
      },
      {
       "actual": "27632",
       "category": "Process recovery",
       "check_id": "process.original_pid",
       "details": null,
       "evidence_ids": [
        "process:original-pid"
       ],
       "expected": "27632",
       "label": "Original worker PID is recorded",
       "status": "pass"
      },
      {
       "actual": "method=TerminateProcess via subprocess.Popen.kill, exit=1, verified=True",
       "category": "Process recovery",
       "check_id": "process.expected_termination",
       "details": null,
       "evidence_ids": [
        "process:termination"
       ],
       "expected": "parent termination with nonzero exit code",
       "label": "Original worker termination is verified",
       "status": "pass"
      },
      {
       "actual": "31396",
       "category": "Process recovery",
       "check_id": "process.new_recovery_pid",
       "details": null,
       "evidence_ids": [
        "process:recovery-pid"
       ],
       "expected": "PID different from 27632",
       "label": "Recovery uses a different PID",
       "status": "pass"
      },
      {
       "actual": "exit=0, verified=True",
       "category": "Process recovery",
       "check_id": "process.recovery_exit",
       "details": null,
       "evidence_ids": [
        "process:recovery-exit"
       ],
       "expected": "exit code 0",
       "label": "Recovery worker exits successfully",
       "status": "pass"
      },
      {
       "actual": "0 steps",
       "category": "Safety and rollback",
       "check_id": "rollback.hard_limit",
       "details": null,
       "evidence_ids": [
        "rollback:achieved"
       ],
       "expected": "<= 0 steps",
       "label": "Achieved rollback is within the hard limit",
       "status": "pass"
      },
      {
       "actual": "d60572aea12f91960f3f0030bdfdca55fdafe059146c7230af9094923811d312",
       "category": "Trajectory correctness",
       "check_id": "trajectory.checkpoint_evaluation",
       "details": "Exact SHA-256 comparison; no numerical tolerance is applied.",
       "evidence_ids": [
        "trajectory:checkpoint-evaluation"
       ],
       "expected": "d60572aea12f91960f3f0030bdfdca55fdafe059146c7230af9094923811d312",
       "label": "Fixed evaluation after restore matches",
       "status": "pass"
      },
      {
       "actual": "1fc72fdf21487afe7b32da833d2300cd9a68f0c0c6f3ce1456910a5102a92997",
       "category": "Trajectory correctness",
       "check_id": "trajectory.final_trainable",
       "details": "Exact SHA-256 comparison; no numerical tolerance is applied.",
       "evidence_ids": [
        "trajectory:final-trainable"
       ],
       "expected": "1fc72fdf21487afe7b32da833d2300cd9a68f0c0c6f3ce1456910a5102a92997",
       "label": "Final trainable parameters match control",
       "status": "pass"
      },
      {
       "actual": "a42a6d25c8aaf6674130ef63439f6fd415824bd23ff9cd6a7c0ca0305be3ef9a",
       "category": "Trajectory correctness",
       "check_id": "trajectory.final_evaluation",
       "details": "Exact SHA-256 comparison; no numerical tolerance is applied.",
       "evidence_ids": [
        "trajectory:final-evaluation"
       ],
       "expected": "a42a6d25c8aaf6674130ef63439f6fd415824bd23ff9cd6a7c0ca0305be3ef9a",
       "label": "Final evaluation logits match control",
       "status": "pass"
      },
      {
       "actual": "exact match",
       "category": "Trajectory correctness",
       "check_id": "trajectory.loss_history",
       "details": "Exact float sequence comparison; no numerical tolerance is applied.",
       "evidence_ids": [
        "trajectory:loss-history"
       ],
       "expected": "exact loss sequence equality",
       "label": "Continued loss trajectory matches control",
       "status": "pass"
      },
      {
       "actual": "contained",
       "category": "Safety and rollback",
       "check_id": "safety.path_containment",
       "details": null,
       "evidence_ids": [
        "safety:path-containment"
       ],
       "expected": "all paths contained; symlink escapes rejected",
       "label": "All managed write paths passed containment",
       "status": "pass"
      },
      {
       "actual": "complete",
       "category": "Safety and rollback",
       "check_id": "contract.no_mandatory_omission",
       "details": null,
       "evidence_ids": [
        "contract:mandatory-state"
       ],
       "expected": "all mandatory continuation state declared",
       "label": "No mandatory contract requirement was silently omitted",
       "status": "pass"
      }
     ],
     "comparison_policy": {
      "atol": 0.0,
      "evaluation_logits": "sha256_exact",
      "evidence": "The controlled CPU workload uses deterministic algorithms, one Torch thread, fixed seeds, and step-derived batches. Cross-process comparisons fail on any digest or loss-sequence difference.",
      "loss_history": "sequence_exact",
      "mode": "exact",
      "optimizer_state": "sha256_exact",
      "rng_state": "sha256_exact",
      "rtol": 0.0,
      "scheduler_state": "sha256_exact",
      "trainable_parameters": "sha256_exact"
     },
     "failed_check_ids": [],
     "hard_rollback_limit_steps": 0,
     "passed": true,
     "schema_version": "recovery-gate-v1"
    },
    "limitations": [
     "Physical NAND writes, write amplification, and SSD lifetime were not measured.",
     "No GPT provider, diagnosis, repair execution, HTML, or packaging is part of Prompt 3."
    ],
    "platform_support_note": "Windows: payload and metadata files are fsynced and directory rename is atomic; directory fsync is unavailable through Python and remains best-effort.",
    "profile": "ci",
    "recovery": {
     "after_restore": {
      "evaluation_sha256": "d60572aea12f91960f3f0030bdfdca55fdafe059146c7230af9094923811d312",
      "global_step": 4,
      "loss_history": [
       3.5371975898742676,
       3.434457540512085,
       3.5977065563201904,
       3.560746669769287
      ],
      "optimizer_sha256": "9d74c2ab1d0065b9a270080cbacd3ccdf2937e8c2aee112d50171dec423a0a3a",
      "scheduler_sha256": "caa817fb3191ab1456ade00320565fb3dfb7e7e648a1207f3f22f04893dec770",
      "trainable_state_sha256": "43ba75808906932a005b0d3e186b5786ab64a25fdce5542655d2d0951fc6eeb5"
     },
     "after_restore_rng": {
      "numpy_sha256": "adc7e545ec0530eae9f1da725e83f48b146bd4ec79f98451367ca3d18e994db5",
      "python_sha256": "dd8aec1ccf3053de61ed6a459e2668c385b7996eaedd947444006209995a7063",
      "torch_sha256": "fa163c67bdc6bd308e73799701eff603b07e6196b09748af3a051a16d257ca62"
     },
     "checkpoint_path": "checkpoints/repaired/native-repaired-complete-v1/checkpoint-step-000004",
     "completed_at": "2026-07-20T01:29:12.418105Z",
     "final": {
      "evaluation_sha256": "a42a6d25c8aaf6674130ef63439f6fd415824bd23ff9cd6a7c0ca0305be3ef9a",
      "global_step": 8,
      "loss_history": [
       3.5371975898742676,
       3.434457540512085,
       3.5977065563201904,
       3.560746669769287,
       3.670823574066162,
       3.627253293991089,
       3.508639335632324,
       3.8248143196105957
      ],
      "optimizer_sha256": "c03dfc8b66e6645fb552223428ad86a855c97049d133b08984604f6e7d55a050",
      "scheduler_sha256": "e07ffd6a89fefb61e80d1ca56025a927222a83180ffced778789606d3a7bec81",
      "trainable_state_sha256": "1fc72fdf21487afe7b32da833d2300cd9a68f0c0c6f3ce1456910a5102a92997"
     },
     "first_completed_step": 5,
     "first_resumed_batch_step": 4,
     "restored_global_step": 4,
     "schema_version": "recovery-worker-result-v1",
     "started_at": "2026-07-20T01:29:10.998216Z",
     "strategy": "safe_adapter_aware",
     "worker_pid": 31396
    },
    "recovery_process": {
     "completed_at": "2026-07-20T01:29:12.909694Z",
     "exit_code": 0,
     "exit_verified": true,
     "started_at": "2026-07-20T01:29:08.944239Z",
     "worker_pid": 31396
    },
    "result_path": "result.json",
    "run_id": "repaired",
    "schema_version": "crash-experiment-v1",
    "strategy": "safe_adapter_aware"
   },
   "replay_call_metadata": {
    "fixture_provenance": "live_gpt_5_6_capture",
    "live_or_fixture": "fixture",
    "model": "gpt-5.6",
    "output_schema_version": "failure-analysis-v2",
    "prompt_version": "v2",
    "provider": "fixture",
    "request_sha256": "ae0ab9ea64dad5dd68d3437d27649987295637630d47647d9b2f27f9db06b178",
    "response_id": null,
    "role": "failure-analysis",
    "schema_version": "agent-call-metadata-v1",
    "source": "captured_live_response_replay",
    "store": false,
    "timestamp": "2026-07-20T01:29:05.160396Z",
    "validation_status": "accepted"
   },
   "report_path": "report.md",
   "result_path": "result.json",
   "run_id": "milestone13-native",
   "schema_version": "repair-loop-result-v1",
   "storage_comparison": {
    "checkpoint_step": 4,
    "limitations": [
     "The repaired recurring total excludes the immutable base artifact stored once per run.",
     "Logical file bytes are measured; physical NAND writes and write amplification are not.",
     "The safe_full source is the unchanged direct-restore measurement implementation."
    ],
    "measurement_scope": "logical_checkpoint_directory_bytes",
    "profile": "ci",
    "repaired_one_time_base_bytes": 18475,
    "repaired_recurring_bytes": 27681,
    "reported_after_recovery_passed": true,
    "safe_full_bytes": 44998,
    "safe_full_measurement_source": "unchanged_safe_full_direct_restore_baseline",
    "schema_version": "storage-comparison-v1",
    "structural_reduction_bytes": 17317,
    "structural_reduction_percent": 38.483932619227524
   }
  },
  "source_run": "milestone13-native",
  "subtitle": "Contract violation detected, repaired, then re-qualified end to end.",
  "title": "Native PyTorch — repair loop",
  "verdict": "VERIFIED"
 },
 {
  "attestation": null,
  "attestation_junit": null,
  "contract": null,
  "environment": null,
  "evidence_files": {},
  "evidence_missing": [],
  "id": "lightning-complete",
  "job_summary": null,
  "junit": null,
  "kind": "qualification",
  "manifest": null,
  "result": {
   "adapter": "pytorch-lightning",
   "checkpoint_event": {
    "checkpoint_path": "crash/checkpoints/checkpoint-4",
    "emitted_at": "2026-07-20T10:54:49.163300Z",
    "event": "checkpoint_committed",
    "global_step": 4,
    "loop_state_present": true,
    "loss_history_present": true,
    "model_present": true,
    "optimizer_present": true,
    "rng_state_present": true,
    "scenario": "complete",
    "scheduler_present": true,
    "schema_version": "flashpilot-lightning-checkpoint-event-v1",
    "worker_pid": 17600
   },
   "checkpoint_inventory": [
    "callbacks",
    "epoch",
    "flashpilot_exact_resume",
    "global_step",
    "hparams_name",
    "hyper_parameters",
    "loops",
    "lr_schedulers",
    "optimizer_states",
    "pytorch-lightning_version",
    "state_dict"
   ],
   "control": {
    "checkpoint_step": 0,
    "cpu_only": true,
    "evaluation_sha256": "966c02c178cef1bbef7d07b1cc491f45bb1ee288992a7657bd036f80a4143636",
    "lightning_version": "2.6.5",
    "loss_history": [
     0.32196044921875,
     0.24109923839569092,
     0.422993540763855,
     0.18924395740032196,
     0.42403459548950195,
     0.47362595796585083,
     0.1744976043701172,
     0.26637983322143555
    ],
    "mode": "control",
    "model_loaded_from_checkpoint": false,
    "optimizer_sha256": "fba1e94775ff1663606e8f8a61c73739a4dfcf5a7854b05e814eb977678ef140",
    "scenario": "complete",
    "scheduler_sha256": "ce8fc7b9958043b43b1af5683656e04bb77f6d1cce16b011849df3083cad06d0",
    "schema_version": "flashpilot-lightning-run-summary-v1",
    "semantic_global_step": 8,
    "torch_version": "2.13.0+cpu",
    "trainable_state_sha256": "92147948cf1bbb326c6ccf31bd456d37d2c06a8c6702717afac683b7cd7370af",
    "trainer_global_step": 8,
    "worker_pid": 30976
   },
   "control_process": {
    "completed_at": "2026-07-20T10:54:42.590998Z",
    "exit_code": 0,
    "exit_verified": true,
    "started_at": "2026-07-20T10:54:34.507586Z",
    "worker_pid": 30976
   },
   "crash_process": {
    "completed_at": "2026-07-20T10:54:49.227478Z",
    "exit_code": 1,
    "exit_verified": true,
    "started_at": "2026-07-20T10:54:42.621501Z",
    "worker_pid": 17600
   },
   "created_at": "2026-07-20T10:54:56.107756Z",
   "fault_scenario": "process-kill",
   "final_verdict": "VERIFIED",
   "forwarded_arguments": [],
   "framework": "lightning",
   "gate": {
    "achieved_rpo_steps": 0,
    "atol": 0.0,
    "checks": [
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.model",
      "expected": "present",
      "label": "Model state is present",
      "status": "pass"
     },
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.loop-state",
      "expected": "present",
      "label": "Loop state is present",
      "status": "pass"
     },
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.optimizer",
      "expected": "present",
      "label": "Optimizer state is present",
      "status": "pass"
     },
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.scheduler",
      "expected": "present",
      "label": "Scheduler state is present",
      "status": "pass"
     },
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.rng",
      "expected": "present",
      "label": "RNG state is present",
      "status": "pass"
     },
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.loss-history",
      "expected": "present",
      "label": "Loss history is present",
      "status": "pass"
     },
     {
      "actual": "verified=True, exit=1",
      "category": "process",
      "check_id": "process.real-termination",
      "expected": "verified nonzero exit",
      "label": "Checkpoint worker was really terminated",
      "status": "pass"
     },
     {
      "actual": "17600 -> 12104",
      "category": "process",
      "check_id": "process.distinct-recovery",
      "expected": "distinct PIDs",
      "label": "Recovery ran in a new process",
      "status": "pass"
     },
     {
      "actual": "8",
      "category": "trajectory",
      "check_id": "progress.global-step",
      "expected": "8",
      "label": "Recovered global step matches control",
      "status": "pass"
     },
     {
      "actual": "exact match",
      "category": "trajectory",
      "check_id": "trajectory.loss-history",
      "expected": "exact control loss history",
      "label": "Loss history exactly matches control",
      "status": "pass"
     },
     {
      "actual": "92147948cf1bbb326c6ccf31bd456d37d2c06a8c6702717afac683b7cd7370af",
      "category": "state",
      "check_id": "state.trainable",
      "expected": "92147948cf1bbb326c6ccf31bd456d37d2c06a8c6702717afac683b7cd7370af",
      "label": "Trainable state digest exactly matches control",
      "status": "pass"
     },
     {
      "actual": "966c02c178cef1bbef7d07b1cc491f45bb1ee288992a7657bd036f80a4143636",
      "category": "state",
      "check_id": "state.evaluation",
      "expected": "966c02c178cef1bbef7d07b1cc491f45bb1ee288992a7657bd036f80a4143636",
      "label": "Evaluation digest exactly matches control",
      "status": "pass"
     },
     {
      "actual": "fba1e94775ff1663606e8f8a61c73739a4dfcf5a7854b05e814eb977678ef140",
      "category": "state",
      "check_id": "state.optimizer",
      "expected": "fba1e94775ff1663606e8f8a61c73739a4dfcf5a7854b05e814eb977678ef140",
      "label": "Optimizer digest exactly matches control",
      "status": "pass"
     },
     {
      "actual": "ce8fc7b9958043b43b1af5683656e04bb77f6d1cce16b011849df3083cad06d0",
      "category": "state",
      "check_id": "state.scheduler",
      "expected": "ce8fc7b9958043b43b1af5683656e04bb77f6d1cce16b011849df3083cad06d0",
      "label": "Scheduler digest exactly matches control",
      "status": "pass"
     }
    ],
    "failed_check_ids": [],
    "max_rpo_steps": 0,
    "passed": true,
    "rtol": 0.0,
    "schema_version": "flashpilot-lightning-recovery-gate-v1"
   },
   "html_report_path": "report.html",
   "limitations": [
    "Qualification covers the included CPU LightningModule, not arbitrary modules.",
    "The RNG bridge is explicit module checkpoint state required by this contract.",
    "The attestation is unsigned and provides integrity, not publisher authentication."
   ],
   "model_checkpoint_load_succeeded": true,
   "qualification_profile": "exact-training-resume",
   "recovery": {
    "checkpoint_step": 4,
    "cpu_only": true,
    "evaluation_sha256": "966c02c178cef1bbef7d07b1cc491f45bb1ee288992a7657bd036f80a4143636",
    "lightning_version": "2.6.5",
    "loss_history": [
     0.32196044921875,
     0.24109923839569092,
     0.422993540763855,
     0.18924395740032196,
     0.42403459548950195,
     0.47362595796585083,
     0.1744976043701172,
     0.26637983322143555
    ],
    "mode": "recover",
    "model_loaded_from_checkpoint": true,
    "optimizer_sha256": "fba1e94775ff1663606e8f8a61c73739a4dfcf5a7854b05e814eb977678ef140",
    "scenario": "complete",
    "scheduler_sha256": "ce8fc7b9958043b43b1af5683656e04bb77f6d1cce16b011849df3083cad06d0",
    "schema_version": "flashpilot-lightning-run-summary-v1",
    "semantic_global_step": 8,
    "torch_version": "2.13.0+cpu",
    "trainable_state_sha256": "92147948cf1bbb326c6ccf31bd456d37d2c06a8c6702717afac683b7cd7370af",
    "trainer_global_step": 8,
    "worker_pid": 12104
   },
   "recovery_process": {
    "completed_at": "2026-07-20T10:54:56.076398Z",
    "exit_code": 0,
    "exit_verified": true,
    "started_at": "2026-07-20T10:54:49.258910Z",
    "worker_pid": 12104
   },
   "report_path": "report.md",
   "result_path": "result.json",
   "run_id": "f24c113605074d618550e38bdb987f2c",
   "scenario": "complete",
   "schema_version": "flashpilot-lightning-qualification-v1",
   "script_path": "inputs/train.py",
   "verified_persisted_bytes": 22703,
   "weights_only_diverged": false
  },
  "source_run": "dev-lightning-complete-3",
  "subtitle": "Same gate, different framework: VERIFIED.",
  "title": "PyTorch Lightning — complete checkpoint",
  "verdict": "VERIFIED"
 },
 {
  "attestation": null,
  "attestation_junit": null,
  "contract": null,
  "environment": null,
  "evidence_files": {},
  "evidence_missing": [],
  "id": "lightning-weights-only",
  "job_summary": null,
  "junit": null,
  "kind": "qualification",
  "manifest": null,
  "result": {
   "adapter": "pytorch-lightning",
   "checkpoint_event": {
    "checkpoint_path": "crash/checkpoints/checkpoint-4",
    "emitted_at": "2026-07-20T10:56:26.556514Z",
    "event": "checkpoint_committed",
    "global_step": 4,
    "loop_state_present": true,
    "loss_history_present": false,
    "model_present": true,
    "optimizer_present": false,
    "rng_state_present": false,
    "scenario": "weights-only",
    "scheduler_present": false,
    "schema_version": "flashpilot-lightning-checkpoint-event-v1",
    "worker_pid": 32492
   },
   "checkpoint_inventory": [
    "epoch",
    "global_step",
    "hparams_name",
    "hyper_parameters",
    "loops",
    "pytorch-lightning_version",
    "state_dict"
   ],
   "control": {
    "checkpoint_step": 0,
    "cpu_only": true,
    "evaluation_sha256": "966c02c178cef1bbef7d07b1cc491f45bb1ee288992a7657bd036f80a4143636",
    "lightning_version": "2.6.5",
    "loss_history": [
     0.32196044921875,
     0.24109923839569092,
     0.422993540763855,
     0.18924395740032196,
     0.42403459548950195,
     0.47362595796585083,
     0.1744976043701172,
     0.26637983322143555
    ],
    "mode": "control",
    "model_loaded_from_checkpoint": false,
    "optimizer_sha256": "fba1e94775ff1663606e8f8a61c73739a4dfcf5a7854b05e814eb977678ef140",
    "scenario": "weights-only",
    "scheduler_sha256": "ce8fc7b9958043b43b1af5683656e04bb77f6d1cce16b011849df3083cad06d0",
    "schema_version": "flashpilot-lightning-run-summary-v1",
    "semantic_global_step": 8,
    "torch_version": "2.13.0+cpu",
    "trainable_state_sha256": "92147948cf1bbb326c6ccf31bd456d37d2c06a8c6702717afac683b7cd7370af",
    "trainer_global_step": 8,
    "worker_pid": 9280
   },
   "control_process": {
    "completed_at": "2026-07-20T10:56:15.639003Z",
    "exit_code": 0,
    "exit_verified": true,
    "started_at": "2026-07-20T10:56:06.072834Z",
    "worker_pid": 9280
   },
   "crash_process": {
    "completed_at": "2026-07-20T10:56:26.627493Z",
    "exit_code": 1,
    "exit_verified": true,
    "started_at": "2026-07-20T10:56:15.679144Z",
    "worker_pid": 32492
   },
   "created_at": "2026-07-20T10:56:38.238186Z",
   "fault_scenario": "process-kill",
   "final_verdict": "FAILED",
   "forwarded_arguments": [],
   "framework": "lightning",
   "gate": {
    "achieved_rpo_steps": 0,
    "atol": 0.0,
    "checks": [
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.model",
      "expected": "present",
      "label": "Model state is present",
      "status": "pass"
     },
     {
      "actual": "present",
      "category": "checkpoint",
      "check_id": "checkpoint.loop-state",
      "expected": "present",
      "label": "Loop state is present",
      "status": "pass"
     },
     {
      "actual": "missing",
      "category": "checkpoint",
      "check_id": "checkpoint.optimizer",
      "expected": "present",
      "label": "Optimizer state is present",
      "status": "fail"
     },
     {
      "actual": "missing",
      "category": "checkpoint",
      "check_id": "checkpoint.scheduler",
      "expected": "present",
      "label": "Scheduler state is present",
      "status": "fail"
     },
     {
      "actual": "missing",
      "category": "checkpoint",
      "check_id": "checkpoint.rng",
      "expected": "present",
      "label": "RNG state is present",
      "status": "fail"
     },
     {
      "actual": "missing",
      "category": "checkpoint",
      "check_id": "checkpoint.loss-history",
      "expected": "present",
      "label": "Loss history is present",
      "status": "fail"
     },
     {
      "actual": "verified=True, exit=1",
      "category": "process",
      "check_id": "process.real-termination",
      "expected": "verified nonzero exit",
      "label": "Checkpoint worker was really terminated",
      "status": "pass"
     },
     {
      "actual": "32492 -> 24156",
      "category": "process",
      "check_id": "process.distinct-recovery",
      "expected": "distinct PIDs",
      "label": "Recovery ran in a new process",
      "status": "pass"
     },
     {
      "actual": "8",
      "category": "trajectory",
      "check_id": "progress.global-step",
      "expected": "8",
      "label": "Recovered global step matches control",
      "status": "pass"
     },
     {
      "actual": "different",
      "category": "trajectory",
      "check_id": "trajectory.loss-history",
      "expected": "exact control loss history",
      "label": "Loss history exactly matches control",
      "status": "fail"
     },
     {
      "actual": "133a4fe54c8b225b57b9a7eb3de1b8bd58ab4eceb1c1b2e13e27b394c79f8e4c",
      "category": "state",
      "check_id": "state.trainable",
      "expected": "92147948cf1bbb326c6ccf31bd456d37d2c06a8c6702717afac683b7cd7370af",
      "label": "Trainable state digest exactly matches control",
      "status": "fail"
     },
     {
      "actual": "8f385ba69b9e891864258b8a3a4a032195f79f5d437f22c526fbae5087f16200",
      "category": "state",
      "check_id": "state.evaluation",
      "expected": "966c02c178cef1bbef7d07b1cc491f45bb1ee288992a7657bd036f80a4143636",
      "label": "Evaluation digest exactly matches control",
      "status": "fail"
     },
     {
      "actual": "c367ccb3b101fd9864d044163c63e88dda11f9062f3328233e5716dc42e87e90",
      "category": "state",
      "check_id": "state.optimizer",
      "expected": "fba1e94775ff1663606e8f8a61c73739a4dfcf5a7854b05e814eb977678ef140",
      "label": "Optimizer digest exactly matches control",
      "status": "fail"
     },
     {
      "actual": "32d51e072e08c2a5d51a3a2394199cad179dd799b4744d072253a2888b07af23",
      "category": "state",
      "check_id": "state.scheduler",
      "expected": "ce8fc7b9958043b43b1af5683656e04bb77f6d1cce16b011849df3083cad06d0",
      "label": "Scheduler digest exactly matches control",
      "status": "fail"
     }
    ],
    "failed_check_ids": [
     "checkpoint.optimizer",
     "checkpoint.scheduler",
     "checkpoint.rng",
     "checkpoint.loss-history",
     "trajectory.loss-history",
     "state.trainable",
     "state.evaluation",
     "state.optimizer",
     "state.scheduler"
    ],
    "max_rpo_steps": 0,
    "passed": false,
    "rtol": 0.0,
    "schema_version": "flashpilot-lightning-recovery-gate-v1"
   },
   "html_report_path": "report.html",
   "limitations": [
    "Qualification covers the included CPU LightningModule, not arbitrary modules.",
    "The RNG bridge is explicit module checkpoint state required by this contract.",
    "The attestation is unsigned and provides integrity, not publisher authentication."
   ],
   "model_checkpoint_load_succeeded": true,
   "qualification_profile": "exact-training-resume",
   "recovery": {
    "checkpoint_step": 4,
    "cpu_only": true,
    "evaluation_sha256": "8f385ba69b9e891864258b8a3a4a032195f79f5d437f22c526fbae5087f16200",
    "lightning_version": "2.6.5",
    "loss_history": [
     0.40072473883628845,
     0.37614256143569946,
     0.22858504951000214,
     0.2903594970703125
    ],
    "mode": "recover",
    "model_loaded_from_checkpoint": true,
    "optimizer_sha256": "c367ccb3b101fd9864d044163c63e88dda11f9062f3328233e5716dc42e87e90",
    "scenario": "weights-only",
    "scheduler_sha256": "32d51e072e08c2a5d51a3a2394199cad179dd799b4744d072253a2888b07af23",
    "schema_version": "flashpilot-lightning-run-summary-v1",
    "semantic_global_step": 8,
    "torch_version": "2.13.0+cpu",
    "trainable_state_sha256": "133a4fe54c8b225b57b9a7eb3de1b8bd58ab4eceb1c1b2e13e27b394c79f8e4c",
    "trainer_global_step": 4,
    "worker_pid": 24156
   },
   "recovery_process": {
    "completed_at": "2026-07-20T10:56:38.188476Z",
    "exit_code": 0,
    "exit_verified": true,
    "started_at": "2026-07-20T10:56:26.666449Z",
    "worker_pid": 24156
   },
   "report_path": "report.md",
   "result_path": "result.json",
   "run_id": "d55ab815ca5f4903a6fdc0f36455e436",
   "scenario": "weights-only",
   "schema_version": "flashpilot-lightning-qualification-v1",
   "script_path": "inputs/train.py",
   "verified_persisted_bytes": null,
   "weights_only_diverged": true
  },
  "source_run": "dev-lightning-weights-2",
  "subtitle": "The same failure class reproduces outside Hugging Face.",
  "title": "PyTorch Lightning — weights-only checkpoint",
  "verdict": "FAILED"
 },
 {
  "attestation": null,
  "attestation_junit": null,
  "contract": null,
  "environment": null,
  "evidence_files": {},
  "evidence_missing": [],
  "id": "unknown-layout",
  "job_summary": "# FlashPilot CI summary\n\n- Outcome: **UNKNOWN**\n- Evidence kind: `static-audit`\n- Framework: `unknown`\n- Qualification profile: `exact-training-resume`\n- Checks: `1/1` non-failing\n\n## Exact failed requirements\n\n- None\n\nThis summary is derived from the same typed evidence used by the local CLI.\n",
  "junit": "<?xml version='1.0' encoding='utf-8'?>\n<testsuite name=\"flashpilot.static-audit\" tests=\"1\" failures=\"0\" errors=\"0\" skipped=\"1\">\n  <properties>\n    <property name=\"status\" value=\"UNKNOWN\" />\n    <property name=\"framework\" value=\"unknown\" />\n    <property name=\"qualification_profile\" value=\"exact-training-resume\" />\n    <property name=\"recovery_verified\" value=\"false\" />\n  </properties>\n  <testcase classname=\"flashpilot.audit.unknown\" name=\"detection.framework\">\n    <skipped message=\"UNKNOWN: Checkpoint layout is unknown or ambiguous; it was not trusted.\" />\n    <system-out>Checkpoint layout is unknown or ambiguous; it was not trusted.</system-out>\n  </testcase>\n</testsuite>\n",
  "kind": "audit",
  "manifest": null,
  "result": {
   "checkpoint_name": "milestone13-unknown-checkpoint",
   "checks": [
    {
     "check_id": "detection.framework",
     "evidence_paths": [],
     "requirement_state_id": null,
     "status": "UNKNOWN",
     "summary": "Checkpoint layout is unknown or ambiguous; it was not trusted."
    }
   ],
   "framework": "unknown",
   "qualification_profile": "exact-training-resume",
   "recovery_verified": false,
   "schema_version": "flashpilot-static-audit-v1",
   "static_only": true,
   "status": "UNKNOWN"
  },
  "source_run": "milestone13-unknown-audit",
  "subtitle": "Not trusted, not guessed. UNKNOWN is never rendered as PASS.",
  "title": "Unrecognised checkpoint layout",
  "verdict": "UNKNOWN"
 }
];
