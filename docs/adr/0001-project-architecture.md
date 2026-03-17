# ADR 0001: Project Architecture Baseline

- Status: Accepted
- Date: 2026-03-16
- Deciders: Project maintainers
- Technical Story: Establish a clear architectural baseline for Outlook AttachExtractor so future changes can be evaluated against explicit structural and business-oriented design decisions.

## Context

Outlook AttachExtractor is a Windows desktop application that automates the extraction and classification of Outlook email attachments. Although the delivery format is a GUI application, the core business value is data automation:

- identify relevant emails from a business communication system
- apply deterministic filtering rules
- extract and classify document payloads
- generate audit-friendly artifacts for validation and reporting

The project must support long-running workloads, preserve operator visibility during execution, and remain maintainable as both a desktop tool and a portfolio-grade automation system.

The codebase already shows a clear separation between:

- user interface concerns in `ui/`
- business logic in `core/`
- background execution in `workers/`
- support services in `utils/`
- configuration assets in `config/`

This ADR formalizes that architecture as the intended baseline.

## Decision

We adopt a layered desktop automation architecture with five main responsibilities:

1. `ui/` owns presentation and user interaction.
2. `workers/` owns background execution and signal-based coordination.
3. `core/` owns business rules and processing logic.
4. `utils/` owns cross-cutting operational services.
5. `config/` owns runtime configuration and visual theme assets.

The application entry point in `main.py` composes these layers into a desktop workflow optimized for operator-driven execution.

## Architecture Overview

```text
User
  -> UI Layer (PySide6)
  -> Worker Layer (threaded execution + signals)
  -> Core Layer (mail extraction and document classification)
  -> Utility/Support Layer (logging, audit, notifications, power handling)
  -> File Outputs (attachments, Parquet artifacts, Excel reports, logs)
```

### UI Layer

The `ui/` package is responsible for:

- rendering the main window and tabs
- collecting user parameters
- exposing progress and status feedback
- applying the theme system
- providing reusable widgets for common interactions

The UI should remain thin. It can orchestrate workflows, but it should not own extraction or classification logic.

### Worker Layer

The `workers/` package is responsible for:

- executing long-running tasks off the main UI thread
- emitting progress, completion, and error signals
- bridging UI events to core processing logic

This layer exists to keep the application responsive during heavy Outlook and file-processing workloads.

### Core Layer

The `core/` package is responsible for:

- email extraction logic
- document classification logic
- deterministic business rules for processing
- domain behavior that should remain independent from widget implementation

This is the main business logic layer and the most important layer for maintainability and portfolio value.

### Utility Layer

The `utils/` package is responsible for cross-cutting services such as:

- mail auditing
- date handling
- logging
- notifications
- power management

These capabilities support reliability, observability, and operability, but they are intentionally separated from the domain layer.

### Configuration Layer

The `config/` package is responsible for:

- persisted application settings
- theme configuration
- static application assets

This keeps runtime options and presentation assets externalized rather than hardcoded across the codebase.

## Business Logic Rationale

The architecture is intentionally shaped around a business workflow rather than around framework mechanics alone.

### Primary business objective

The system exists to automate repetitive, high-volume email document handling for business users.

### Key business constraints

- operators need a desktop UI because the process is interactive and tied to Outlook on Windows
- extraction can run for a long time, so the UI must remain responsive
- results must be reviewable, not just executed
- missing or skipped emails must be explainable
- generated outputs must be useful both operationally and analytically

### Architectural response to those constraints

- A GUI layer is retained because Outlook-based business workflows are operator-driven.
- Background workers are used because mailbox scanning and file extraction are long-running tasks.
- Business rules are isolated in `core/` so automation behavior can evolve without tightly coupling to the GUI.
- Audit and logging utilities are first-class concerns because trust and traceability matter as much as raw extraction speed.
- Structured outputs such as Parquet and Excel are treated as product artifacts, not incidental by-products.

## Why This Architecture Was Chosen

### Option A: Put logic directly in the UI

This was rejected because it would:

- make the code harder to maintain
- mix presentation and domain logic
- reduce testability
- make future automation reuse more difficult

### Option B: Fully service-oriented or headless-first architecture

This was not chosen as the baseline because the current operating model depends on:

- Windows desktop execution
- Outlook Classic integration
- operator-driven folder selection and monitoring

However, the current separation keeps open the possibility of extracting more headless processing flows later.

### Chosen direction: layered desktop automation

This architecture balances:

- practical desktop usability
- maintainable code separation
- operational resilience
- future portability of business logic

## Consequences

### Positive consequences

- clear separation of concerns across the codebase
- responsive UI during long-running operations
- easier onboarding for future contributors
- stronger alignment with data automation and data engineering narratives
- better traceability through dedicated audit and logging utilities

### Negative consequences

- more modules and coordination boundaries than a small script-style tool
- worker and signal orchestration adds implementation complexity
- some logic may still depend on Windows and Outlook-specific constraints

### Risks to manage

- business logic leaking back into UI widgets over time
- worker classes becoming too orchestration-heavy
- utility modules accumulating domain logic that belongs in `core/`

## Boundaries and Guardrails

To preserve this architecture over time:

- UI modules should not implement extraction or classification rules directly.
- Worker modules should orchestrate execution, not redefine business rules.
- Core modules should avoid depending on widget internals.
- Utility modules should remain support-oriented and not become a second business layer.
- Configuration should stay externalized where practical.

## Portfolio Positioning

This architecture supports presenting the project as a data engineering and automation portfolio piece because it shows:

- ingestion from an operational business system
- deterministic processing logic
- traceable intermediate artifacts
- analytical output generation
- operational reliability patterns in a real user-facing workflow

The project is therefore best described as a desktop-delivered data automation system with data engineering characteristics.

## Related Artifacts

- [README.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/README.md)
- [.tinker/treemap.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/.tinker/treemap.md)
- [.tinker/dependencies_report.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/.tinker/dependencies_report.md)
