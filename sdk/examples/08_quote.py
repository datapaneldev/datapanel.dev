"""有预算上限的算力报价. Run with --help for live-mode arguments."""

import sys

from datapanel_agent.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["quote", *sys.argv[1:]]))
