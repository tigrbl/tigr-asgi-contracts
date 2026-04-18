#!/usr/bin/env python3
"""Backward-compatible wrapper for the full ssot-registry sync tool."""

from __future__ import annotations

from sync_ssot_registry import main as sync_main


if __name__ == "__main__":
    sync_main()
