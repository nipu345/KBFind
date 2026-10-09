---
title: MFA Device Re-enrollment After Handset Replacement
tags: [accounts, security, mobile]
---
## Symptoms
- User got a new or replacement phone and no longer receives push approvals.
- The authenticator app on the new phone is empty, or codes are rejected.
- User is stuck at the "approve sign-in request" screen.

## Cause
Multi-factor authentication is bound to the original device. Moving to a new phone does not transfer the registration unless the user migrated it beforehand.

## Resolution
1. Verify identity in person with a photo ID, or through the approved remote verification process. Never reset MFA based on an email request alone.
2. Remove the old device registration from the user's MFA profile.
3. Issue a one-time bypass code valid for 15 minutes.
4. Walk the user through enrolling the new phone: install the authenticator app, scan the QR code, approve a test push.
5. Recommend adding a second method (backup phone number or hardware key) so this does not happen again.
