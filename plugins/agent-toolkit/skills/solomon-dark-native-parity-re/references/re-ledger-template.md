# Deep RE ledger entry template

Use this shape for the relevant system file under
`Website/docs/Game Native Parity RE/`. Extend the existing file for that system;
create a new numbered file and index entry only for a genuinely separate system.
Adapt headings to the mechanic; omit inapplicable fields rather than filling
the entry with `N/A`.

```markdown
## YYYY-MM-DD — <native system or mechanic>

### Reported smell and parity question

- Reported web behavior:
- Stock behavior to recover:
- Reproduction inputs/scenes:
- Falsifiable questions:

### Evidence and provenance

| Evidence class | Exact source | Observation | Confidence |
| --- | --- | --- | --- |
| Clean stock | executable/capture/frame | ... | high/medium/low |
| Instructions | function/address/range | ... | high/medium/low |
| Runtime | process/build/address/probe | ... | high/medium/low |
| Asset/data | file/record/registry slot | ... | high/medium/low |

Clearly label injected-loader or debugger evidence. Record the preferred image
base and runtime ASLR mapping when runtime addresses appear.

### System boundary and membership inventory

Native system: <name and one-line boundary definition>

| Member (class/variant/scene/branch) | Native source (function/table row/record) | Disposition | Proof |
| --- | --- | --- | --- |
| ... | ... | exact-ported | test/receipt |

One row per member found by the membership sweep (xrefs, authored tables,
registries, scenes, state branches). Allowed final dispositions: `exact-ported`,
`verified-already-at-parity`, `out-of-system` (reason), `blocked-by-platform`
(named browser constraint). `not-yet-extracted` is not a disposition, and a
missing row prevents completion. While investigating, record unresolved
evidence and `recovered-pending-port` status explicitly. Replace every
provisional status with a supported final disposition before delivery.

### Native ownership thread

- Owner and construction path:
- Upstream state producers/callers:
- State representation and transitions:
- Downstream consumers/callees:
- Sibling systems sharing ownership or data:
- Entry, interruption, reset, and teardown:

### Recovered behavioral contract

- Timing/ticks/thresholds:
- Geometry/transforms/coordinate spaces:
- Render/hit/collision/traversal order:
- Assets/audio/randomness:
- Input/network authority/replication:
- Boundary and failure behavior:

### Nearby-system findings

- Durable finding:
- Evidence:
- Why it matters or may matter later:
- Website ledger/catalog destination:

### Confidence and open questions

- Confirmed:
- Inferred:
- Unknown:
- Next falsifying probe if the unknown becomes material:

### Web implementation consequence

- Correct owner/module:
- Shared model change:
- Stock behavior preserved:
- Browser-specific approximation, if unavoidable:
- Symptom patch or obsolete path to remove:

### Validation contract

- Focused automated test:
- Playwright or runtime journey:
- Stock-versus-web comparison:
- Measurable acceptance criteria:

### Implementation validation receipt

- Files/modules changed:
- Tests and canonical gate:
- Browser/native evidence:
- Remaining implementation explicitly out of scope:
```

Website is the sole durable owner. Put system explanation in the matching
Website ledger file and machine-consumable addresses, records, or catalog
entries in an appropriate Website-owned artifact when one is justified. Never
update Mod Loader docs, reports, catalogs, configuration, scripts, tests, or
other files; they are read-only tooling or historical evidence for this skill.

Use this investigation breadth check before coding:

- [ ] system boundary declared; membership enumerated from xrefs, authored
      tables, registries, scenes, and state branches
- [ ] every authored data table the system consumes extracted in full — all
      rows, variants, and styles, including members absent from the reported
      scene
- [ ] every membership row has a recovered native contract or a named platform
      constraint; members still needing implementation are marked
      `recovered-pending-port`, not falsely declared ported
- [ ] any assumption falsified for one member is corrected in the recovered
      model for every member sharing it; required implementation changes are
      recorded
- [ ] owner, constructor, and lifetime recovered
- [ ] state writers and transition conditions recovered
- [ ] update/render/audio/collision consumers recovered as applicable
- [ ] timing, geometry, order, and coordinate spaces recovered as applicable
- [ ] scene entry/reset/interruption/teardown recovered
- [ ] shared factory, registry, vtable, bundle, or sibling path inspected
- [ ] multiplayer authority or replication inspected when state can be shared
- [ ] clean-stock observation and instruction/data evidence reconciled
- [ ] nearby durable findings documented
- [ ] confidence explicit; every unknown platform-justified, none merely
      unextracted
- [ ] validation planned per member, not only for the reported symptom
- [ ] ledger updated before web implementation
