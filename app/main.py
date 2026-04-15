import asyncio

try:
    import uvloop
except Exception:  # pragma: no cover
    uvloop = None

from app.runner import BotRunner
from app.settings import SecretSettings, load_config
from app.storage.db import connect
from app.storage.repositories import Repository
from app.utils.logging import configure_logging


def main() -> None:
    secrets = SecretSettings()
    config = load_config(secrets.app_config_path)
    configure_logging(config.log_level)
    repo = Repository(connect(config.sqlite_path))
    runner = BotRunner(config, secrets, repo)
    if uvloop is not None:
        uvloop.install()
    asyncio.run(runner.run())


if __name__ == "__main__":
    main()
