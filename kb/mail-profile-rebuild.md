---
title: Mail Client Profile Corruption and Rebuild
tags: [email, desktop]
---
## Symptoms
- Desktop email client crashes on launch or hangs at "loading profile."
- Client repeatedly asks for the password even after it is entered correctly.
- New messages appear in webmail but never arrive in the desktop app.

## Cause
The local mail profile or its offline cache file has become corrupted, often after an interrupted update or a full disk.

## Resolution
1. Confirm mail works in the web client. If it does not, the problem is the account, not the profile.
2. Close the mail client completely.
3. Create a new mail profile from the system mail settings and set it as the default.
4. Sign in and let the mailbox re-sync. Large mailboxes can take an hour.
5. Once the new profile works, delete the old profile and its cache file to free disk space.
