---
name: add-distributor
description: "Add or repair FFLScan distributor feeds, parsers, and mappings; audit source data and ingestion results."
---

# Add Distributor

## Overview

Add distributors through the ingestion architecture, not by patching isolated parsing logic. For a new or changed source contract, verify live data and make distributor-specific rules explicit. For a focused parser repair, inspect the affected source and representative fixtures; expand to other feeds only when joins or shared behavior require it.

For a data-quality audit, use supplied files and fetch live sources only when
the requested verification needs them. Report findings and unresolved identity
or mapping choices; parser implementation is a separate branch taken when the
task requests a change. Audit-only work does not require a build or new tests.

## Workflow

1. Read local instructions and the ingestion surfaces relevant to this change.
   - Check repo instructions and current ingestion files under `src/FFLScan.Infrastructure/Services/Ingestion`.
   - For feed registration or defaults, inspect `src/FFLScan.Infrastructure/Data/DatabaseSeeder.cs` and `src/FFLScan.Infrastructure/Services/SupportedDistributorRegistry.cs`.
   - Compare against the pre-refactor implementation with `git show HEAD:<path>` when behavior claims need verification.

2. Protect credentials.
   - Do not print credentials in commands, logs, tests, or final output.
   - Use temporary downloader/smoke projects under `/tmp` when live SFTP/FTP/API access is needed.
   - Store downloaded analysis files under `/tmp/fflscan-feed-analysis/<distributor-slug>/`.

3. Identify the relevant source files and obtain any additional files needed for the task.
   - Include primary catalog, inventory/QOH overlays, pricing overlays, image/detail feeds, and API/SOAP/PHP responses when configured or discoverable.
   - Record non-secret facts: remote path, local temp path, file size, hash, encoding, row count, delimiter, and headers.
   - If a listed file is unavailable but an existing mapping references another file, test both and report the discrepancy.

4. Analyze data before coding.
   - Use `python3 tools/feed-analyzer/analyze_feed.py <file> --sample 100000` when available.
   - For split feeds, run additional join analysis across catalog, inventory, pricing, and images using normalized keys.
   - Read `references/data-quality-checklist.md` for smells that must be investigated and reported.

5. For an implementation, decide whether a custom parser is required.
   - Use the generic parser only when headers, encodings, identifiers, and overlays are clean.
   - Create a standalone parser under `src/FFLScan.Infrastructure/Services/Ingestion/Parsers/<Distributor>DistributorFeedParser.cs` when the feed needs distributor-specific encoding, header correction, identity rules, parent/variant handling, image URL construction, duplicate policy, or row skips.
   - Register custom parsers before `GenericDistributorFeedParser` in `src/FFLScan.Infrastructure/Hosting/FflScanServiceCollectionExtensions.cs`.
   - Keep distributor rules in the parser; keep persistence logic in the ingestion service.

6. Be explicit about identity.
   - Prefer real UPC/GTIN values from catalog or trusted overlays.
   - Where missing UPC means “not a sellable/importable row,” SKU must not substitute for UPC. Flag an unsupported fallback during an audit; change it within an implementation task.
   - Treat placeholder UPCs such as `0`, all-zeroes, `N/A`, blank, or invalid lengths as smells requiring either skip rules or a documented policy.

7. When changing ingestion, preserve metadata and history.
   - Emit skipped-row reasons with stable issue categories such as `<code>_missing_upc`, `<code>_invalid_product_name`, or `<code>_parent_product`.
   - Ensure aggregate issue counts appear in `ImportMetadata.IssueCounts`.
   - Ensure final runs persist metadata into `ImportLogs.MetadataJson`; detailed samples can remain in `SampleErrors`.

8. Validate the requested result.
   - For an audit, verify row counts, joins, representative anomalies, and the evidence behind each finding.
   - For code changes, add focused tests with small local sample files covering the affected parser rules, joins, invalid rows, duplicate handling, metadata counts, or mapped fields.
   - Put distributor metadata tests in the matching split file under `tests/FFLScan.Tests/Ingestion/DistributorFeedReaderMetadataTests.*.cs`: CSV/TXT distributors in `.CsvDistributors.cs`, XML/API/SOAP/detail-feed distributors in `.StructuredDistributors.cs`, shared builders in `.RowBuilders.cs`, and reusable test setup in `.FactoryHelpers.cs`.
   - For code changes, run the affected tests and the repository's required checks; expand only for changed dependencies or unresolved failures.
   - When verifying ingestion behavior, smoke-run the reader against representative downloaded files without touching production data.

9. Final report.
   - State what files were tested, what parser was added or changed, live row/item/skip counts, issue counts, and remaining data smells.
   - Clearly call out smells that need business decisions before optimization, especially duplicate UPC/SKU policy, parent/variant modeling, placeholder identifiers, bad names, questionable category normalization, encoding anomalies, and mismatched overlay UPCs.

## Implementation Standards

- Keep each custom distributor parser in its own file.
- Do not add broad fallback behavior to make one bad feed pass.
- Do not hide source data defects by silently merging or fabricating identifiers.
- Prefer source-specific skip reasons over generic `missing_identifier` when the cause is known.
- Update seed/registry mappings to match live headers and feed paths.
- Leave downloaded files and analysis outputs in `/tmp` only; remove temporary downloader/smoke project directories before finishing.
