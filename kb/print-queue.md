---
title: Print Queue Mapping and Stuck Job Clearing
tags: [printing, hardware]
---
## Symptoms
- User sends a document to print and nothing comes out.
- The job sits in the queue as "pending" or "error" and blocks everything behind it.
- The printer does not appear in the list of available printers at all.

## Cause
Jobs get stuck when the spooler hangs or a driver mismatch occurs. Missing printers are usually a mapping problem: the device is not connected to the managed print server.

## Resolution
1. Open the print queue and cancel all pending jobs.
2. On Windows, restart the Print Spooler service; on macOS, reset the printing system only as a last resort.
3. Re-add the printer from the managed print server rather than by IP address so the correct driver installs.
4. Confirm the user has print quota remaining in the print release portal.
5. If the release station shows the job but the printer does not print, check for paper jams or toner errors on the device panel and log a hardware ticket.
