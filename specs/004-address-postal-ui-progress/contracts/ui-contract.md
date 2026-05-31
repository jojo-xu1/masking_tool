# UI Contract

## Purpose

The desktop UI must make masking runs understandable while they are running and after they finish.

## Inputs

- File or folder selection
- Single-file language selection when file mode is used
- Detection-source toggles, including person, phone, address, and postal-code detection
- Run command

## Running State

When a run starts:

- progress becomes visible within 1 second for folder processing
- the run command is disabled or otherwise guarded against duplicate starts
- the UI indicates that processing is active
- current progress is based on completed files out of total discovered files

## Progress Fields

The UI progress state exposes:

```text
total_targets
completed_targets
processed_count
skipped_count
failed_count
current_target
is_running
```

## Completion Summary

When a run finishes, the UI must show:

- output location
- processed count
- skipped count
- failed count
- failure reasons when available

## Error And Partial Failure Behavior

- A failed file must not hide successful file results.
- Partial failures must be visible in the final summary.
- The UI must return to a state where the user can start another run after completion or failure.

## Accessibility And Readability

- File/folder selection, language selection, and detection toggles must remain easy to scan.
- Progress and completion messages must not rely on color alone.
