import asyncio
import json
import logging
from typing import Any

from google.protobuf import json_format
from mitmproxy import ctx, log

from generated.platoon_activity_pb2 import PlatoonActivityResponse
from gfl2logger.gfl2.data.base import BaseData

logger = logging.getLogger(__name__)


class PlatoonActivityData(BaseData):
    OPTIONS = [
        {
            "name": "gfl2_platoonactivity",
            "label": "Activity",
            "category": "Platoon",
            "typespec": bool,
            "default": True,
            "help": "Log Platoon objectives and member activity",
        }
    ]

    async def export(self) -> None:
        if ctx.options.gfl2_platoonactivity:
            await asyncio.to_thread(self.to_json)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, list[dict[str, Any]]] = {
            "objectives": [],
            "entries": [],
        }
        for payload in self.data:
            activity = PlatoonActivityResponse()
            activity.ParseFromString(payload)
            decoded = json_format.MessageToDict(activity)
            result["objectives"].extend(decoded.get("objectives", []))
            result["entries"].extend(decoded.get("entries", []))
        return result

    def to_json(self) -> None:
        filename = self.output_path(
            f"gfl2logger_platoonactivity_{self.log_time.strftime('%Y%m%dT%H%M%SZ')}.json"
        )
        try:
            with open(filename, "w", encoding="utf-8") as output:
                json.dump(self.to_dict(), output, ensure_ascii=False, indent=2)
            logger.log(log.ALERT, f"Platoon activity data written to {filename}")
        except OSError as error:
            logger.error(f"Failed to write to {filename}, error={error}")
