---
title: ActiveSync Mailbox Configuration on Mobile Devices
tags: [email, mobile]
---
## Symptoms
- Email, calendar, or contacts do not show up on the user's phone.
- Phone mail app says "cannot get mail" or "account verification failed."
- Calendar invites accepted on the computer are missing from the phone.

## Cause
The phone is using a legacy protocol, an outdated saved password, or has not accepted the required device security policy (screen lock).

## Resolution
1. Remove the account from the phone.
2. Install the organization's supported mail app, or add the account as a Microsoft Exchange account in the built-in mail app. Do not use IMAP.
3. Sign in with the full email address and complete the MFA prompt.
4. Accept the device policy prompt; the phone must have a passcode set.
5. Enable mail, calendar, and contacts sync in the account settings.
