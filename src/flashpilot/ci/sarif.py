"""Strict deterministic SARIF 2.1.0 projection of existing CI evidence."""

from __future__ import annotations

import hashlib
import json
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flashpilot import __version__
from flashpilot.ci.models import CICheck, CICheckStatus, CIRunEvidence

SARIF_PATH = "results.sarif"
SARIF_VERSION = "2.1.0"
SARIF_SCHEMA_URI = (
    "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json"
)
FLASHPILOT_INFORMATION_URI = "https://github.com/cimpal55/flashpilot"


class StrictSarifModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)


class SarifMessage(StrictSarifModel):
    text: str = Field(min_length=1, max_length=4_096)


class SarifReportingConfiguration(StrictSarifModel):
    level: Literal["error"] = "error"


class SarifRuleProperties(StrictSarifModel):
    tags: tuple[str, ...] = Field(min_length=2, max_length=4)
    precision: Literal["very-high"] = "very-high"
    problem_severity: Literal["error"] = Field(
        default="error",
        serialization_alias="problem.severity",
        validation_alias="problem.severity",
    )

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, tags: tuple[str, ...]) -> tuple[str, ...]:
        if len(tags) != len(set(tags)):
            raise ValueError("SARIF rule tags must be unique")
        if any(not tag or tag != tag.strip() for tag in tags):
            raise ValueError("SARIF rule tags must be nonempty and already trimmed")
        return tags


class SarifReportingDescriptor(StrictSarifModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9_.-]*$", max_length=255)
    name: str = Field(pattern=r"^[a-z][a-z0-9_.-]*$", max_length=255)
    short_description: SarifMessage = Field(
        serialization_alias="shortDescription",
        validation_alias="shortDescription",
    )
    full_description: SarifMessage = Field(
        serialization_alias="fullDescription",
        validation_alias="fullDescription",
    )
    default_configuration: SarifReportingConfiguration = Field(
        serialization_alias="defaultConfiguration",
        validation_alias="defaultConfiguration",
    )
    help: SarifMessage
    properties: SarifRuleProperties

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if self.name != self.id:
            raise ValueError("SARIF rule name must equal its exact FlashPilot check ID")
        return self


class SarifToolComponent(StrictSarifModel):
    name: Literal["FlashPilot"] = "FlashPilot"
    semantic_version: str = Field(
        default=__version__,
        pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$",
        serialization_alias="semanticVersion",
        validation_alias="semanticVersion",
    )
    information_uri: Literal[FLASHPILOT_INFORMATION_URI] = Field(
        default=FLASHPILOT_INFORMATION_URI,
        serialization_alias="informationUri",
        validation_alias="informationUri",
    )
    rules: tuple[SarifReportingDescriptor, ...]

    @field_validator("rules")
    @classmethod
    def validate_rules(
        cls, rules: tuple[SarifReportingDescriptor, ...]
    ) -> tuple[SarifReportingDescriptor, ...]:
        identifiers = tuple(rule.id for rule in rules)
        if not identifiers or len(identifiers) != len(set(identifiers)):
            raise ValueError("SARIF rules must contain unique check IDs")
        return rules


class SarifTool(StrictSarifModel):
    driver: SarifToolComponent


class SarifArtifactLocation(StrictSarifModel):
    uri: Literal[
        "audit.json",
        "result.json",
        "comparison.json",
        "policy-evaluation.json",
    ]


class SarifRegion(StrictSarifModel):
    start_line: Literal[1] = Field(
        default=1,
        serialization_alias="startLine",
        validation_alias="startLine",
    )
    start_column: Literal[1] = Field(
        default=1,
        serialization_alias="startColumn",
        validation_alias="startColumn",
    )


class SarifPhysicalLocation(StrictSarifModel):
    artifact_location: SarifArtifactLocation = Field(
        serialization_alias="artifactLocation",
        validation_alias="artifactLocation",
    )
    region: SarifRegion = Field(default_factory=SarifRegion)


class SarifLocation(StrictSarifModel):
    physical_location: SarifPhysicalLocation = Field(
        serialization_alias="physicalLocation",
        validation_alias="physicalLocation",
    )
    message: SarifMessage


class SarifResultProperties(StrictSarifModel):
    flashpilot_status: Literal["FAIL", "WARN", "UNKNOWN"] = Field(
        serialization_alias="flashpilotStatus",
        validation_alias="flashpilotStatus",
    )
    evidence_kind: str = Field(
        pattern=r"^[a-z][a-z0-9-]*$",
        serialization_alias="evidenceKind",
        validation_alias="evidenceKind",
    )
    framework: str = Field(pattern=r"^[a-z][a-z0-9-]*$")
    expected: str | None = Field(default=None, max_length=4_096)
    actual: str | None = Field(default=None, max_length=4_096)


class SarifResult(StrictSarifModel):
    rule_id: str = Field(
        pattern=r"^[a-z][a-z0-9_.-]*$",
        max_length=255,
        serialization_alias="ruleId",
        validation_alias="ruleId",
    )
    rule_index: int = Field(
        ge=0,
        serialization_alias="ruleIndex",
        validation_alias="ruleIndex",
    )
    level: Literal["error", "warning"]
    message: SarifMessage
    locations: tuple[SarifLocation, ...] = Field(min_length=1, max_length=1)
    partial_fingerprints: dict[str, str] = Field(
        serialization_alias="partialFingerprints",
        validation_alias="partialFingerprints",
    )
    properties: SarifResultProperties

    @field_validator("partial_fingerprints")
    @classmethod
    def validate_fingerprint(cls, values: dict[str, str]) -> dict[str, str]:
        if set(values) != {"primaryLocationLineHash"}:
            raise ValueError("SARIF result requires one stable primary-location fingerprint")
        value = values["primaryLocationLineHash"]
        if len(value) != 66 or value[-2:] != ":1":
            raise ValueError("SARIF primary-location fingerprint has the wrong format")
        int(value[:-2], 16)
        return values


