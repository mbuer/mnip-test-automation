from dataclasses import dataclass

from mnip_test_automation.config import LaneConfig


@dataclass
class LaneState:
    config: LaneConfig
    processed: bool = False
    down_since: float | None = None
