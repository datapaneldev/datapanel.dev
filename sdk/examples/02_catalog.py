"""发现可用数据. Run with --help for live-mode arguments."""

import sys

from datapanel_agent.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["catalog", *sys.argv[1:]]))
