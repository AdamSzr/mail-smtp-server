# Mail SMTP / IMAP Sandbox

This repository contains a small set of Python experiments for handling mail protocols and proxying mail flows. It is primarily a local learning/prototype environment for SMTP and IMAP behavior, authentication, mailbox responses, and message relaying.

The project is not a production-ready mail server. It focuses on protocol simulation and experimentation with SMTP AUTH, IMAP command responses, and storing or relaying messages locally.

## What this project does

- runs an SMTP listener that accepts authenticated mail submissions
- supports basic SMTP AUTH flows (PLAIN / LOGIN style handling in the demo code)
- simulates IMAP server responses for mailbox discovery and fetch commands
- includes a proxy-style IMAP server that forwards traffic to a real backend provider
- can persist incoming mail to a local folder for debugging / local testing
- can relay mail to MX hosts using DNS lookup and SMTP

## Repository layout

- `smtp-server.py` — custom SMTP server implementation built on Python's `smtpd`
- `my-smtp-impl.py` — `aiosmtpd`-based SMTP server with auth enforcement
- `my-smtp-local-drive-message-handler.py` — stores received messages in the `mails/` directory
- `my_smtp_relay_handler.py` — relays a message to the recipient domain's MX server
- `my-imap-server.py` — IMAP server that responds with mock mailbox data
- `my-imap-proxy-server.py` — proxy that relays IMAP traffic to a real IMAP backend
- `my_imap_server_class.py` — IMAP command handlers and canned responses
- `logger.py` — lightweight logger wrapper
- `my_utils.py` — helper methods for time and credential decoding
- `mails/` — sample `.eml` files and helper mail registry

## Protocol references

- SMTP: https://www.rfc-editor.org/rfc/rfc5321
- IMAP: https://www.rfc-editor.org/rfc/rfc3501
- AUTH PLAIN / SMTP AUTH behavior: RFC 4954

## Prerequisites

Python 3.10+ is recommended.

Install the dependencies used by the SMTP pieces:

```bash
python3 -m pip install aiosmtpd dnspython
```

The IMAP proxy examples may also rely on the standard library only, but some examples use `imaplib` and `asyncio`.

## Running the SMTP examples

### 1) Basic custom SMTP server

```bash
python3 smtp-server.py
```

This script starts a simple SMTP listener and then waits for Enter before shutting down.

### 2) aiosmtpd version

```bash
python3 my-smtp-impl.py
```

This version uses `aiosmtpd` and enforces SMTP authentication.

### 3) Local message storage handler

```bash
python3 my-smtp-local-drive-message-handler.py
```

This is a storage-oriented handler intended to save incoming messages under the `mails/` or `emails/` area.

### 4) Relay handler

```bash
python3 my_smtp_relay_handler.py
```

This file acts as a relaying helper, not a full standalone daemon.

## Running the IMAP examples

### Mock IMAP server

```bash
python3 my-imap-server.py
```

This starts a local IMAP server that emits canned responses for commands such as `CAPABILITY`, `LIST`, `SELECT`, and `UID FETCH`.

### IMAP proxy

```bash
python3 my-imap-proxy-server.py
```

This acts as a pass-through proxy between an IMAP client and a real backend email provider.

## Typical flow

1. Start an SMTP listener.
2. Connect with an SMTP client or mail library.
3. Authenticate using the example credentials defined in the code.
4. Submit a message.
5. Inspect the message in the local storage folder or relay it out via MX.
6. Use the IMAP examples to simulate mailbox behavior or test client compatibility.

## Example credentials

The sample SMTP auth implementation contains hard-coded credentials in the code, for example:

```python
USER_CREDENTIALS = {
    "adam": "adam"
}
```

These are only for local experimentation and should not be used in real deployments.

## Security and production notes

This repo is a laboratory/prototype project. It is not suitable for production use because:

- credentials are hard-coded in source files
- SMTP and IMAP behaviors are mocked or simplified
- TLS, certificate handling, and secure secret storage are minimal
- relaying logic is intentionally lightweight and intended for testing only

## Notes

Several files are exploratory or contain example protocol responses copied from real-world email flows. If you want to adapt this project into a real mail system, the next steps would be:

- move credentials to environment variables or a secure secret store
- replace mock IMAP responses with real mailbox state
- persist email data in a database or IMAP-compatible storage model
- enable TLS and authenticated delivery policies
- add tests around SMTP AUTH and IMAP command parsing

