---
title: macOS Privacy Permissions for Screen Sharing, Camera, and Microphone
tags: [desktop, software, audio]
---
## Symptoms
- On a Mac, the user can join a video meeting but others see a black screen when they try to share their screen.
- The camera or microphone does not work in one application but works in others.
- The application never asked for permission, or the user clicked "Don't Allow."

## Cause
macOS requires each application to be given permission for screen recording, camera, and microphone access. If permission was denied once, the application cannot ask again, and screen sharing stays blank until the permission is turned on manually.

## Resolution
1. Open System Settings, then Privacy & Security.
2. Under Screen & System Audio Recording, turn on the conferencing application.
3. Under Camera and Microphone, turn on the same application.
4. Fully quit the application with Cmd+Q and reopen it. Screen sharing changes do not take effect until it restarts.
5. If the application does not appear in the list, start a screen share once so macOS adds it, then repeat the steps above.
