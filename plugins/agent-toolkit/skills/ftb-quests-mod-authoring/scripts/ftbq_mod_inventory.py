#!/usr/bin/env python3
"""Extract mod inventory and validate FTB Quests item/entity tasks.

The installed profile remains the source of truth. This helper reads jars,
language files, recipes, tags, configs, and quest SNBT files without requiring
Minecraft to launch.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import re
import sys
import tomllib
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator


QUEST_ID_RE = re.compile(r"\n\t\t\tid: \"([0-9A-F]+)\"")
TITLE_RE = re.compile(r"quest\.([0-9A-F]+)\.title: \"([^\"]+)\"")
INVALID_ITEM_RE = re.compile(
    r"Unknown registry key in ResourceKey\[minecraft:root / minecraft:item\]: ([a-z0-9_.-]+:[a-z0-9_./-]+)"
)


@dataclass
class JarMod:
    modid: str
    jar: str
    version: str | None = None
    sha256: str | None = None


@dataclass
class ModInventory:
    modid: str
    jars: list[JarMod] = field(default_factory=list)
    lang_counts: dict[str, int] = field(default_factory=dict)
    sample_entries: dict[str, list[str]] = field(default_factory=dict)
    recipe_type_counts: dict[str, int] = field(default_factory=dict)
    tag_counts: dict[str, int] = field(default_factory=dict)
    worldgen_count: int = 0
    loot_table_count: int = 0
    advancement_count: int = 0
    entity_ids: list[str] = field(default_factory=list)
    item_ids: list[str] = field(default_factory=list)
    config_files: list[str] = field(default_factory=list)


@dataclass
class QuestValidation:
    chapter: str
    quest_count: int
    item_task_count: int
    unique_item_task_count: int
    entity_task_count: int
    unique_entity_task_count: int
    missing_items: list[dict[str, str]]
    missing_entities: list[dict[str, str]]
    invalid_logged_items: list[dict[str, str]]
    scope_violations: list[dict[str, str]]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_json(data: bytes, source: str) -> Any | None:
    try:
        return json.loads(data)
    except Exception as exc:
        print(f"warning: could not parse JSON {source}: {exc}", file=sys.stderr)
        return None


def read_mods_toml(zf: zipfile.ZipFile) -> dict[str, str | None]:
    for name in ("META-INF/neoforge.mods.toml", "META-INF/mods.toml"):
        if name not in zf.namelist():
            continue
        try:
            data = tomllib.loads(zf.read(name).decode("utf-8"))
        except Exception:
            return {}
        out: dict[str, str | None] = {}
        for mod in data.get("mods", []):
            modid = mod.get("modId")
            if modid:
                out[str(modid)] = str(mod.get("version")) if mod.get("version") is not None else None
        return out
    return {}


def iter_zip_sources(jar: Path) -> Iterator[tuple[str, zipfile.ZipFile]]:
    """Yield the top-level jar and any nested JarJar mod jars.

    Some NeoForge packs ship addons as tiny wrapper jars with real mods embedded
    under META-INF/jarjar. Treat those nested jars as first-class inventory
    sources so addon IDs and quest tasks validate against the installed pack.
    """
    with zipfile.ZipFile(jar) as outer:
        yield str(jar), outer
        for name in outer.namelist():
            if not name.startswith("META-INF/jarjar/") or not name.endswith(".jar"):
                continue
            data = outer.read(name)
            with zipfile.ZipFile(io.BytesIO(data)) as nested:
                yield f"{jar}!/{name}", nested


def extract_result_ids(value: Any) -> Iterable[str]:
    if isinstance(value, str) and ":" in value:
        yield value
    elif isinstance(value, dict):
        for key in ("id", "item"):
            item_id = value.get(key)
            if isinstance(item_id, str) and ":" in item_id:
                yield item_id
        for nested in value.values():
            yield from extract_result_ids(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from extract_result_ids(nested)


def parse_quest_blocks(text: str) -> list[str]:
    marker = "\n\tquests: ["
    if marker not in text:
        return []
    start = text.index(marker) + len(marker)
    end = text.index("\n\t]", start)
    blocks: list[str] = []
    i = start
    while i < end:
        if text[i] == "{":
            depth = 0
            block_start = i
            while i < end:
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        blocks.append(text[block_start : i + 1])
                        break
                i += 1
        i += 1
    return blocks


def parse_lang_titles(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return {quest_id: title for quest_id, title in TITLE_RE.findall(path.read_text(encoding="utf-8"))}


def collect_logged_invalid_items(profile: Path) -> set[str]:
    """Read current launch logs for item IDs Minecraft rejected at ItemStack load.

    Static jar/lang/recipe evidence can include non-item registry names or
    datagen-only names. If the live log says an ID is an unknown item registry
    key, treat it as invalid for FTB item tasks until a relaunch proves
    otherwise.
    """
    invalid: set[str] = set()
    for log in (profile / "logs").glob("*.log"):
        try:
            invalid.update(INVALID_ITEM_RE.findall(log.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
    return invalid


def collect_profile_ids(profile: Path) -> tuple[set[str], set[str], dict[str, JarMod]]:
    valid_items: set[str] = set()
    valid_entities: set[str] = set()
    jar_mods: dict[str, JarMod] = {}
    for jar in sorted((profile / "mods").glob("*.jar")):
        try:
            digest = sha256(jar)
            for source, zf in iter_zip_sources(jar):
                mod_versions = read_mods_toml(zf)
                for modid, version in mod_versions.items():
                    jar_mods[modid] = JarMod(modid=modid, jar=source, version=version, sha256=digest)
                for name in zf.namelist():
                    parts = name.split("/")
                    if len(parts) >= 5 and parts[0] == "assets" and parts[2:4] == ["models", "item"] and name.endswith(".json"):
                        valid_items.add(f"{parts[1]}:{Path(name).stem}")
                    if len(parts) == 4 and parts[0] == "assets" and parts[2] == "lang" and parts[3] == "en_us.json":
                        lang = safe_json(zf.read(name), name)
                        if not isinstance(lang, dict):
                            continue
                        for key in lang:
                            m = re.match(r"(item|block|entity)\.([^.]+)\.([^.]+)$", key)
                            if not m:
                                continue
                            rid = f"{m.group(2)}:{m.group(3)}"
                            if m.group(1) in {"item", "block"}:
                                valid_items.add(rid)
                            else:
                                valid_entities.add(rid)
                    if "/recipe/" in name and name.startswith("data/") and name.endswith(".json"):
                        recipe = safe_json(zf.read(name), name)
                        if not isinstance(recipe, dict):
                            continue
                        for key in ("result", "output", "results", "outputs"):
                            if key in recipe:
                                valid_items.update(extract_result_ids(recipe[key]))
        except zipfile.BadZipFile:
            print(f"warning: bad jar {jar}", file=sys.stderr)
    return valid_items, valid_entities, jar_mods


def inventory_mod(profile: Path, modid: str, jar_mods: dict[str, JarMod]) -> ModInventory:
    inv = ModInventory(modid=modid)
    for jar in sorted((profile / "mods").glob("*.jar")):
        try:
            digest = sha256(jar)
            for source, zf in iter_zip_sources(jar):
                names = zf.namelist()
                mods = read_mods_toml(zf)
                owns_mod = modid in mods or any(n.startswith(f"assets/{modid}/") for n in names)
                if not owns_mod:
                    continue
                inv.jars.append(jar_mods.get(modid, JarMod(modid=modid, jar=source, sha256=digest)))
                for name in names:
                    parts = name.split("/")
                    if len(parts) == 4 and parts[0] == "assets" and parts[1] == modid and parts[2] == "lang" and parts[3] == "en_us.json":
                        lang = safe_json(zf.read(name), name)
                        if not isinstance(lang, dict):
                            continue
                        group_counts: collections.Counter[str] = collections.Counter()
                        samples: dict[str, list[str]] = collections.defaultdict(list)
                        for key, label in lang.items():
                            group = key.split(".", 1)[0]
                            if key.startswith(f"block.{modid}."):
                                group = "block"
                                inv.item_ids.append(f"{modid}:{key.rsplit('.', 1)[1]}")
                            elif key.startswith(f"item.{modid}."):
                                group = "item"
                                inv.item_ids.append(f"{modid}:{key.rsplit('.', 1)[1]}")
                            elif key.startswith(f"entity.{modid}."):
                                group = "entity"
                                inv.entity_ids.append(f"{modid}:{key.rsplit('.', 1)[1]}")
                            group_counts[group] += 1
                            if len(samples[group]) < 20:
                                samples[group].append(f"{key} => {label}")
                        inv.lang_counts = dict(collections.Counter(inv.lang_counts) + group_counts)
                        for group, entries in samples.items():
                            inv.sample_entries.setdefault(group, []).extend(entries)
                    if name.startswith(f"data/{modid}/recipe/") and name.endswith(".json"):
                        recipe = safe_json(zf.read(name), name)
                        recipe_type = recipe.get("type", "unknown") if isinstance(recipe, dict) else "unknown"
                        inv.recipe_type_counts[recipe_type] = inv.recipe_type_counts.get(recipe_type, 0) + 1
                    if name.startswith(f"data/{modid}/tags/") and name.endswith(".json"):
                        tag_group = name.split("/")[3] if len(name.split("/")) > 3 else "unknown"
                        inv.tag_counts[tag_group] = inv.tag_counts.get(tag_group, 0) + 1
                    if name.startswith(f"data/{modid}/worldgen/"):
                        inv.worldgen_count += 1
                    if name.startswith(f"data/{modid}/loot_table/") or name.startswith(f"data/{modid}/loot_tables/"):
                        inv.loot_table_count += 1
                    if name.startswith(f"data/{modid}/advancement") or name.startswith(f"data/{modid}/advancements"):
                        inv.advancement_count += 1
        except zipfile.BadZipFile:
            continue
    inv.item_ids = sorted(set(inv.item_ids))
    inv.entity_ids = sorted(set(inv.entity_ids))
    for group in list(inv.sample_entries):
        inv.sample_entries[group] = inv.sample_entries[group][:20]
    config_root = profile / "config"
    if config_root.exists():
        inv.config_files = sorted(
            str(path.relative_to(profile))
            for path in config_root.rglob("*")
            if path.is_file() and modid.lower().replace("_", "") in str(path).lower().replace("_", "")
        )
    return inv


def validate_chapter(
    profile: Path,
    chapter_name: str,
    valid_items: set[str],
    valid_entities: set[str],
    logged_invalid_items: set[str] | None = None,
    allowed_namespaces: set[str] | None = None,
) -> QuestValidation:
    chapter = profile / "config/ftbquests/quests/chapters" / f"{chapter_name}.snbt"
    lang = profile / "config/ftbquests/quests/lang/en_us.snbt"
    titles = parse_lang_titles(lang)
    text = chapter.read_text(encoding="utf-8")
    blocks = parse_quest_blocks(text)
    missing_items: list[dict[str, str]] = []
    missing_entities: list[dict[str, str]] = []
    invalid_logged_items: list[dict[str, str]] = []
    scope_violations: list[dict[str, str]] = []
    items: list[str] = []
    entities: list[str] = []
    logged_invalid_items = logged_invalid_items or set()
    for block in blocks:
        quest_match = QUEST_ID_RE.search(block)
        quest_id = quest_match.group(1) if quest_match else "unknown"
        title = titles.get(quest_id, quest_id)
        for item_id in re.findall(r"item: \{ count: \d+, id: \"([^\"]+)\" \}", block):
            items.append(item_id)
            namespace = item_id.split(":", 1)[0] if ":" in item_id else ""
            if allowed_namespaces and not item_id.startswith("minecraft:") and namespace not in allowed_namespaces:
                scope_violations.append({"quest": title, "id": item_id})
            if item_id in logged_invalid_items:
                invalid_logged_items.append({"quest": title, "id": item_id})
            if not item_id.startswith("minecraft:") and item_id not in valid_items:
                missing_items.append({"quest": title, "id": item_id})
        entity_candidates = set(re.findall(r"entity: \"([a-z0-9_.-]+:[a-z0-9_/.-]+)\"", block))
        entity_candidates.update(re.findall(r"entity: \{ id: \"([a-z0-9_.-]+:[a-z0-9_/.-]+)\"", block))
        if 'type: "entity"' in block:
            entity_candidates.update(re.findall(r"id: \"([a-z0-9_.-]+:[a-z0-9_/.-]+)\"", block))
        for entity_id in sorted(entity_candidates):
            entities.append(entity_id)
            if not entity_id.startswith("minecraft:") and entity_id not in valid_entities:
                missing_entities.append({"quest": title, "id": entity_id})
    return QuestValidation(
        chapter=chapter_name,
        quest_count=len(blocks),
        item_task_count=len(items),
        unique_item_task_count=len(set(items)),
        entity_task_count=len(entities),
        unique_entity_task_count=len(set(entities)),
        missing_items=missing_items,
        missing_entities=missing_entities,
        invalid_logged_items=invalid_logged_items,
        scope_violations=scope_violations,
    )


def write_markdown(path: Path, profile: Path, inventories: list[ModInventory], validation: QuestValidation | None) -> None:
    lines = [
        "# FTB Quests Mod Inventory",
        "",
        f"Profile: `{profile}`",
        "",
    ]
    for inv in inventories:
        lines.extend([f"## {inv.modid}", ""])
        if inv.jars:
            lines.append("Jars:")
            for jar in inv.jars:
                version = f", version `{jar.version}`" if jar.version else ""
                digest = f", sha256 `{jar.sha256}`" if jar.sha256 else ""
                lines.append(f"- `{Path(jar.jar).name}`{version}{digest}")
            lines.append("")
        lines.append(f"Language counts: `{json.dumps(inv.lang_counts, sort_keys=True)}`")
        lines.append(f"Recipe types: `{json.dumps(inv.recipe_type_counts, sort_keys=True)}`")
        lines.append(f"Tag groups: `{json.dumps(inv.tag_counts, sort_keys=True)}`")
        lines.append(f"Worldgen files: `{inv.worldgen_count}`")
        lines.append(f"Loot tables: `{inv.loot_table_count}`")
        lines.append(f"Advancements: `{inv.advancement_count}`")
        lines.append(f"Item/block IDs from lang: `{len(inv.item_ids)}`")
        lines.append(f"Entity IDs from lang: `{len(inv.entity_ids)}`")
        if inv.entity_ids:
            lines.append("Entities: " + ", ".join(f"`{x}`" for x in inv.entity_ids[:80]))
        if inv.config_files:
            lines.append("")
            lines.append("Config files:")
            lines.extend(f"- `{x}`" for x in inv.config_files)
        lines.append("")
        for group, samples in sorted(inv.sample_entries.items()):
            lines.append(f"Sample `{group}` entries:")
            lines.extend(f"- {sample}" for sample in samples[:12])
            lines.append("")
    if validation:
        lines.extend([
            "## Quest Validation",
            "",
            f"Chapter: `{validation.chapter}`",
            f"Quests: `{validation.quest_count}`",
            f"Item tasks: `{validation.item_task_count}` total, `{validation.unique_item_task_count}` unique",
            f"Entity tasks: `{validation.entity_task_count}` total, `{validation.unique_entity_task_count}` unique",
            f"Missing item IDs: `{len(validation.missing_items)}`",
            f"Missing entity IDs: `{len(validation.missing_entities)}`",
            f"Log-invalid item IDs: `{len(validation.invalid_logged_items)}`",
            f"Scope violations: `{len(validation.scope_violations)}`",
            "",
        ])
        for label, rows in (
            ("Missing items", validation.missing_items),
            ("Missing entities", validation.missing_entities),
            ("Log-invalid items", validation.invalid_logged_items),
            ("Scope violations", validation.scope_violations),
        ):
            if rows:
                lines.append(f"### {label}")
                lines.extend(f"- `{row['id']}` in {row['quest']}" for row in rows)
                lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--modids", required=True, help="Comma-separated mod ids to inventory")
    parser.add_argument("--chapter", help="FTB Quests chapter filename without .snbt")
    parser.add_argument("--allowed-namespaces", help="Comma-separated namespaces allowed in item tasks for this chapter")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero if chapter validation has missing, log-invalid, or out-of-scope item/entity tasks")
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--out-json", type=Path)
    args = parser.parse_args()

    profile = args.profile
    modids = [x.strip() for x in args.modids.split(",") if x.strip()]
    allowed_namespaces = {x.strip() for x in args.allowed_namespaces.split(",") if x.strip()} if args.allowed_namespaces else None
    valid_items, valid_entities, jar_mods = collect_profile_ids(profile)
    logged_invalid_items = collect_logged_invalid_items(profile)
    inventories = [inventory_mod(profile, modid, jar_mods) for modid in modids]
    validation = validate_chapter(profile, args.chapter, valid_items, valid_entities, logged_invalid_items, allowed_namespaces) if args.chapter else None
    result = {
        "profile": str(profile),
        "inventories": [asdict(inv) for inv in inventories],
        "validation": asdict(validation) if validation else None,
    }
    if args.out_json:
        args.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        write_markdown(args.out_md, profile, inventories, validation)
    print(json.dumps({
        "mods": modids,
        "valid_items": len(valid_items),
        "valid_entities": len(valid_entities),
        "logged_invalid_items": len(logged_invalid_items),
        "validation": asdict(validation) if validation else None,
    }, indent=2, sort_keys=True))
    if args.strict and validation:
        failed = validation.missing_items or validation.missing_entities or validation.invalid_logged_items or validation.scope_violations
        if failed:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
