"""Conditional single-GPU payload; requires an actual published CUDA runtime."""

from datapanel_agent.training import main

if __name__ == "__main__":
    raise SystemExit(main("gpu"))
