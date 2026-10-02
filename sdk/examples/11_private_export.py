"""私有结果安全导出. Run with --help for live-mode arguments."""

import sys

from datapanel_agent.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["private-export", *sys.argv[1:]]))