class SarifRunAutomationDetails(StrictSarifModel):
    id: str = Field(pattern=r"^flashpilot/[a-z][a-z0-9-]*/[a-z][a-z0-9-]*$")


class SarifRun(StrictSarifModel):
    tool: SarifTool
    automation_details: SarifRunAutomationDetails = Field(
        serialization_alias="automationDetails",
        validation_alias="automationDetails",
    )
    results: tuple[SarifResult, ...]

    @model_validator(mode="after")
    def validate_result_references(self) -> Self:
        rules = self.tool.driver.rules
        for result in self.results:
            if result.rule_index >= len(rules) or rules[result.rule_index].id != result.rule_id:
                raise ValueError("SARIF result does not reference its exact rule")
        return self


class FlashPilotSarifLog(StrictSarifModel):
    schema_uri: Literal[SARIF_SCHEMA_URI] = Field(
        default=SARIF_SCHEMA_URI,
        serialization_alias="$schema",
        validation_alias="$schema",
    )
    version: Literal[SARIF_VERSION] = SARIF_VERSION
    runs: tuple[SarifRun, ...] = Field(min_length=1, max_length=1)


def _result_message(check: CICheck) -> str:
    message = check.summary
    if check.expected is not None or check.actual is not None:
        message += f" Expected={check.expected!s}; actual={check.actual!s}."
    return message


def _fingerprint(
    *,
    kind: str,
    framework: str,
    check: CICheck,
    source_uri: str,
) -> str:
    identity = "\0".join((kind, framework, check.check_id, source_uri)).encode("utf-8")
    return f"{hashlib.sha256(identity).hexdigest()}:1"


def build_sarif_for_checks(
    *,
    kind: str,
    framework: str,
    checks: tuple[CICheck, ...],
    source_uri: Literal[
        "audit.json",
        "result.json",
        "comparison.json",
        "policy-evaluation.json",
    ],
) -> FlashPilotSarifLog:
    """Build one SARIF run from already-derived typed check evidence."""

    rules = tuple(
        SarifReportingDescriptor(
            id=check.check_id,
            name=check.check_id,
            shortDescription=SarifMessage(text=f"FlashPilot requirement {check.check_id}."),
            fullDescription=SarifMessage(
                text=(f"Deterministic FlashPilot checkpoint evidence requirement {check.check_id}.")
            ),
            defaultConfiguration=SarifReportingConfiguration(),
            help=SarifMessage(text="Inspect the referenced typed FlashPilot evidence artifact."),
            properties=SarifRuleProperties(
                tags=("reliability", "checkpoint-recovery", kind),
            ),
        )
        for check in checks
    )
    results = []
    for index, check in enumerate(checks):
        if check.status in {CICheckStatus.PASS, CICheckStatus.NOT_APPLICABLE}:
            continue
        message = _result_message(check)
        results.append(
            SarifResult(
                ruleId=check.check_id,
                ruleIndex=index,
                level="error" if check.status is CICheckStatus.FAIL else "warning",
                message=SarifMessage(text=message),
                locations=(
                    SarifLocation(
                        physicalLocation=SarifPhysicalLocation(
                            artifactLocation=SarifArtifactLocation(uri=source_uri),
                        ),
                        message=SarifMessage(text=f"Typed evidence for {check.check_id}."),
                    ),
                ),
                partialFingerprints={
                    "primaryLocationLineHash": _fingerprint(
                        kind=kind,
                        framework=framework,
                        check=check,
                        source_uri=source_uri,
                    )
                },
                properties=SarifResultProperties(
                    flashpilotStatus=check.status.value,
                    evidenceKind=kind,
                    framework=framework,
                    expected=check.expected,
                    actual=check.actual,
                ),
            )
        )
    return FlashPilotSarifLog(
        runs=(
            SarifRun(
                tool=SarifTool(driver=SarifToolComponent(rules=rules)),
                automationDetails=SarifRunAutomationDetails(id=f"flashpilot/{kind}/{framework}"),
                results=tuple(results),
            ),
        )
    )


def build_sarif_log(evidence: CIRunEvidence) -> FlashPilotSarifLog:
    """Build one standards-shaped SARIF run without creating a second verdict."""

    return build_sarif_for_checks(
        kind=evidence.kind,
        framework=evidence.framework,
        checks=evidence.checks,
        source_uri="audit.json" if evidence.kind == "static-audit" else "result.json",
    )


def _render_log(log: FlashPilotSarifLog) -> str:
    document = log.model_dump(
        mode="json",
        by_alias=True,
        exclude_none=True,
    )
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def render_sarif(evidence: CIRunEvidence) -> str:
    return _render_log(build_sarif_log(evidence))


def render_sarif_checks(
    *,
    kind: str,
    framework: str,
    checks: tuple[CICheck, ...],
    source_uri: Literal[
        "audit.json",
        "result.json",
        "comparison.json",
        "policy-evaluation.json",
    ],
) -> str:
    return _render_log(
        build_sarif_for_checks(
            kind=kind,
            framework=framework,
            checks=checks,
            source_uri=source_uri,
        )
    )
