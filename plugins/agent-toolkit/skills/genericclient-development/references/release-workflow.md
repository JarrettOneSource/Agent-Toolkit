# Build, install, and publication workflow

Read this reference when packaging, restarting RuneLite, or pushing a stable
GenericClient phase.

## Full local gates

From `/home/user/GenericClient` run:

```bash
./gradlew test shadowJar
npm --prefix mcp test
git diff --check
```

Run focused tests first when iterating, but do not substitute them for the full
gate. Inspect failures; do not rerun blindly.

## Controlled install

1. Stop active standalone Lua and REPL work or wait for its terminal receipt.
2. Log out through GenericClient when logged in.
3. Resolve the current RuneLite PID and stop the process. Confirm it exited.
4. Never copy over the installed JAR while RuneLite is running.
5. Compute the source JAR SHA-256, copy it to the installed path, then compute
   the installed SHA-256. They must match exactly.
6. Resolve the current visible Jagex Launcher renderer dynamically. Do not reuse
   an old child HWND. Trigger the selected account's Play action through the
   active launcher session.
7. Wait for a successful `/rpc` `status` response and `LOGIN_SCREEN`; do not use
   obsolete HTTP paths as readiness checks.
8. Call `session_login`, then verify `LOGGED_IN`, account identity/location,
   plugin lifecycle, installed script schema, and the requested live behavior.

The Jagex Launcher is account/session bootstrap; `session_login` handles the
RuneLite login/click-to-play portion after the plugin endpoint exists.

## Live acceptance

Capture the smallest decisive evidence:

- exact artifact hash;
- installed schema/module paths;
- client status and account snapshot;
- terminal Lua/walker/action receipt;
- screenshot when the visible result matters;
- recent chat/system messages for game transitions.

Do not claim a broad route, quest, combat system, or account milestone from a
single unit test or hover receipt.

## Cleanup and push

1. Delete temporary diagnostics using scoped file edits.
2. Update source docs and account notes with only verified facts.
3. Inspect `git status`, `git diff --stat`, `git diff --check`, and the relevant
   full diff. Preserve unrelated user changes.
4. Commit a coherent stable phase. Do not include credentials, runtime caches,
   downloaded videos, or temporary traces.
5. Pull/rebase only when needed and without destructive resets. Resolve any
   overlap deliberately.
6. Push the requested branch, then verify local `HEAD`, `origin`, and remote
   branch state. Publication and installed live acceptance are separate facts.
