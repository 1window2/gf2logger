import asyncio
import json
import logging
from collections.abc import Generator
from typing import Any

from google.protobuf import json_format
from mitmproxy import ctx, log

from generated.platoon_profile_pb2 import PlatoonProfileResponse
from gfl2logger.gfl2.data.base import BaseData

logger = logging.getLogger(__name__)


class PlatoonProfileData(BaseData):
    OPTIONS = [
        {
            "name": "gfl2_platoonprofile",
            "label": "Platoon Profile",
            "category": "Platoon",
            "typespec": bool,
            "default": True,
            "help": "Log the Platoon profile",
        }
    ]

    async def export(self) -> None:
        if ctx.options.gfl2_platoonprofile:
            await asyncio.to_thread(self.to_json)

    def to_dicts(self) -> Generator[dict[str, Any]]:
        for payload in self.data:
            profile = PlatoonProfileResponse()
            profile.ParseFromString(payload)
            yield json_format.MessageToDict(profile)

    def to_json(self) -> None:
        filename = self.output_path(
            f"gfl2logger_platoonprofile_{self.log_time.strftime('%Y%m%dT%H%M%SZ')}.json"
        )
        try:
            with open(filename, "w", encoding="utf-8") as output:
                json.dump(list(self.to_dicts()), output, ensure_ascii=False, indent=2)
            logger.log(log.ALERT, f"Platoon profile data written to {filename}")
        except OSError as error:
            logger.error(f"Failed to write to {filename}, error={error}")
