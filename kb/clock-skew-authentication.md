---
title: System Clock Drift Causing Authentication Failures
tags: [accounts, desktop, identity]
---
## Symptoms
- A user gets sign-in errors on one specific computer even though the password works everywhere else.
- MFA codes from an authenticator app are rejected as invalid.
- Errors mention a time difference, an expired token, or a failure to contact the domain.

## Cause
Sign-in systems and one-time codes depend on the device clock being accurate to within a few minutes. A dead motherboard battery, a disabled time service, or a manually set time zone lets the clock drift.

## Resolution
1. Compare the device clock with an accurate time source.
2. Turn on automatic date and time and set the correct time zone.
3. On Windows, run `w32tm /resync` from an administrator prompt. On macOS, toggle "Set time and date automatically" off and on.
4. For authenticator app code errors, enable automatic time on the phone as well.
5. If the clock resets every time the computer is powered off, the motherboard battery likely needs replacing; log a hardware ticket.
