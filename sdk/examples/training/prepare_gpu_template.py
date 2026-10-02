"""Prepare synthetic GPU input or validate your own JSON, without an API call.

Generate: python examples/training/prepare_gpu_template.py --output work/gpu-input
Validate: python examples/training/prepare_gpu_template.py --validate work/gpu-input/input.json
"""

from datapanel_agent.gpu_template import main

if __name__ == "__main__":
    raise SystemExit(main())
