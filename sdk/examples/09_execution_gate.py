"""执行开关与诚实降级. Run with --help for live-mode arguments."""

import sys

from datapanel_agent.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["execution-gate", *sys.argv[1:]]))
