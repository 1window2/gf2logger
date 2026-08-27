import asyncio
import json
import logging
from typing import Any

from mitmproxy import ctx, log

from gfl2logger.gfl2.data.base import BaseData
from gfl2logger.gfl2.protobuf_wire import WireDecodeError, decode_message

logger = logging.getLogger(__name__)


class PlatoonUpdatesData(BaseData):
    OPTIONS = [
        {
            "name": "gfl2_platoonupdates",
            "label": "Updates",
            "category": "Platoon",
            "typespec": bool,
            "default": True,
            "help": "Log live Platoon update payloads",
        }
    ]

    async def export(self) -> None:
        if ctx.options.gfl2_platoonupdates:
            await asyncio.to_thread(self.to_json)

    def to_dicts(self) -> list[dict[str, Any]]:
        decoded = []
        for payload in self.data:
            item: dict[str, Any] = {"rawHex": payload.hex()}
            try:
                item["fields"] = decode_message(payload)
            except WireDecodeError as error:
                item["decodeError"] = str(error)
            decoded.append(item)
        return decoded

    def to_json(self) -> None:
        filename = self.output_path(
            f"gfl2logger_platoonupdates_{self.log_time.strftime('%Y%m%dT%H%M%SZ')}.json"
        )
        try:
            with open(filename, "w", encoding="utf-8") as output:
                json.dump(self.to_dicts(), output, ensure_ascii=False, indent=2)
            logger.log(log.ALERT, f"Platoon updates data written to {filename}")
        except OSError as error:
            logger.error(f"Failed to write to {filename}, error={error}")
