---
title: Network File Share Access Denied
tags: [storage, accounts]
---
## Symptoms
- A user gets "access denied" or "you do not have permission" when opening a department shared drive.
- The mapped drive letter is missing, or shows a red X.
- A new team member can see the folder but not open it.

## Cause
Shared drives are secured by group membership. A new employee may not have been added to the right group, or group changes have not reached the computer because the user has not signed out since the change. Off campus, shared drives are only reachable through the VPN.

## Resolution
1. Confirm the full folder path the user is trying to reach.
2. Check the folder's access group and confirm the user is a member. Request approval from the folder owner if not.
3. After any group change, have the user sign out and back in, or restart the computer.
4. If working remotely, connect to the VPN before opening the drive.
5. Re-map the drive using the full server path if the drive letter is missing.
