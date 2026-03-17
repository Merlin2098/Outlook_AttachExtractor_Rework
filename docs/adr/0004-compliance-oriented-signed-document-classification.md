# ADR 0004: Compliance-Oriented Signed Document Classification

- Status: Accepted
- Date: 2026-03-16
- Deciders: Project maintainers and business stakeholders
- Technical Story: Define why the system classifies extracted documents by signature status and why that behavior is central to HR compliance workflows.

## Context

The project does not exist only to download attachments from Outlook. Its business value is closely tied to compliance-oriented document handling.

In the HR context, documentation procedures need to be controlled and traceable. The organization must be able to:

- identify the documents that were received
- separate compliant from non-compliant documentation states
- follow up on missing or incomplete records
- support internal control processes
- align document handling with Peruvian legal and administrative requirements

For this reason, not all extracted files have the same business value. Signed documents are especially important because they are the records most directly associated with compliance evidence and HR documentation completeness.

The system therefore needs a clear and explicit mechanism to distinguish signed documents from unsigned ones after extraction.

## Decision

We classify extracted documents according to signature-related status as a first-class business workflow.

The system separates documents into compliance-relevant categories such as:

- signed
- unsigned

This classification is based on explicit naming and detection patterns such as:

- `firmado`
- `signed`
- `sin_firmar`
- `not_signed`

The output structure is designed so users can quickly identify which files are ready for compliance handling and which files require follow-up or validation.

## Decision Drivers

- support HR compliance workflows
- prioritize signed documents as higher-value compliance artifacts
- reduce manual effort in post-download sorting
- make document status visible immediately after extraction
- improve control over documentation procedures
- support alignment with Peruvian legal and operational requirements

## Business Rationale

This decision is fundamentally business-driven.

The organization needs more than bulk attachment retrieval. It needs a workflow that helps HR and operational teams maintain control over documentation procedures.

Signed documents matter because they help answer practical compliance questions such as:

- which required records are already complete
- which records still need signature follow-up
- which documents can be considered ready for downstream review or filing

Without classification, users would still need to manually review large numbers of extracted files, which would reduce much of the value of the automation.

## Why Classification Is a First-Class Concern

The project treats classification as part of the main workflow, not as an optional post-processing step, because:

- compliance value depends on document state, not just on file presence
- HR teams need fast visibility into documentation completeness
- follow-up actions depend on whether documents are signed or unsigned
- the automation should reduce operational ambiguity, not just move files around

This means extraction alone is not considered sufficient for the business problem.

## Architecture Implications

This decision influences the architecture in several ways:

- the `core/` layer must include explicit classification rules
- the `workers/` layer must support classification as a long-running process when needed
- the output folder structure must reflect business-relevant document states
- audit and reporting flows should remain compatible with classification outcomes

The classification capability is therefore both a business feature and an architectural responsibility.

## Alternatives Considered

### Option A: Download all files without classification

This was rejected because it would:

- leave too much manual work after extraction
- weaken the compliance value of the system
- make it harder to monitor documentation completeness
- reduce the practical usefulness of the output for HR teams

### Option B: Leave classification entirely to manual review

This was rejected because manual review does not scale well and introduces:

- more time spent sorting files
- more inconsistency between operators
- more risk of delayed compliance follow-up

### Option C: Treat classification as a secondary or optional feature

This was rejected because classification is part of the core business purpose of the application, not a peripheral enhancement.

## Consequences

### Positive consequences

- signed compliance documents are easier to isolate and track
- HR users can review documentation state faster
- follow-up on missing signatures becomes more actionable
- the project aligns more closely with business and legal control needs
- the automation solves a more complete workflow than simple extraction alone

### Negative consequences

- classification rules may need ongoing refinement as naming patterns evolve
- false positives or false negatives are possible if document naming is inconsistent
- the system must maintain clear expectations about what classification means

### Risks to manage

- business users may assume classification is legally definitive in every edge case
- naming conventions may vary across teams or document sources
- regulatory or procedural changes may require future updates to detection logic

## Guardrails

To preserve the intent of this decision:

- classification logic should remain explicit and understandable
- the system should distinguish automated categorization from formal legal judgment
- signed-versus-unsigned outputs should be easy for users to interpret
- future changes to classification rules should be evaluated against HR compliance needs

## Peruvian HR Compliance Perspective

This project supports HR documentation control in a Peruvian business context by making it easier to:

- track required supporting documentation
- identify documents pending completion
- maintain more orderly evidence for internal procedures
- support compliance follow-up aligned with Peruvian labor and administrative obligations

This ADR does not claim that the application itself determines legal compliance automatically. Instead, it documents that the software is intentionally designed to support compliance-oriented operational control.

## Portfolio Positioning

This ADR strengthens the project's portfolio value because it shows the ability to connect software behavior to a real business rule:

- not all files matter equally
- document status changes business risk
- automation should reflect compliance priorities

That makes the project a stronger example of business-aware engineering rather than generic file processing.

## Related Artifacts

- [docs/adr/0000-project-migration-from-vba-macro.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/docs/adr/0000-project-migration-from-vba-macro.md)
- [docs/adr/0001-project-architecture.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/docs/adr/0001-project-architecture.md)
- [docs/adr/0002-audit-oriented-mail-processing.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/docs/adr/0002-audit-oriented-mail-processing.md)
- [README.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/README.md)
