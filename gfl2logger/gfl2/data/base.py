import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mitmproxy import addonmanager, ctx

logger = logging.getLogger(__name__)


class ReassemblyLimitError(ValueError):
    """Raised when a payload sequence exceeds its bounded reassembly budget."""


class BaseData:
    OPTIONS: list[dict[str, Any]] = []
    MAX_REASSEMBLY_BYTES = 8 * 1024 * 1024
    MAX_REASSEMBLY_FRAGMENTS = 256

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
        if len(b) > self.MAX_REASSEMBLY_BYTES:
            raise ReassemblyLimitError(
                f"initial payload exceeds {self.MAX_REASSEMBLY_BYTES} bytes"
            )
        self.data = [b]
        self.reassembled_bytes = len(b)
        self.log_time = datetime.now(timezone.utc)

    def append(self, b: bytes) -> None:
        next_size = self.reassembled_bytes + len(b)
        if len(self.data) >= self.MAX_REASSEMBLY_FRAGMENTS:
            raise ReassemblyLimitError(
                f"payload sequence exceeds {self.MAX_REASSEMBLY_FRAGMENTS} fragments"
            )
        if next_size > self.MAX_REASSEMBLY_BYTES:
            raise ReassemblyLimitError(
                f"payload sequence exceeds {self.MAX_REASSEMBLY_BYTES} bytes"
            )
        self.data.append(b)
        self.reassembled_bytes = next_size

    @staticmethod
    def output_path(filename: str) -> Path:
        return Path(ctx.options.confdir).joinpath(filename)

    async def export(self) -> None:
        for b in self.data:
            logger.debug(b.hex())
