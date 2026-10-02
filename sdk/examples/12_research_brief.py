"""生成可审查研究简报. Run with --help for live-mode arguments."""

import sys

from datapanel_agent.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["research-brief", *sys.argv[1:]]))
