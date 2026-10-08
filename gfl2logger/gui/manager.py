import asyncio
import logging
import multiprocessing
import queue
from pathlib import Path

from mitmproxy import ctx, log, optmanager

from gfl2logger.gui import window
from gfl2logger.gui.command import Command, CommandType
from gfl2logger.utils import asyncio_utils
from gfl2logger.utils.optmanager_wrapper import GFL2OptManagerWrapper
from gfl2logger.utils.paths import CONFIG_FILENAME

logger = logging.getLogger(__name__)

GUI_POLL_SECONDS = 1.0
MAX_PENDING_GUI_COMMANDS = 2048


def send_nowait(target: "multiprocessing.Queue[Command]", command: Command) -> bool:
    """Queue a command for the window without ever blocking the proxy on a stuck GUI."""
    try:
        target.put_nowait(command)
    except queue.Full:
        return False
    return True


class GUIManager:
    def __init__(self):
        self.from_gui: "multiprocessing.Queue[Command]" = multiprocessing.Queue()
        # Bounded so a window that stops reading cannot make log records pile up in memory.
        self.to_gui: "multiprocessing.Queue[Command]" = multiprocessing.Queue(
            maxsize=MAX_PENDING_GUI_COMMANDS
        )
        self.subprocess = multiprocessing.Process(
            target=window.draw_window,
            args=(self.from_gui, self.to_gui),
            name="TkWindow",
            daemon=True,
        )
        self.log_handler = GuiLogHandler(self.to_gui)
        self.log_handler.install()

    async def loop(self) -> None:
        self.subprocess.start()
        try:
            # Wake up periodically: if the window process dies without sending SHUTDOWN, a
            # plain blocking read would leave the proxy capturing with no window to quit it.
            while self.subprocess.is_alive():
                try:
                    cmd = await asyncio.to_thread(
                        self.from_gui.get, True, GUI_POLL_SECONDS
                    )
                except queue.Empty:
                    continue
                if cmd.type == CommandType.SHUTDOWN:
                    break
                try:
                    self.handle_command(cmd)
                except Exception as error:
                    # A failed command must not end this loop, or the window could no
                    # longer shut the app down.
                    logger.error(f"Unable to apply {cmd.type.name}, error={error}")
        finally:
            ctx.master.shutdown()

    def handle_command(self, cmd: Command) -> None:
        match cmd.type:
            case CommandType.OPTIONS:
                for opt in cmd.content:
                    setattr(ctx.options, opt, cmd.content[opt])
            case CommandType.SAVE_OPTIONS:
                optmanager.save(
                    self.optmanager_wrapper,
                    Path(ctx.options.confdir).joinpath(CONFIG_FILENAME),
                    defaults=True,
                )
                logger.log(log.ALERT, f"Configurations saved to {CONFIG_FILENAME}")
            case _:
                logger.warning(
                    f"Unrecognized command from gui, cmd.type={cmd.type}, cmd.content={cmd.content}"
                )

    def configure(self, updated: set[str]) -> None:
        send_nowait(
            self.to_gui,
            Command(
                CommandType.OPTIONS,
                {
                    opt: getattr(ctx.options, opt)
                    for opt in updated
                    if opt.startswith("gfl2_")
                },
            ),
        )

    def load(self, _) -> None:
        self.optmanager_wrapper = GFL2OptManagerWrapper(ctx.options)

    async def running(self) -> None:
        asyncio_utils.create_task(self.loop())

    async def done(self) -> None:
        send_nowait(self.to_gui, Command(CommandType.SHUTDOWN, None))
        # Signal-driven shutdown can reach done() while loop() is blocked in
        # from_gui.get().  Wake that read so asyncio can close its worker thread
        # and the frozen macOS app can exit cleanly.
        self.from_gui.put(Command(CommandType.SHUTDOWN, None))
        self.subprocess.join(timeout=5)
        self.subprocess.terminate()
        self.log_handler.uninstall()


class GuiLogHandler(log.MitmLogHandler):
    def __init__(self, to_gui: "multiprocessing.Queue[Command]"):
        super().__init__()
        self.to_gui = to_gui
        self.formatter = log.MitmFormatter(False)

    def emit(self, record: logging.LogRecord):
        # Dropping a log line is better than blocking the capture path on the window.
        send_nowait(self.to_gui, Command(CommandType.LOG, self.format(record)))
