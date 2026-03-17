# ADR 0003: Background Workers for Long-Running Operations

- Status: Accepted
- Date: 2026-03-16
- Deciders: Project maintainers
- Technical Story: Define how long-running extraction and classification tasks are executed without blocking the desktop interface.

## Context

The project performs operations that can take a significant amount of time, including:

- scanning Outlook folders
- evaluating filters across large mail volumes
- extracting many attachments
- classifying files after extraction
- generating audit and reporting artifacts

These activities are not instantaneous, and they can become expensive when mailbox volume is high. In a desktop application, running this work directly on the main UI thread would create several problems:

- the interface would freeze during execution
- progress feedback would become unreliable or invisible
- cancellation and user feedback would feel broken
- the application would appear unstable even when work is still progressing

Because the system is designed for operator-driven execution, responsiveness is part of the product behavior, not just a technical preference.

## Decision

We execute long-running business operations through dedicated background worker classes in `workers/`, while the UI remains focused on interaction and presentation.

The architecture uses:

1. the UI layer to collect parameters and trigger actions
2. worker classes to run long-running processes outside the main UI thread
3. signal-based communication to send progress, completion, and error updates back to the interface
4. the core layer to hold the business logic executed by workers

This means the worker layer is the execution boundary between an interactive PySide6 interface and the underlying automation logic.

## Decision Drivers

- keep the UI responsive during long-running operations
- provide real-time feedback to the operator
- isolate execution concerns from business rules
- reduce the risk of unstable user experience during high-volume runs
- maintain a clear architecture where the GUI does not directly own processing flow

## Architecture Overview

```text
User action in UI
  -> UI collects parameters
  -> Worker starts in background
  -> Worker invokes core processing
  -> Worker emits progress/status/error signals
  -> UI updates progress widgets, logs, and notifications
```

## Why Background Workers Were Chosen

The chosen design fits the operational reality of the application:

- mailbox access can be slow and variable
- file extraction can take time depending on volume and file size
- reporting and audit generation add additional work
- users need to observe progress throughout execution

Workers allow the application to remain interactive while heavy processing continues in the background.

## Separation of Responsibilities

### UI responsibilities

The UI layer should:

- capture user intent
- configure workflow parameters
- display progress and status
- present results and errors

The UI should not implement the actual extraction or classification logic.

### Worker responsibilities

The worker layer should:

- manage background execution
- coordinate the lifecycle of long-running operations
- emit progress and completion events
- translate execution state into signals that the UI can consume

Workers should orchestrate execution, but they should not become the primary home for domain rules.

### Core responsibilities

The core layer should:

- define extraction behavior
- define classification rules
- encapsulate deterministic processing logic

This keeps business decisions portable and reduces coupling to the interface framework.

## Alternatives Considered

### Option A: Run all logic directly in the main UI thread

This was rejected because it would:

- freeze the interface
- damage the operator experience
- make the tool feel unreliable
- tightly couple execution state to widget behavior

### Option B: Put all processing logic inside worker classes

This was rejected because it would:

- blur the line between orchestration and business logic
- make future reuse of domain behavior harder
- increase the risk of large, hard-to-maintain worker classes

### Option C: Build a fully external service or job runner

This was not chosen as the baseline because the current operating model depends on:

- desktop interaction with Outlook on Windows
- operator-led folder selection and monitoring
- a local application experience rather than a distributed service architecture

The current layered design keeps a path open for future extraction of more headless workflows if needed.

## Consequences

### Positive consequences

- the interface stays responsive during long operations
- operators receive continuous progress feedback
- execution concerns are isolated from presentation concerns
- the codebase is easier to reason about than a UI-thread-driven design
- the project demonstrates production-minded desktop automation practices

### Negative consequences

- worker orchestration introduces additional architectural complexity
- signal flow must be designed carefully to avoid fragile UI behavior
- debugging cross-layer execution can be more involved than in a single-threaded script

### Risks to manage

- workers growing into large multi-purpose classes
- business logic being duplicated between workers and core modules
- progress signals becoming inconsistent across different workflows

## Guardrails

To preserve the intent of this decision:

- long-running processes should not execute directly on the main UI thread
- workers should remain orchestration-focused
- core logic should remain outside the UI and outside widget classes
- progress, error, and completion events should be communicated through explicit signals
- UI components should react to worker state rather than manage the processing lifecycle themselves

## Business Rationale

From a business perspective, a frozen interface during a large mailbox run reduces confidence in the system. Users need clear evidence that work is progressing and they need visibility into:

- current stage
- completion progress
- errors
- final outcome

The worker-based model supports that need directly. It turns long-running automation into an observable user-guided workflow instead of an opaque blocking task.

## Portfolio Positioning

This decision supports the project's portfolio value because it demonstrates:

- practical concurrency design in a real desktop application
- separation between orchestration and business logic
- operational thinking for long-running automation
- user-facing observability in data-processing workflows

It helps present the project as a serious automation system designed for reliability and usability, not just as a simple script wrapped in a GUI.

## Related Artifacts

- [docs/adr/0001-project-architecture.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/docs/adr/0001-project-architecture.md)
- [docs/adr/0002-audit-oriented-mail-processing.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/docs/adr/0002-audit-oriented-mail-processing.md)
- [README.md](/c:/Users/User/Documents/VS%20Code/Outlook_AttachExtractor_Rework/README.md)
