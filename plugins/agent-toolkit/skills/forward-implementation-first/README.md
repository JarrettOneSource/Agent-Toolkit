# Forward Implementation First

Use this skill when administrative markers block authorized pipeline work or
cause valid stages to be replayed. Operational guidance lives in
[SKILL.md](SKILL.md); examples live in
[examples/failure-modes.md](examples/failure-modes.md).

[examples/execution-profile.md](examples/execution-profile.md) is an optional
scheduling example for environments without an existing scheduler.

Input identity, integrity checks, locks protecting live writers, frozen
experiment rules, and required output evidence remain substantive contracts.
The skill does not authorize bypassing them or publishing outside the user's
approved scope.

`install.sh` copies the skill and examples into supported agent directories
whose parent configuration directories exist. It overwrites existing copies,
so preserve local edits first. This machine maintains its customized copy in
`~/.codex/skills/forward-implementation-first/`.

Adapted locally from [Vuk97/forward-implementation-first](https://github.com/Vuk97/forward-implementation-first).
MIT; see [LICENSE](LICENSE).
