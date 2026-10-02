"""任务跟踪与取消回读. Run with --help for live-mode arguments."""

import sys

from datapanel_agent.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["job-lifecycle", *sys.argv[1:]]))
