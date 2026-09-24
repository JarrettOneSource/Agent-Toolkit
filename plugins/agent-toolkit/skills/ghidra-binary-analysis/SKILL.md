---
name: ghidra-binary-analysis
description: "Inspect native binaries with headless Ghidra: decompile functions, trace references, and extract layouts or data."
---

# Ghidra Binary Analysis

Use bundled headless scripts for repeatable Ghidra queries and extraction.

Resolve `scripts/` relative to this skill's directory (`${CLAUDE_SKILL_DIR}` in Claude Code). Prefer an up-to-date project-local copy under `tools/ghidra-scripts/` when the project owns the investigation tooling.

Prefer an existing imported/analyzed project when one is available. Use `-process <program>` with `-noanalysis` for repeat queries. Prefer `-readOnly` to avoid lock contention when running many headless queries against the same project.

Read [references/headless-workflow.md](references/headless-workflow.md) when you need command templates, WSL-to-Windows path examples, or common investigation recipes.

## Select the query

Establish the project path, project name, program, and binary identity from the
request and current project. Use the matching script below directly when a
function, address, range, or table is known. Broader string, RTTI, or offset
searches are for unresolved targets, not prerequisites for every query.

Honor project-specific wrappers and replica rules. When invoking Windows
Ghidra from WSL, use Windows paths in the command; the reference has templates
for existing projects and initial imports.

## Common Reverse-Engineering Patterns

- Start from strings, RTTI names, or parser tokens, then pivot to xrefs and nearby constructors.
- For C++ binaries, look for type factories that map IDs to constructors, then find common post-constructor init functions that apply global modifiers.
- For MSVC binaries, use `::vftable` symbols and RTTI strings to recover constructors and virtual overrides.
- When Ghidra decompiles `param_1` as `undefined8 *` or another typed pointer, convert `param_1 + n` into byte offsets before naming fields.
- Serialize headless Ghidra runs against the same project. Do not run multiple writable sessions in parallel on one project.

## Bundled Scripts

| Script | Use |
| --- | --- |
| `scripts/decompile_targets.py` | Decompile one or more functions by address or exact name |
| `scripts/search_terms_refs.py` | Find strings/symbols and the functions that reference them |
| `scripts/find_offset_accesses.py` | Find candidate functions touching specific object-field offsets |
| `scripts/refs_to_addr_decompile.py` | Decompile every function referencing one or more addresses |
| `scripts/dump_array.py` | Dump byte/int/float sequences from memory |
| `scripts/dump_values.py` | Dump a few isolated float constants by address |
| `scripts/vtable_slot_lookup.py` | Resolve function pointers at a vtable slot |
| `scripts/list_symbols_range.py` | List symbols inside an address range |
| `scripts/refs_in_range.py` | Scan instructions for direct references into an address range |
| `scripts/dump_function_instructions.py` | Dump raw instructions from a function body |

## Output Shape

Lead with the requested formula, behavior, or extracted data, then give the
function addresses, field offsets, table records, or instructions supporting it.
Distinguish observations from decompiler interpretation and inference. State
unresolved writers, aliases, or inherited constructors when they limit the
answer; do not expand a completed narrow query into a whole-binary audit.
