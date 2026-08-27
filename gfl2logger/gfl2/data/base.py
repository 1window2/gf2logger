import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mitmproxy import addonmanager, ctx

logger = logging.getLogger(__name__)


class BaseData:
    OPTIONS: list[dict[str, Any]] = []

    @classmethod
    def add_options(cls, loader: addonmanager.Loader) -> None:
        for opt in cls.OPTIONS:
            if "name" in opt:
                loader.add_option(
                    name=opt["name"],
                    typespec=opt.get("typespec", bool),
                    default=opt.get("default", True),
                    help=opt.get("help", ""),
                )

    def __init__(self, b: bytes):
        self.data = [b]
        self.log_time = datetime.now(timezone.utc)

    def append(self, b: bytes):
        self.data.append(b)

    @staticmethod
    def output_path(filename: str) -> Path:
        return Path(ctx.options.confdir).joinpath(filename)

    async def export(self) -> None:
        for b in self.data:
            logger.debug(b.hex())
