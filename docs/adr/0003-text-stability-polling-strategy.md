# 3. Text Stability Polling Strategy

Date: 2024-05-24

## Status
Accepted

## Context
AI Studio streams responses. A simple wait for a "Stop" button to disappear is unreliable because the button may flicker or the DOM may lag. We experienced 30000ms timeouts using static locators.

## Decision
We implemented a multi-stage polling mechanism:
1. Wait for the run button to change state.
2. Monitor the `section.combined-content` element.
3. Compare the `inner_text` length over a 1500ms window.
4. Consider transcription complete only when the text length remains identical for 2 consecutive checks and the run button is visible.

## Consequences
- More resilient to network fluctuations and streaming pauses.
- Slower execution (by ~3s) to ensure data integrity.
