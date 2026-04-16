import asyncio

import structlog

from app.runner import BotRunner
from app.settings import SecretSettings, load_config
from app.storage.db import connect
from app.storage.repositories import Repository
from app.utils.logging import configure_logging


def main() -> None:
    secrets = SecretSettings()
    config = load_config(secrets.app_config_path)
    configure_logging(config.log_level)
    log = structlog.get_logger("main")
    log.info("config_loaded", config_path=secrets.app_config_path, mode=config.mode.value, symbols=config.symbols)

    conn = connect(config.sqlite_path)
    repo = Repository(conn)
    log.info("db_initialized", sqlite_path=config.sqlite_path)

    runner = BotRunner(config, secrets, repo)

    try:
        try:
            import uvloop

            uvloop.install()
            log.info("uvloop_installed")
        except Exception as exc:
            log.exception("uvloop_not_installed", error=str(exc))

        asyncio.run(runner.run())
    except KeyboardInterrupt:
        log.info("shutdown", reason="keyboard_interrupt")
    except Exception as exc:
        log.exception("shutdown", reason="unhandled_exception", error=str(exc))
        raise
    finally:
        log.info("shutdown", reason="main_exit")


if __name__ == "__main__":
    main()
