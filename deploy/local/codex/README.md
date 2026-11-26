# Codex integration preparation

Paperclip's official image includes the Codex CLI and supports the official
`codex_local` adapter. This directory contains preparation notes only; no agent
or Codex task runs during installation.

## Rules

- Use **subscription authentication** through the official Paperclip/Codex
  browser flow when the owner explicitly authorizes it.
- Do **not** set `OPENAI_API_KEY` or substitute an API key for the subscription.
- Do **not** read, copy or commit the owner's personal `~/.codex` auth/session
  files, tokens, cookies or logs.
- Do **not** automate login. The owner completes the browser/device authorization.
- Keep any Codex session state inside the Paperclip persistent data mount.
- Do not start agents, heartbeats, routines or workflows during this Work Order.

## Future flow (after Docker is available and owner authorizes)

1. Start Paperclip at `http://localhost:3100`.
2. Claim the instance as the first admin in the browser.
3. Open the official Codex/provider connection flow and complete subscription
   authentication in the browser.
4. Verify the adapter reports the CLI presence without running a task.
5. Stop there; agent creation and execution require a later authorized Work Order.
