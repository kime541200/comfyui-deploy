#!/usr/bin/env python3
"""依 profile 安裝 custom node。

用法: install_custom_nodes.py [--dry-run] PROFILE
  nodes.yaml          node 名稱 -> git repo
  profiles/PROFILE.yaml  該 profile 要裝的 node 名稱清單；`extends` 指定的 profile 先展開
已存在的 node 目錄會略過（讓 base 可先成為獨立的 image layer）。
--dry-run 只驗證名稱，不 clone。
"""
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
TARGET = Path("/app/ComfyUI/custom_nodes")


def resolve(name, seen=()):
    """展開 profile 的 extends，回傳去重且保序的 node 名稱清單（base 在前）。"""
    if name in seen:
        sys.exit(f"Circular extends: {' -> '.join((*seen, name))}")
    path = ROOT / "profiles" / f"{name}.yaml"
    if not path.is_file():
        sys.exit(f"Unknown profile '{name}': {path} not found")
    data = yaml.safe_load(path.read_text()) or {}
    nodes = resolve(data["extends"], (*seen, name)) if data.get("extends") else []
    return nodes + [n for n in data.get("nodes") or [] if n not in nodes]


def main(argv):
    dry_run = "--dry-run" in argv
    args = [a for a in argv if a != "--dry-run"]
    if len(args) != 1:
        sys.exit(__doc__)
    catalog = yaml.safe_load((ROOT / "nodes.yaml").read_text())
    wanted = resolve(args[0])
    unknown = [n for n in wanted if n not in catalog]
    if unknown:
        sys.exit(f"Not in nodes.yaml: {', '.join(unknown)}")
    if dry_run:
        print(f"OK: {len(wanted)} nodes resolved for profile '{args[0]}'")
        return

    for name in wanted:
        print(f"=== Installing custom node: {name} ===", flush=True)
        dest = TARGET / name
        if dest.exists():
            continue
        subprocess.run(
            ["git", "clone", "--depth", "1", catalog[name], str(dest)], check=True
        )
        requirements = dest / "requirements.txt"
        if requirements.is_file():
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--no-cache-dir",
                 "-r", str(requirements)],
                check=True,
            )
    print("Custom node installation complete.")


if __name__ == "__main__":
    main(sys.argv[1:])
