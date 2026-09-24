# Distributor Data Quality Checklist

Use this checklist before and after implementing a distributor parser. Report findings even when no code change is needed.

## File And Format

- Confirm actual file format, delimiter, header row, text encoding, line endings, quote style, and whether the extension is misleading.
- Watch for UTF-16 CSVs, cp1252/Latin-1 bytes in mostly-ASCII files, malformed quotes, inconsistent column counts, blank trailer rows, and mixed delimiters.
- For XML/SOAP/API/PHP feeds, save representative raw responses and identify record elements, pagination, auth headers, rate limits, and error response shapes.

## Identity

- Count non-empty, unique, and duplicate values for UPC/GTIN, distributor SKU, manufacturer SKU, and product name.
- Check for placeholder identifiers: blank UPC, `0`, all-zeroes, `N/A`, `UNKNOWN`, repeated dummy UPCs, invalid UPC lengths, and UPCs failing normalizer rules.
- Check whether inventory/pricing overlays use the same SKU shape as catalog. Normalize spaces, underscores, hyphens, casing, and leading zeroes only when justified by data.
- Report UPC mismatches between catalog and overlays. Do not silently trust one source without a distributor-specific policy.

## Row Types

- Look for parent/configurable/matrix/product-family rows that are not sellable SKUs.
- Look for variation rows where a base SKU repeats but complete SKU or option columns identify variants.
- Decide whether to skip, merge, or preserve variants based on UPC and overlay behavior.

## Overlays And Joins

- For split feeds, measure catalog-to-inventory, catalog-to-price, and inventory-to-price match rates.
- Report overlay rows missing from catalog and catalog rows missing from overlays.
- Check duplicate overlay SKUs. If duplicates differ in quantity, price, MAP, MSRP, UPC, or customer/account number, report the required business decision.
- Confirm quantity, price, MAP, and MSRP parse correctly from decimals, currency strings, blanks, negatives, zeroes, and warehouse totals.

## Product Content

- Count fill rates for name, brand/manufacturer, category, subcategory, description, caliber, capacity, image URL, MSRP, MAP, price, and quantity.
- Flag bad names such as `#REF!`, `NULL`, `TBD`, repeated generic names, truncated names, mojibake, or HTML fragments.
- Check image fields: relative filename, full URL, CDN base, multiple image variants, duplicates, broken patterns, and whether URL construction should be parser-owned.
- Review top categories/manufacturers for normalization opportunities and obvious source errors.

## Duplicate And Merge Policy

- Report duplicate UPC groups, duplicate SKU groups, and repeated names separately.
- For duplicate UPCs, inspect whether rows are true duplicates, alternate packaging, variants sharing a barcode, or source errors.
- For duplicate SKUs, inspect whether another field such as complete SKU, warehouse, customer number, or option columns must participate in the key.
- Never invent a merge policy silently. Implement a parser rule only after the data supports it.

## Metadata To Emit

Emit stable issue-count categories for relevant findings:

- `<code>_parent_product`
- `<code>_missing_upc`
- `<code>_placeholder_upc`
- `<code>_invalid_upc`
- `<code>_invalid_product_name`
- `<code>_duplicate_sku`
- `<code>_duplicate_upc`
- `<code>_overlay_upc_mismatch`
- `<code>_unmatched_overlay_row`

Include row counts, canonical item counts, skip counts, source file metadata, top categories/manufacturers, sample items, and issue counts in job metadata/history.

## Final Report Template

Report:

- Files tested with size, hash, encoding, delimiter, row counts, and headers.
- Parser/config changes made.
- Live smoke result: total rows, canonical items, skipped rows, error rows, issue counts, price/quantity/image coverage.
- Smells found and whether each was fixed, intentionally skipped, or needs a business decision.
- Tests and build commands run.
