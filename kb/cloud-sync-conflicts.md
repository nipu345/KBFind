---
title: Cloud Storage Sync Conflict Resolution
tags: [storage, desktop]
---
## Symptoms
- Duplicate files appear with the computer's name added to the filename.
- Files show a red X or "sync pending" icon and never finish uploading.
- A user's changes seem to disappear or revert to an older version.

## Cause
Two copies of the file were edited at the same time (for example, offline on a laptop and online in a browser), or the filename contains characters or a path length the service does not allow.

## Resolution
1. Open both copies and have the user decide which to keep; merge edits manually if needed.
2. Rename files that contain unsupported characters (`" * : < > ? / \ |`) or have very long paths.
3. Use the service's version history to restore content that was overwritten.
4. Pause and resume sync, then check the sync client's activity panel for remaining errors.
5. Recommend editing shared documents in the browser to avoid future conflicts.
