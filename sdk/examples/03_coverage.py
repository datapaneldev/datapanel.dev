"""覆盖率与缺口审计. Run with --help for live-mode arguments."""

import sys

from datapanel_agent.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["coverage", *sys.argv[1:]]))
