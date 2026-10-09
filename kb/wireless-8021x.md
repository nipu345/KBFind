---
title: 802.1X Wireless Profile Configuration
tags: [network, wireless]
---
## Symptoms
- Laptop or phone will not connect to the secure campus wireless network.
- Device keeps prompting for a username and password in a loop.
- A certificate warning appears when trying to join.

## Cause
The secure network uses 802.1X (WPA2/WPA3-Enterprise). A stale saved profile, wrong identity format, or an untrusted server certificate blocks authentication.

## Resolution
1. Forget the network on the device.
2. Rejoin and sign in with the full identity, including the domain (user@example.edu), not just the username.
3. When shown the server certificate, confirm the common name matches the published RADIUS server name before trusting it.
4. On Windows, set EAP method to PEAP and inner authentication to MSCHAPv2 if the profile was created manually.
5. If it still fails, check the account is not locked and has not had a recent password change.
