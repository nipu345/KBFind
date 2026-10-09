---
title: Remote Access VPN Client Connectivity Failures
tags: [network, remote]
---
## Symptoms
- User working from home cannot reach internal websites, file shares, or licensed research databases.
- VPN client shows "connecting" indefinitely, or connects but pages still do not load.

## Cause
Usually one of: outdated VPN client, the home network blocking the VPN port, a DNS setting on the device overriding internal names, or the user connected to the wrong VPN profile.

## Resolution
1. Confirm the client is the current supported version; reinstall from the software portal if not.
2. Check the user selected the general access profile, not a department-specific one.
3. Have the user try a different network (phone hotspot) to rule out the home router.
4. Flush DNS (`ipconfig /flushdns` on Windows, `sudo dscacheutil -flushcache` on macOS) and reconnect.
5. Collect the client log file and escalate to network operations if none of the above works.
