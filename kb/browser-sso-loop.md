---
title: Single Sign-On Redirect Loops and Browser Session Corruption
tags: [accounts, identity, browser]
---
## Symptoms
- After entering a password, the browser keeps bouncing between the sign-in page and the website.
- The user signs in successfully but lands on a blank page or an "access denied" message for a site they normally use.
- The problem goes away in a private or incognito window.

## Cause
Stale or conflicting session cookies from an earlier sign-in, often with a different account, confuse the single sign-on service. Browser extensions that block cookies or trackers can cause the same loop.

## Resolution
1. Test in a private window. If it works there, the problem is cached browser data.
2. Clear cookies and cached data for the campus sign-in domain and the affected site, then fully close and reopen the browser.
3. If the user has multiple campus accounts (for example, student and employee), sign out of all of them first.
4. Temporarily disable privacy or ad-blocking extensions and retry.
5. If the loop happens in every browser and device, collect the time of the attempt and the site address and escalate to the identity team.
