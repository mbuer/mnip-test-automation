from mnip_test_automation.config import load_config
from mnip_test_automation.switch import OnyxSwitch
from mnip_test_automation.watcher import MultiLaneWatcher


def main() -> None:
    config = load_config()

    switch = OnyxSwitch(
        switch_config=config.switch,
        network_config=config.network,
    )

    watcher = MultiLaneWatcher(
        config=config,
        switch=switch,
    )

    watcher.run_forever()


if __name__ == "__main__":
    main()
