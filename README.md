# Outlook AttachExtractor

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.0+-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Version](https://img.shields.io/badge/Version-3.0.0-orange.svg)](https://github.com/Merlin2098/Outlook_AttachExtractor_Rework)

Desktop automation project for Microsoft Outlook focused on high-volume attachment extraction, file classification, and auditable mail processing.

This repository is especially relevant as a **data engineering portfolio project** because it combines:

- data ingestion from a business system
- filtering and transformation logic
- file-based outputs for downstream use
- audit datasets in Parquet
- Excel reporting for business users
- operational safeguards for long-running jobs

Even though the delivery format is a desktop application, the core value of the project is **data automation and reproducible processing at scale**.

## Portfolio Framing

This project can be presented as a practical example of applied data engineering in an enterprise desktop context.

### Why it fits a data engineering portfolio

- It extracts structured information from an operational source system: Outlook mailboxes.
- It materializes intermediate and final artifacts in analytics-friendly formats such as Parquet and Excel.
- It uses audit-oriented processing with unique mail identifiers to improve traceability and reduce skipped records.
- It separates UI, business logic, and worker execution, which keeps the processing layer maintainable.
- It handles long-running workloads with progress reporting, logging, and system-level protections.

### Business problem solved

Many teams still receive critical business documents by email. This project automates the repetitive workflow of:

1. finding relevant emails
2. identifying candidate messages by date and subject filters
3. extracting attachments
4. classifying documents by signature status
5. generating audit outputs for validation and follow-up

That makes it a useful bridge between classic desktop operations and data pipeline thinking.

## Key Features

### High-volume attachment extraction

- Audit workflow based on Outlook `EntryID` values for more reliable mail tracking
- Subject filtering with three modes:
  - all phrases must match
  - any phrase can match
  - no phrase filtering
- Date range detection based on available mailbox contents
- Duplicate handling during extraction
- Excel output with mail metadata and processing status
- Parquet-based mail mapping for audit and debugging workflows

### Document classification

- Automatic routing of files according to digital signature status
- Detection patterns such as `firmado`, `signed`, `sin_firmar`, and `not_signed`
- Real-time process metrics
- Safe duplicate handling with optional subfolder organization

### User experience and operations

- Modular PySide6 interface built from reusable widgets
- Persistent light/dark theming through JSON configuration
- Detailed progress tracking by processing phase
- Real-time logs with visual cues
- Visual and audio completion notifications
- Outlook folder explorer for mailbox selection
- Splash screen and lazy loading for faster startup experience

### Reliability for long jobs

- Power management protection to prevent machine sleep during execution
- Dual logging strategy for session logs and error logs
- Automatic cleanup of historical logs
- Safer batch handling for large mailbox workloads

## What Makes This Interesting Technically

The project is more than a GUI utility. It includes several patterns that map well to data engineering and data operations work:

- **Source system integration:** Outlook is used as the operational input source.
- **Deterministic filtering:** Emails are filtered using explicit criteria and unique identifiers.
- **Intermediate data products:** Mail inventories are persisted for inspection and replay-like analysis.
- **Analytical artifacts:** Parquet and Excel outputs support both technical and business audiences.
- **Operational observability:** Logging, progress, and audit reports improve trust in long-running automation.
- **Separation of concerns:** UI, workers, and business logic are split into distinct layers.

## Architecture

The application follows a 3-layer structure:

```text
UI (PySide6)
  -> user interaction, widgets, themes, progress display

Workers (Qt threading/signals)
  -> background execution, progress emission, task orchestration

Core
  -> extraction rules, classification logic, processing behavior
```

### Main directories

```text
Outlook_AttachExtractor_Rework/
|-- config/      # App configuration and theme assets
|-- core/        # Business logic
|-- ui/          # Main window, tabs, reusable widgets
|-- utils/       # Logging, audit, dates, notifications, power handling
|-- workers/     # Background workers and Qt signal flow
|-- main.py      # Application entry point
```

### Layer responsibilities

- `core/`: attachment extraction and document classification logic
- `workers/`: threaded execution wrappers around long-running operations
- `ui/`: interface composition, tab structure, reusable widgets, and themes
- `utils/`: support modules such as mail auditing, date handling, and logging

## Audit Workflow with Entry IDs

One of the strongest technical aspects of the project is the audit-oriented workflow:

1. The mailbox is mapped using unique Outlook `EntryID` values.
2. Mail metadata is persisted to Parquet.
3. Filters are applied against the stored inventory.
4. Only eligible messages are processed for attachment extraction.
5. Excel reports summarize processed and skipped items with reasons.

### Why this matters

- Reduces the risk of silently missing emails during large runs
- Improves reproducibility and troubleshooting
- Produces a reviewable data artifact for validation
- Makes the workflow easier to explain in portfolio and interview settings

## Technology Stack

- Python 3.13+
- PySide6
- pywin32
- Polars
- Parquet
- OpenPyXL / XlsxWriter
- PyInstaller

## Requirements

- Windows 10 or Windows 11
- Python 3.13+
- Microsoft Outlook Classic installed and configured
- Local Outlook cache available for the mailbox being processed
- Administrator permissions recommended for long-running jobs

## Installation

### From source

```bash
git clone https://github.com/Merlin2098/Outlook_AttachExtractor_Rework.git
cd Outlook_AttachExtractor_Rework
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### From executable build

1. Download the package from the Releases page.
2. Extract the full `OutlookExtractor/` folder.
3. Run `OutlookExtractor.exe`.
4. Distribute the full folder, not only the executable.

## Usage

### Attachment extraction flow

1. Open the attachment download tab.
2. Select the Outlook folder to scan.
3. Configure phrase filters and matching mode.
4. Set the processing date range.
5. Choose the destination folder.
6. Start the extraction process.
7. Review the saved attachments, Excel report, and audit artifacts.

### Document classification flow

1. Open the document classification tab.
2. Select the source folder.
3. Select the destination folder.
4. Start classification.
5. Review the generated signed and unsigned output folders.

### Phrase search modes

| Mode | Behavior |
| --- | --- |
| Full match | The subject must contain all phrases |
| Partial match | The subject must contain at least one phrase |
| No filter | All emails in the date range are processed |

## Configuration

### `config/config.json`

```json
{
  "tema": "claro",
  "ui": {
    "window_size": [1200, 700]
  }
}
```

Main settings:

- `tema`: last selected theme
- `window_size`: saved application window dimensions

### Theme files

The files `theme_light.json` and `theme_dark.json` define the color palette used by the application UI.

## Logging

The application uses a dual logging model:

- session logs: `session_YYYYMMDD_HHMMSS.log`
- error logs: `errors_YYYYMMDD_HHMMSS.log`

Automatic behavior:

- retains up to 50 files per log type
- removes log files older than 30 days
- stores logs under the application `logs/` directory

## Building the Executable

To generate a distributable one-folder executable with PyInstaller:

```bash
venv\Scripts\activate
python generar_onedir.py
```

Output:

- build result is created under `dist/OutlookExtractor/`
- distribute the complete folder

### PySide6 and COM note

The file `runtime_hook_com.py` is important for:

- COM initialization inside the packaged application
- Outlook interoperability
- safer threaded behavior in bundled execution

## Known Limitations

- Works only with **Outlook Classic**
- Not compatible with **New Outlook**
- Processes only emails available in the local Outlook cache
- Designed specifically for Windows environments
- Very large mailboxes may still require operator monitoring

## Troubleshooting

### Cannot connect to Outlook

Possible causes:

- Outlook is not installed or configured
- New Outlook is being used instead of Outlook Classic
- insufficient permissions

Suggested actions:

1. Confirm Outlook Classic is installed.
2. Run the application as administrator.
3. Confirm at least one Outlook account is configured.

### No emails found in the selected date range

Suggested checks:

1. Verify the available mailbox date range shown in logs.
2. Review phrase filters.
3. Try the no-filter mode to isolate filter issues.
4. Inspect the audit Parquet output for debugging.

### Long process stops after thousands of emails

Likely cause:

- COM object accumulation during very large runs

Suggested actions:

1. Review the error logs.
2. Split processing into smaller date windows.
3. Use the audit outputs to identify failure boundaries.

## Future Improvements

Potential directions that would strengthen the project even more as a portfolio piece:

- automated test suite expansion
- benchmark and profiling reports
- richer analytical dashboards from audit outputs
- stronger data quality validation rules
- export to additional structured targets
- broader mailbox source support

## Contribution

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit with clear messages.
4. Push the branch.
5. Open a pull request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Author

**Richi**  
[GitHub](https://github.com/Merlin2098)

Last major update: January 2025  
Current version: 3.0.0
