import asyncio
import logging
from collections.abc import Generator
from typing import Self

from gfl2logger.gfl2.data import DATA_TYPES
from gfl2logger.gfl2.data.base import BaseData, ReassemblyLimitError
from gfl2logger.utils import asyncio_utils

logger = logging.getLogger(__name__)

MAX_MESSAGE_QUEUE_ITEMS = 16
MAX_PAYLOAD_QUEUE_ITEMS = 128
MAX_INPUT_CHUNK_BYTES = 1024 * 1024
REASSEMBLY_TIMEOUT_SECONDS = 30.0


class Payload:
    def __init__(self, b: bytearray, msg_id=-1):
        if len(b) < 4:
            raise Exception(
                f"cannot construct payload with less than 4 bytes, b={b.hex()}"
            )
        self.msg_id = msg_id
        self.end_of_msg = False
        self.type = int.from_bytes(b[0:2], "little")
        self.len = int.from_bytes(b[2:4], "little") + 4
        if self.len > len(b):
            raise Exception(
                f"not enough data to construct payload, expected_len={self.len}, len(b)={len(b)}, b={b.hex()}"
            )
        self.data = bytes(b[4 : self.len])

    @classmethod
    def from_sequence(cls, b: bytearray, msg_id=-1) -> Generator[Self]:
        i = 0
        try:
            while i < len(b):
                payload = cls(b[i:], msg_id)
                i += payload.len
                if i >= len(b):
                    payload.end_of_msg = True
                yield payload
        except Exception as e:
            logger.error(f"Malformed payload, exception={e}")


class GFL2Parser:
    def __init__(self, *, reassembly_timeout: float = REASSEMBLY_TIMEOUT_SECONDS):
        self.msg_queue: asyncio.Queue[bytes] = asyncio.Queue(
            maxsize=MAX_MESSAGE_QUEUE_ITEMS
        )
        self.payload_queue: asyncio.Queue[Payload] = asyncio.Queue(
            maxsize=MAX_PAYLOAD_QUEUE_ITEMS
        )
        self.active = True
        self.reassembly_timeout = reassembly_timeout
        self._pending_payload: Payload | None = None
        self._pending_data: BaseData | None = None
        self._pending_started_at: float | None = None

        self._tasks = (
            asyncio_utils.create_task(self.parse_message()),
            asyncio_utils.create_task(self.parse_payload()),
        )

    def stop(self) -> None:
        self.active = False
        self.msg_queue.shutdown()
        self.payload_queue.shutdown()

    async def on_message(self, content: bytes) -> None:
        if len(content) > MAX_INPUT_CHUNK_BYTES:
            logger.warning(
                "Dropping oversized TCP chunk, len=%d, max=%d",
                len(content),
                MAX_INPUT_CHUNK_BYTES,
            )
            return
        await self.msg_queue.put(content)

    async def parse_message(self) -> None:
        buffer = bytearray()
        total_len = 0
        msg_id = -1

        while self.active:
            try:
                content = await self.msg_queue.get()
            except asyncio.QueueShutDown:
                break

            buffer.extend(content)

            while True:
                if total_len == 0 and len(buffer) < 5:
                    logger.warning(
                        f"Message skipped due to insufficient length, buffer={buffer.hex()}"
                    )
                    buffer.clear()
                    break

                # start of new messsage
                if total_len == 0:
                    msg_id = int.from_bytes(buffer[0:3], "little")
                    total_len = int.from_bytes(buffer[3:5], "little") + 5

                # wait for more data
                if total_len > len(buffer):
                    break

                for payload in Payload.from_sequence(buffer[5:total_len], msg_id):
                    await self.payload_queue.put(payload)

                # end of mesage
                if total_len == len(buffer):
                    buffer.clear()
                    total_len = 0
                    msg_id = -1
                    break

                # jump to next message
                buffer = buffer[total_len:]
                total_len = 0
                msg_id = -1

    async def _export_data(self, data: BaseData) -> None:
        try:
            await data.export()
        except Exception as e:
            logger.error(f"Unable to export data, exception={e}")

    def _clear_pending(self) -> None:
        self._pending_payload = None
        self._pending_data = None
        self._pending_started_at = None

    async def _export_pending(self) -> None:
        data = self._pending_data
        self._clear_pending()
        if data is not None:
            await self._export_data(data)

    async def _next_payload(self) -> Payload | None:
        if self._pending_started_at is None:
            return await self.payload_queue.get()

        deadline = self._pending_started_at + self.reassembly_timeout
        remaining = deadline - asyncio.get_running_loop().time()
        if remaining <= 0:
            logger.warning("Payload reassembly timed out; dropping incomplete sequence")
            self._clear_pending()
            return None

        try:
            return await asyncio.wait_for(self.payload_queue.get(), timeout=remaining)
        except TimeoutError:
            logger.warning("Payload reassembly timed out; dropping incomplete sequence")
            self._clear_pending()
            return None

    async def _process_payload(self, payload: Payload) -> None:
        logger.debug(
            f"PLD: msg_id={payload.msg_id}, eom={payload.end_of_msg}, type={payload.type}, len={payload.len}"
        )

        if self._pending_payload is not None and self._pending_data is not None:
            can_append = self._pending_payload.type == payload.type and (
                self._pending_payload.msg_id == 0
                or self._pending_payload.msg_id == payload.msg_id
            )
            if can_append:
                try:
                    self._pending_data.append(payload.data)
                except ReassemblyLimitError as e:
                    logger.warning(
                        "Dropping oversized payload sequence, type=%d, reason=%s",
                        payload.type,
                        e,
                    )
                    self._clear_pending()
                    return

                self._pending_payload = payload
                if payload.msg_id != 0 and payload.end_of_msg:
                    await self._export_pending()
                return

            await self._export_pending()

        if payload.type not in DATA_TYPES:
            return

        data = DATA_TYPES[payload.type](payload.data)
        if payload.msg_id != 0 and payload.end_of_msg:
            await self._export_data(data)
            return

        self._pending_payload = payload
        self._pending_data = data
        self._pending_started_at = asyncio.get_running_loop().time()

    async def parse_payload(self) -> None:
        while self.active:
            try:
                payload = await self._next_payload()
            except asyncio.QueueShutDown:
                break
            if payload is None:
                continue
            await self._process_payload(payload)
