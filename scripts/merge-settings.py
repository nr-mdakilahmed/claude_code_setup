#!/usr/bin/env python3
"""
Merge cc-team-setup settings.template.json into ~/.claude/settings.json non-destructively.
Backs up the original before making any changes.
"""
import json, sys, os, shutil
from datetime import datetime

def load(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def merge_hooks(target, template):
    added = []
    for event, hook_list in template.get("hooks", {}).items():
        target.setdefault("hooks", {}).setdefault(event, [])
        existing_cmds = set()
        for entry in target["hooks"][event]:
            for h in entry.get("hooks", []):
                existing_cmds.add(h.get("command", ""))
        for entry in hook_list:
            cmds = [h.get("command", "") for h in entry.get("hooks", [])]
            if not any(c in existing_cmds for c in cmds):
                target["hooks"][event].append(entry)
                added.append(f"  + hook [{event}]: {cmds[0][:60]}")
    return added

def merge_allow(target, template):
    added = []
    target.setdefault("permissions", {}).setdefault("allow", [])
    existing = set(target["permissions"]["allow"])
    for entry in template.get("permissions", {}).get("allow", []):
        if entry not in existing:
            target["permissions"]["allow"].append(entry)
            existing.add(entry)
            added.append(f"  + allow: {entry}")
    return added

def merge_plugins(target, template):
    added = []
    target.setdefault("enabledPlugins", {})
    for plugin_id, enabled in template.get("enabledPlugins", {}).items():
        if plugin_id not in target["enabledPlugins"]:
            target["enabledPlugins"][plugin_id] = enabled
            added.append(f"  + plugin: {plugin_id} = {enabled}")
    return added

def merge_marketplaces(target, template):
    added = []
    target.setdefault("extraKnownMarketplaces", {})
    for name, config in template.get("extraKnownMarketplaces", {}).items():
        if name not in target["extraKnownMarketplaces"]:
            target["extraKnownMarketplaces"][name] = config
            added.append(f"  + marketplace: {name}")
    return added

def main():
    if len(sys.argv) < 3:
        print("Usage: merge-settings.py <template.json> <target settings.json>")
        sys.exit(1)

    template_path = sys.argv[1]
    target_path = sys.argv[2]

    template = load(template_path)
    target = load(target_path)

    # Backup
    if os.path.exists(target_path):
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        bak = f"{target_path}.bak.{ts}"
        shutil.copy(target_path, bak)
        print(f"Backed up → {bak}")

    all_added = []

    # model (only if not set)
    if "model" not in target and "model" in template:
        target["model"] = template["model"]
        all_added.append(f"  + model: {template['model']}")

    # statusLine (only if not set)
    if "statusLine" not in target and "statusLine" in template:
        target["statusLine"] = template["statusLine"]
        all_added.append("  + statusLine")

    all_added += merge_hooks(target, template)
    all_added += merge_allow(target, template)
    all_added += merge_plugins(target, template)
    all_added += merge_marketplaces(target, template)

    with open(target_path, "w") as f:
        json.dump(target, f, indent=2)

    if all_added:
        print(f"Merged {len(all_added)} additions into {target_path}:")
        print("\n".join(all_added))
    else:
        print("Nothing to merge — settings.json already up to date.")

if __name__ == "__main__":
    main()
