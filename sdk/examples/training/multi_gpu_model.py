"""Conditional two-GPU DDP test; no CPU fallback and no current production acceptance."""

from datapanel_agent.training import main

if __name__ == "__main__":
    raise SystemExit(main("multi-gpu"))
