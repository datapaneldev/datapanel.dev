"""平台内数据访问. Run with --help for live-mode arguments."""

import sys

from datapanel_agent.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["data-access", *sys.argv[1:]]))
