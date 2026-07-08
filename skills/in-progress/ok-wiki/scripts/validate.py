#!/usr/bin/env python3
import os
import sys
import re
import json


def load_config():
    config_path = os.path.expanduser("~/.config/ok-wiki/config.json")
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to parse config file: {e}")
    return {}


def parse_frontmatter(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        return None, None, f"Failed to read file: {e}"

    # Match frontmatter block at start of file
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", content, re.DOTALL)
    if not match:
        return (
            None,
            content,
            "Missing YAML frontmatter block starting and ending with ---",
        )

    frontmatter_text = match.group(1)
    body_text = match.group(2)

    frontmatter = {}
    lines = frontmatter_text.splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            return None, content, f"Malformed line in frontmatter: '{line}'"
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        # Clean quotes and brackets
        val = re.sub(r'^["\'\[]?(.*?)["\'\]]?$', r"\1", val)
        frontmatter[key] = val

    if "type" not in frontmatter or not frontmatter["type"]:
        return None, content, "Missing required 'type' key in frontmatter"

    return frontmatter, body_text, None


def extract_relative_links(body, current_dir):
    links = []
    # Match markdown links: [label](path)
    matches = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", body)
    for label, target_path in matches:
        # Skip web links, email links, anchors
        if target_path.startswith(("http://", "https://", "mailto:", "#")):
            continue

        # Clean query/anchor params
        target_clean = target_path.split("#")[0].split("?")[0]
        if not target_clean:
            continue

        # Resolve target path relative to current dir
        abs_target = os.path.normpath(os.path.join(current_dir, target_clean))
        if os.path.isdir(abs_target):
            index_path = os.path.join(abs_target, "index.md")
            if os.path.isfile(index_path):
                abs_target = index_path
        links.append({"label": label, "raw_path": target_path, "abs_path": abs_target})
    return links


def validate_bundle(root_dir):
    print(f"Scanning OK-Wiki bundle at: {root_dir}")
    if not os.path.isdir(root_dir):
        print(f"Error: {root_dir} is not a valid directory.")
        return 1

    # Base ignore folders
    ignore_dirs = {
        ".git",
        ".obsidian",
        "assets",
        "scratch",
        "node_modules",
        ".venv",
        "env",
    }

    # Load custom ignores from config if present
    config = load_config()
    custom_ignores = config.get("ignore_dirs", [])
    if isinstance(custom_ignores, list):
        for d in custom_ignores:
            ignore_dirs.add(d)

    ignore_files = {"index.md", "log.md"}

    concepts = {}
    links_to_check = []
    index_links = {}
    errors = []
    warnings = []

    # 1. Walk and scan concept files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Prune ignored folders in-place
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

        for file in filenames:
            if not file.endswith(".md"):
                continue

            abs_path = os.path.join(dirpath, file)
            rel_path = os.path.relpath(abs_path, root_dir)

            # Special validation for log.md
            if file == "log.md":
                try:
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        log_content = f.read()
                    # Check for date headings
                    dates = re.findall(
                        r"^##\s+(\d{4}-\d{2}-\d{2})", log_content, re.MULTILINE
                    )
                    if not dates:
                        warnings.append(
                            f"{rel_path}: No date headings (## YYYY-MM-DD) found in changelog."
                        )
                except Exception as e:
                    errors.append(f"{rel_path}: Failed to read log file: {e}")
                continue

            # Special validation for index.md
            if file == "index.md":
                try:
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        index_content = f.read()
                    file_links = extract_relative_links(index_content, dirpath)
                    index_links[abs_path] = set()
                    for link in file_links:
                        index_links[abs_path].add(link["abs_path"])
                        links_to_check.append(
                            {
                                "source_rel": rel_path,
                                "label": link["label"],
                                "raw_path": link["raw_path"],
                                "abs_path": link["abs_path"],
                            }
                        )
                except Exception as e:
                    errors.append(f"{rel_path}: Failed to read index file: {e}")
                continue

            if file in ignore_files:
                continue

            # Parse regular concept document
            frontmatter, body, err = parse_frontmatter(abs_path)
            if err:
                errors.append(f"{rel_path}: {err}")
                continue

            concept_id = rel_path[:-3].replace("\\", "/")
            concepts[concept_id] = abs_path

            # Extract relative links
            file_links = extract_relative_links(body, dirpath)
            for link in file_links:
                links_to_check.append(
                    {
                        "source_rel": rel_path,
                        "label": link["label"],
                        "raw_path": link["raw_path"],
                        "abs_path": link["abs_path"],
                    }
                )

    # 2. Check all extracted relative links
    for link in links_to_check:
        target_abs = link["abs_path"]
        if not os.path.exists(target_abs):
            warnings.append(
                f"{link['source_rel']}: Broken link [ {link['label']} ] -> '{link['raw_path']}' (File not found: {os.path.basename(target_abs)})"
            )

    # 3. Check for orphaned concepts (missing from parent index.md)
    for concept_id, concept_abs in concepts.items():
        concept_dir = os.path.dirname(concept_abs)
        parent_index = os.path.join(concept_dir, "index.md")
        rel_concept = os.path.relpath(concept_abs, root_dir)

        if not os.path.isfile(parent_index):
            warnings.append(
                f"{rel_concept}: Parent index.md is missing (should be at {os.path.relpath(parent_index, root_dir)})."
            )
        elif parent_index not in index_links or concept_abs not in index_links[parent_index]:
            warnings.append(
                f"{rel_concept}: Concept is orphaned (not linked in {os.path.relpath(parent_index, root_dir)})."
            )

    # 4. Check for unlinked subdirectory indexes
    for index_path in list(index_links.keys()):
        if index_path == os.path.join(root_dir, "index.md"):
            continue

        index_dir = os.path.dirname(index_path)
        parent_dir = os.path.dirname(index_dir)
        parent_index = os.path.join(parent_dir, "index.md")

        rel_index = os.path.relpath(index_path, root_dir)
        rel_parent_index = os.path.relpath(parent_index, root_dir)

        if not os.path.isfile(parent_index):
            warnings.append(
                f"{rel_index}: Parent index.md is missing ({rel_parent_index})."
            )
        elif parent_index not in index_links or index_path not in index_links[parent_index]:
            warnings.append(
                f"{rel_index}: Subdirectory index is not linked in parent index ({rel_parent_index})."
            )

    # 3. Print Results
    print("\n--- Validation Results ---")
    print(f"Scanned {len(concepts)} concepts.")

    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  [WARN] {warning}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for error in errors:
            print(f"  [FAIL] {error}")
        print("\nValidation FAILED.")
        return 1

    print("\nValidation PASSED successfully.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate.py <path_to_wiki_root>")
        sys.exit(1)

    target_root = os.path.abspath(sys.argv[1])
    sys.exit(validate_bundle(target_root))
