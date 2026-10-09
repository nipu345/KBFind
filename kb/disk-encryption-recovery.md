---
title: Full-Disk Encryption Recovery Key Retrieval
tags: [security, desktop, hardware]
---
## Symptoms
- On startup, a blue screen asks for a long numeric recovery key before the computer will boot.
- Often appears right after a firmware/BIOS update, a hardware repair, or a docking station change.

## Cause
The encryption system detected a change in the boot environment and requires the recovery key to prove the drive has not been tampered with.

## Resolution
1. Note the recovery key ID shown on the screen (the first 8 characters are enough).
2. Verify the user's identity and confirm they are the assigned user of the device.
3. Look up the key by ID in the device management console. Read it to the user; do not email or text it.
4. After the device boots, have the user restart once more to confirm the prompt does not return.
5. If the prompt repeats on every boot, suspend and resume protection from the encryption control panel, then escalate if it continues.
