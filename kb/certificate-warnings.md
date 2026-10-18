---
title: Browser Certificate Warnings on Internal Websites
tags: [security, network, browser]
---
## Symptoms
- The browser shows "Your connection is not private" or a certificate error when opening a campus website.
- Some users see the warning and others do not.

## Cause
Certificate warnings usually come from the device clock being wrong, an outdated browser or operating system missing current root certificates, or security software inspecting web traffic. Occasionally the website's certificate has actually expired.

## Resolution
1. Check that the device's date, time, and time zone are correct and set automatically.
2. Update the browser and operating system.
3. Try another browser or device. If every device shows the error, the site's certificate is likely expired; report the exact address to the web services team.
4. Tell users never to click past a certificate warning on a sign-in page, since it can indicate a fake site.
5. If only one network shows the error, the user may be on a hotel or café network that intercepts traffic; have them use the VPN or a hotspot.
