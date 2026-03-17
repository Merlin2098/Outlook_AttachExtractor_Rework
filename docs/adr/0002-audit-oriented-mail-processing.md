# ADR 0002: Audit-Oriented Mail Processing with EntryID and Parquet

- Status: Accepted
- Date: 2026-03-16
- Deciders: Project maintainers
- Technical Story: Define how the system tracks email processing reliably and produces artifacts that support validation, troubleshooting, and business review.

## Context

The project processes large volumes of Outlook emails in order to extract attachments and generate business outputs. In this type of workflow, one of the main risks is losing trust in the process because:

- emails may be skipped without clear explanation
- large mailbox scans can be difficult to validate manually
- operators need evidence of what was processed and why
- technical debugging requires an inspectable representation of the mail inventory

A simple scan-and-download approach would produce final files, but it would not provide strong traceability. For business workflows, that is not sufficient.

The project therefore needs an audit-oriented processing model that:

- identifies emails uniquely
- preserves a structured inventory of candidate records
- supports deterministic filtering before extraction
- produces outputs that can be reviewed by both technical and non-technical users

## Decision

We use an audit-first mail processing strategy based on:

1. unique Outlook `EntryID` values as the primary email identifier
2. a persisted mail inventory in Parquet format
3. downstream filtering and extraction based on that structured inventory
4. Excel reporting for business-facing review of processed and skipped records

This means the system does not treat attachment extraction as a blind one-step action. Instead, it treats the mailbox as a data source that is first mapped, then filtered, then processed, then reported.

## Decision Drivers

- reliability during high-volume mailbox processing
- explainability of processed versus skipped emails
- reproducibility of selection logic
- technical troubleshooting through structured artifacts
- business visibility through familiar report formats

## Workflow

```text
Outlook mailbox
  -> mail inventory using EntryID
  -> persisted audit dataset in Parquet
  -> filtering and eligibility decisions
  -> attachment extraction
  -> Excel audit/report output
```

## Why EntryID Was Chosen

`EntryID` is used as the canonical mail identifier because it is better suited than weaker identifiers such as subject lines or date-only references.

This supports:

- more precise tracking of individual messages
- lower risk of ambiguous matching
- more reliable reconciliation between inventory and extraction results

For the purposes of this project, the important architectural principle is that email processing must be anchored to a stable message identity whenever possible.

## Why Parquet Was Chosen for the Audit Dataset

Parquet was chosen as the persisted audit format because it fits the project’s portfolio and operational goals well:

- it is structured and analytics-friendly
- it supports downstream inspection and debugging workflows
- it aligns with data engineering conventions better than ad hoc flat text logging
- it makes the project easier to present as a data automation system rather than only a desktop utility

Parquet is not only a storage choice. It is also part of the project’s architectural positioning as a system that creates reusable data artifacts.

## Why Excel Was Also Chosen

Excel is retained as a complementary output because business users and operators often need a familiar review surface.

Excel supports:

- validation by non-technical stakeholders
- easier handoff and follow-up workflows
- fast review of processed and omitted records

The architectural principle is that the project should serve both:

- engineering-friendly artifacts for traceability
- business-friendly artifacts for operational review

## Alternatives Considered

### Option A: Direct extraction without persisted audit inventory

This was rejected because it would:

- reduce traceability
- make skipped records harder to explain
- weaken confidence in large runs
- make debugging more dependent on transient logs

### Option B: Log-only audit trail

This was rejected because logs alone are not enough for structured analysis:

- they are harder to query systematically
- they are less suitable for tabular review
- they do not represent the mailbox inventory as a reusable dataset

### Option C: Excel-only reporting

This was rejected as the sole audit strategy because Excel is good for business review but weaker than Parquet for:

- technical inspection
- structured downstream analysis
- data engineering alignment

## Consequences

### Positive consequences

- improved confidence in high-volume processing
- stronger ability to explain what happened during a run
- better technical debugging through persisted intermediate data
- better business review through spreadsheet outputs
- stronger portfolio narrative around auditability and data engineering practices

### Negative consequences

- more storage used per run because intermediate artifacts are preserved
- more workflow steps than a simple extraction-only tool
- additional implementation complexity in dataset generation and reporting

### Risks to manage

- audit artifacts becoming inconsistent with final extracted outputs
- schema drift in audit datasets over time
- operators treating Excel as the only source of truth instead of understanding the full audit chain

## Guardrails

To preserve the intent of this decision:

- processed emails should remain tied to a unique message identity
- audit artifacts should be generated consistently as part of extraction workflows
- structured audit outputs should not be replaced by logs alone
- business-facing reports should remain aligned with the underlying structured audit data

## Business Rationale

This decision is not only technical. It reflects an operational need for trust.

In enterprise email-based workflows, users care about more than whether files were downloaded. They also need to know:

- which emails were considered
- which were selected
- which were skipped
- why a record did or did not lead to an extracted document

That is why auditability is treated as part of the product behavior, not as an optional afterthought.

## Portfolio Positioning

This ADR strengthens the project’s positioning as a data engineering and automation portfolio piece because it demonstrates:

- source-system record identification
- intermediate dataset materialization
- traceable filtering logic
- dual-output design for technical and business consumers

This is a strong example of designing automation for observability and trust, not just throughput.

## Related Artifacts

- [docs/adr/0001-project-architecture.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/docs/adr/0001-project-architecture.md)
- [README.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/README.md)
- [.tinker/dependencies_report.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/.tinker/dependencies_report.md)
