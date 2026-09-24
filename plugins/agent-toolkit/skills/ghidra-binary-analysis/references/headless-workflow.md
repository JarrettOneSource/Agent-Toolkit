# Headless Ghidra Workflow

## Command Templates

### Existing analyzed project

Use this when the program is already imported and analyzed:

```bash
env JAVA_HOME='C:/path/to/jdk' \
  cmd.exe /c C:/path/to/ghidra/support/analyzeHeadless.bat \
  D:/path/to/ghidra_project ProjectName \
  -readOnly -process binary.exe -noanalysis \
  -postScript D:/path/to/skill/scripts/decompile_targets.py 0x140001000 \
  -scriptPath D:/path/to/skill/scripts \
  > output.log 2>&1
```

### Initial import

Use this when the binary has not been imported yet:

```bash
env JAVA_HOME='C:/path/to/jdk' \
  cmd.exe /c C:/path/to/ghidra/support/analyzeHeadless.bat \
  D:/path/to/ghidra_project ProjectName \
  -import D:/path/to/binary.exe
```

### Notes

- Use Windows-style paths when invoking `cmd.exe /c analyzeHeadless.bat` from WSL.
- Keep one project open in one headless session at a time unless every session is explicitly read-only and you understand the lock behavior.
- For repeat extraction on an already analyzed program, prefer `-readOnly -process ... -noanalysis`.

## Investigation Recipes

### Recover a parser or file format

1. Search for file paths, section labels, config keys, or user-facing strings with `scripts/search_terms_refs.py`.
2. Decompile the parser entry points with `scripts/decompile_targets.py`.
3. Follow referenced globals, tables, and helper functions with `scripts/refs_to_addr_decompile.py`.
4. Dump any lookup tables with `scripts/dump_array.py`.
5. Trace class-specific handlers or factory functions if the parser emits type IDs or flags.

### Recover class stats or embedded gameplay data

1. Find factories, constructors, or RTTI names with `scripts/search_terms_refs.py`.
2. If you know field offsets like HP, damage, XP, or speed, use `scripts/find_offset_accesses.py`.
3. Decompile candidate constructors and shared init methods.
4. Dump nearby float/int clusters with `scripts/dump_array.py` and `scripts/dump_values.py`.
5. Separate constructor baselines from post-init/global scaling.

### Work through a global state block

1. Use `scripts/list_symbols_range.py` to identify nearby labels.
2. Use `scripts/refs_in_range.py` to find all direct instruction references into the range.
3. Decompile the small set of functions that touch the block.
4. Treat mirrored/checkpoint globals separately from the real source-of-truth writer.

### Work through RTTI and virtual dispatch

1. Search for RTTI strings or class names with `scripts/search_terms_refs.py`.
2. Resolve vtable slots with `scripts/vtable_slot_lookup.py`.
3. Decompile the resolved virtual methods and the constructors that install the vtables.
4. If the constructor only calls a parent ctor and swaps the vtable, follow the parent ctor before concluding the base stats.

## Practical Heuristics

- If a decompiled constructor uses `undefined8 *param_1`, multiply pointer indices by `8` before assigning field names.
- If a value looks wrong after decompilation, check raw instructions with `scripts/dump_function_instructions.py`.
- If a table is clearly a float cluster but individual names are missing, dump the whole range first, then assign meanings from call sites.
- Distinguish verified behavior from strong inference in the final write-up.
