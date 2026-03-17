# ADR 0000: Migration from Legacy VBA Macro to Auditable Desktop Automation

- Status: Accepted
- Date: 2026-03-16
- Deciders: Project maintainers and business stakeholders
- Technical Story: Replace a fragile and outdated VBA-based email attachment workflow with a maintainable desktop application focused on compliance-oriented document extraction, classification, and auditability.

## Context

This project started as a migration initiative.

Before this application existed, the process depended on legacy VBA macro files used to download email attachments from Outlook. That legacy solution had several serious limitations:

- it was outdated and difficult to maintain
- it could freeze the user's laptop for hours during execution
- it provided little or no visible progress feedback
- it was weak from an auditability perspective
- it did not support a reliable compliance-oriented review flow

From a business perspective, this was a significant operational problem. The organization needed a more trustworthy process to download and classify email documents, especially because only signed documents were required for compliance purposes.

The legacy macro approach was no longer adequate for the scale, transparency, and reliability expected from the workflow.

## Decision

We replaced the legacy VBA macro workflow with a Python-based desktop application that:

1. integrates with Outlook in a more maintainable codebase
2. keeps the interface responsive during long-running operations
3. provides visible progress and execution feedback
4. improves auditability through structured outputs and reporting
5. supports document classification focused on signed-versus-unsigned compliance needs

This project is therefore not only a new tool. It is the architectural and operational replacement for a legacy automation process that had become unreliable and insufficient for business controls.

## Problem Statement

The previous VBA-based process created four main categories of problems.

### 1. Operational usability problems

- users could not clearly see whether the process was advancing
- long runs made the machine appear frozen
- poor feedback reduced trust in the automation

### 2. Technical maintenance problems

- VBA macros were harder to extend and modernize
- the solution was not structured for modular growth
- troubleshooting and evolution were constrained by the legacy implementation model

### 3. Audit and control problems

- the old process did not provide a strong audit trail
- it was difficult to explain what had been processed or skipped
- compliance-focused review required stronger traceability

### 4. Business filtering problems

- not every downloaded file had the same business value
- signed documents were the most important output for compliance
- the workflow needed a clearer way to separate relevant from non-relevant documents

## Business Drivers

- reduce operator frustration during long processing windows
- improve reliability and transparency of the document retrieval workflow
- support compliance-oriented handling of signed documentation
- modernize a business-critical automation process
- create outputs that are usable for both operations and review

## Chosen Direction

The replacement solution was designed as a Windows desktop application with explicit support for:

- Outlook-driven attachment extraction
- progress visibility during execution
- document classification after extraction
- audit-friendly artifacts for validation and reporting
- modular code organization that can evolve over time

This direction preserved the practical desktop workflow users needed, while replacing the legacy macro model with a more maintainable and observable architecture.

## Why a Migration Was Necessary

### Option A: Keep the VBA macro and make small fixes

This was rejected because incremental fixes would not solve the root issues:

- poor observability
- poor maintainability
- poor auditability
- weak alignment with the compliance workflow

### Option B: Replace the macro with a modern desktop automation application

This was chosen because it allowed the team to address both technical and business needs at the same time:

- modern code structure
- better execution control
- better user feedback
- stronger audit support
- compliance-oriented document classification

## Consequences

### Positive consequences

- the workflow moved away from a fragile legacy automation model
- users gained progress visibility during long runs
- the system became more maintainable and extensible
- compliance-relevant signed documents became easier to isolate
- the project gained a much stronger audit and reporting story

### Negative consequences

- the migration required a full reimplementation rather than small patches
- the new system introduced a broader architectural footprint
- maintainers now own a larger codebase than a simple macro solution

### Risks to manage

- migration expectations may overpromise parity with every macro behavior
- business users may still compare the new app against historical manual habits
- compliance rules may evolve and require future refinement of classification logic

## Business Logic Rationale

The migration was not only about performance or code quality. It was fundamentally about improving the business process around document retrieval and compliance review.

The critical business insight was:

- the organization did not simply need attachments
- it needed the right attachments
- signed documents had special compliance value
- the process had to be transparent enough to defend in review and follow-up activities

That is why classification and auditability became first-class design concerns in the replacement solution.

## Relationship to Later ADRs

This ADR is foundational because it explains why the later architectural decisions exist.

Specifically, it motivates:

- the layered project architecture
- the use of background workers for long-running tasks
- the audit-oriented design with `EntryID`, Parquet, and Excel outputs
- the focus on signed-versus-unsigned document classification

In other words, the later ADRs describe how the system works, while this ADR explains why the project had to exist in the first place.

## Portfolio Positioning

This ADR is especially valuable for portfolio storytelling because it shows that the project is a modernization effort, not just a greenfield app.

It demonstrates experience with:

- migrating away from a legacy business-critical workflow
- translating operational pain points into architecture decisions
- improving auditability and user trust
- aligning automation outputs with compliance requirements

That makes the project a strong example of applied engineering in a real business setting.

## Related Artifacts

- [docs/adr/0001-project-architecture.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/docs/adr/0001-project-architecture.md)
- [docs/adr/0002-audit-oriented-mail-processing.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/docs/adr/0002-audit-oriented-mail-processing.md)
- [docs/adr/0003-background-workers-for-long-running-operations.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/docs/adr/0003-background-workers-for-long-running-operations.md)
- [README.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/README.md)
