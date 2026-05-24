# 2. Use CDP for Browser Connection

Date: 2024-05-24

## Status
Accepted

## Context
Initial authentication via `auth_google.json` was brittle and frequently triggered security blocks or required manual session handling.

## Decision
We switched to using a Chrome DevTools Protocol (CDP) connection on port 9222. This allows the script to attach to an already authenticated, manually opened browser instance.

## Consequences
- Requires the user to launch Chrome with `--remote-debugging-port=9222`.
- Dramatically increases stability by bypassing Google’s bot detection on login.
