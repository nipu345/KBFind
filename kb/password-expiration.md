---
title: Credential Rotation Policy and Expired Password Reset
tags: [accounts, identity]
---
## Symptoms
- User receives a message that their password has expired or must be changed.
- Sign-in worked yesterday but fails today on every service.
- User forgot their password and cannot answer the recovery questions.

## Cause
Passwords expire every 365 days under the credential rotation policy. Users who ignore the reminder emails are forced to reset at next sign-in.

## Resolution
1. Direct the user to the self-service password reset page. It requires a verified recovery email or phone number.
2. If no recovery method is on file, verify identity and issue a temporary password that must be changed at first sign-in.
3. New passwords must be at least 12 characters and cannot match the last 5 passwords.
4. Remind the user to update the saved password on phones and laptops to avoid a lockout (see Account Lockout Remediation).
