---
title: Suspicious Message Reporting and Credential Compromise Response
tags: [security, email, accounts]
---
## Symptoms
- User received a suspicious email asking them to sign in, pay an invoice, or buy gift cards.
- User clicked a link and entered their username and password on a page that looked wrong.
- Contacts report receiving strange emails "from" the user.

## Cause
Phishing campaign. If credentials were entered, assume the account is compromised.

## Resolution
1. If the user only received the message: have them use the "Report phishing" button, then delete it.
2. If credentials were entered: reset the password immediately and sign the account out of all sessions.
3. Review MFA registrations and remove any device the user does not recognize.
4. Check mailbox rules for forwarding or auto-delete rules the attacker may have created.
5. Open a security incident ticket with the time of the click and the sender address.
