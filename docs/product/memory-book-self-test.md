# Memory Book Self-Test

Use this when you want to prove the first Cortex brain loop yourself.

## Start

```bash
uv run cortex-capture-control-server --host 127.0.0.1 --port 8799
```

Open `http://127.0.0.1:8799/index.html#memory_palace`.

## Happy path

1. Click `Try demo`.
2. Click `Save memory`.
3. Ask: `What does Cortex remember about the dashboard demo?`
4. Confirm the `Agent handoff` card says:
   - saved memories used: `1`;
   - agent use: `answer only`;
   - safety lock: `locked`.

## Safety path

1. Click `Test secret lock`.
2. Confirm the message says `Secret lock worked`.
3. Confirm the saved memory count did not increase.

This test must not start real screen capture, store raw refs, echo the fake
secret-shaped text, export anything, or give an agent tool/action authority.
