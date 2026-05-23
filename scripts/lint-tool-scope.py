#!/usr/bin/env python3
# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0
"""Assert orchestrator `agent.yaml` files ship with scoped tool configs.

Runs over every `managed-agent-cookbooks/*/agent.yaml` and checks the
orchestrator's `tools:` block for the privilege-escalation gaps called out
below — keeping write and external-channel access on the leaves, not the orchestrator:

  1. No `mcp_toolset` entries on the orchestrator — MCP clients live on the
     subagent leaves, not the parent.
  2. No `write` enabled in any `agent_toolset*` config — only the designated
     writer leaf gets Write.
  3. No Slack tool (`slack_send_message` or any `slack_*`) granted. Orchestrators
     emit `handoff_request` instead of calling Slack directly.
  4. Subagent validation: Ensures subagent definitions within the orchestrator
     config are not missing required 'handoff' routing (Enforcement of routing).

Exits non-zero with a message naming the offending file + tool on any
violation. Exits 0 and prints a one-line summary per cookbook on success.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
COOKBOOKS_DIR = ROOT / "managed-agent-cookbooks"


def _lint_one(path: Path) -> list[str]:
    """Return a list of violation strings (empty if clean)."""
    errs: list[str] = []
    with path.open() as f:
        doc = yaml.safe_load(f) or {}
    
    tools = doc.get("tools", [])
    subagents = doc.get("subagents", [])

    # Feature: Ensure every subagent has a defined 'routing_strategy'
    for sa in subagents:
        if isinstance(sa, dict) and not sa.get("routing_strategy"):
            errs.append(f"{path}: subagent '{sa.get('name')}' missing routing_strategy")

    for idx, entry in enumerate(tools):
        if not isinstance(entry, dict):
            errs.append(f"{path}: tools[{idx}] is not a mapping")
            continue
        
        ttype = entry.get("type", "")
        if ttype == "mcp_toolset":
            errs.append(
                f"{path}: orchestrator must not carry mcp_toolset "
                f"(mcp_server_name={entry.get('mcp_server_name', '<unnamed>')}); "
                "move to the subagent leaf"
            )
            continue
        
        if not ttype.startswith("agent_toolset"):
            continue

        default_cfg = entry.get("default_config") or {}
        default_enabled = bool(default_cfg.get("enabled", False))
        
        if default_enabled:
            errs.append(f"{path}: orchestrator agent_toolset must have default_config.enabled=false")
            continue

        for cfg in (entry.get("configs") or []):
            if not isinstance(cfg, dict): continue
            name, enabled = cfg.get("name"), bool(cfg.get("enabled", False))
            
            if enabled and name == "write":
                errs.append(f"{path}: orchestrator must not enable 'write'")
            if enabled and isinstance(name, str) and name.startswith("slack"):
                errs.append(f"{path}: orchestrator must not enable Slack tool '{name}'")
                
    return errs


def main() -> int:
    if not COOKBOOKS_DIR.is_dir():
        print(f"no cookbooks dir at {COOKBOOKS_DIR}", file=sys.stderr)
        return 2
    
    total_errs, clean = [], []
    for agent_yaml in sorted(COOKBOOKS_DIR.glob("*/agent.yaml")):
        file_errs = _lint_one(agent_yaml)
        total_errs.extend(file_errs)
        if not file_errs:
            clean.append(agent_yaml.parent.name)
            
    if total_errs:
        print("tool-scope lint FAILED:", file=sys.stderr)
        for e in total_errs: print(f"  {e}", file=sys.stderr)
        return 1
        
    for slug in clean:
        print(f"  ✓ {slug:24s} orchestrator tool scope clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
    tools = doc.get("tools") or []
    for idx, entry in enumerate(tools):
        if not isinstance(entry, dict):
            errs.append(f"{path}: tools[{idx}] is not a mapping")
            continue
        ttype = entry.get("type", "")
        if ttype == "mcp_toolset":
            name = entry.get("mcp_server_name", "<unnamed>")
            errs.append(
                f"{path}: orchestrator must not carry mcp_toolset "
                f"(mcp_server_name={name}); move to the subagent leaf"
            )
            continue
        if not ttype.startswith("agent_toolset"):
            continue
        # Inspect per-tool configs.
        default_cfg = entry.get("default_config") or {}
        default_enabled = bool(default_cfg.get("enabled", False))
        configs = entry.get("configs") or []
        seen = set()
        for cfg in configs:
            if not isinstance(cfg, dict):
                continue
            name = cfg.get("name")
            enabled = bool(cfg.get("enabled", default_enabled))
            seen.add(name)
            if enabled and name == "write":
                errs.append(
                    f"{path}: orchestrator must not enable 'write'; "
                    f"only the writer leaf holds Write"
                )
            if enabled and isinstance(name, str) and name.startswith("slack"):
                errs.append(
                    f"{path}: orchestrator must not enable Slack tool '{name}'; "
                    f"emit a handoff_request instead"
                )
        # If the default is enabled, it extends to every tool in the toolset —
        # including write and Slack. We cannot enumerate the toolset here, so
        # reject default-enabled on orchestrators outright.
        if default_enabled:
            errs.append(
                f"{path}: orchestrator agent_toolset must have "
                f"default_config.enabled=false; got default enabled=true"
            )
    return errs


def main() -> int:
    if not COOKBOOKS_DIR.is_dir():
        print(f"no cookbooks dir at {COOKBOOKS_DIR}", file=sys.stderr)
        return 2
    total_errs: list[str] = []
    clean: list[str] = []
    for agent_yaml in sorted(COOKBOOKS_DIR.glob("*/agent.yaml")):
        errs = _lint_one(agent_yaml)
        if errs:
            total_errs.extend(errs)
        else:
            clean.append(agent_yaml.parent.name)
    if total_errs:
        print("tool-scope lint FAILED:", file=sys.stderr)
        for e in total_errs:
            print(f"  {e}", file=sys.stderr)
        return 1
    for slug in clean:
        print(f"  ✓ {slug:24s} orchestrator tool scope clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
