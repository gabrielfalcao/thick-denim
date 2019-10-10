# -*- coding: utf-8 -*-
"""
holds everything related to logging and console output.
"""
import os
import sys
import logging
from thick_denim.fs import app_icon_path

try:
    from pync import Notifier
except:
    Notifier = None


verbose_mode = bool(os.getenv("THICK_DENIM_VERBOSE")) or True
debug_mode = bool(os.getenv("THICK_DENIM_DEBUG")) or True

# set global level in root logger based on
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)


def print(*parts):
    msg = " ".join(map(str, parts))
    print_to_stdout(msg)


def print_err(msg):
    print_to_stderr(f"❌ \033[1;33m{msg}\033[0m")


def print_to_stdout(msg):
    """prints the given string into the stdout"""
    print_to_fd(msg, sys.stdout)


def print_to_fd(msg, fd):
    """prints the given string into the given file-like object"""
    fd.write(f"{msg}\n")
    fd.flush()


def print_to_stderr(msg):
    """prints the given string into the stderr"""
    print_to_fd(msg, sys.stderr)


def set_debug_mode(debug: bool):
    """sets the debug flag globally"""

    global debug_mode

    if debug_mode and debug:  # alreaady set to True
        return

    debug_mode = debug

    if not debug:
        return

    logging.getLogger().setLevel(logging.DEBUG)

    # print_to_stderr(
    #     f"\033[1;30mrunning in debug mode. "
    #     f"Use `newstore --no-debug` to reduce verbosity.\033[0m"
    # )


def set_verbose_mode(verbose: bool):
    """sets the verbose flag globally"""
    global verbose_mode

    if verbose_mode and verbose:  # alreaady set to True
        return

    verbose_mode = verbose

    if not verbose:
        return

    logging.getLogger().setLevel(logging.INFO)

    # print_to_stderr(
    #     f"\033[1;30mrunning in verbose mode. "
    #     f"Use `newstore --no-verbose` to reduce verbosity.\033[0m"
    # )


def get_logger(*args, **kw) -> logging.Logger:
    """alias to :py:func:`logging.getLogger`"""
    logger = logging.getLogger(*args, **kw)
    return logger


class UIReporter(object):
    """Utility to report messages to the command-line while respecting the
    global flags ``verbose`` and ``debug``.

    This class can be instantiated at any time.
    The default file-descriptor for writing messages is sys.stderr.
    """

    def __init__(self, name, fd=sys.stderr):
        self.name = name
        self.fd = fd

    def verbose_ansi_print(
        self,
        message: str,
        ansi_prefix: str = "\033[1l37m",
        ansi_suffix: str = "\033[0m",
    ):
        if not verbose_mode:
            return

        self.fd.write(
            f"{ansi_prefix}{self.name}{ansi_suffix}\033[1;30m:\033[0m {message}\n"
        )
        self.fd.flush()

    def report(self, message):
        self.verbose_ansi_print(f"\033[1;30m{message}\033[0m", "\033[1;30m")

    def info(self, message):
        self.verbose_ansi_print(message, "\033[1;32m")

    def error(self, message):
        self.verbose_ansi_print(message, "\033[1;31m")

    def warning(self, message):
        self.verbose_ansi_print(message, "\033[1;33m")

    def debug(self, message):
        if not debug_mode:
            return
        self.verbose_ansi_print(message, "\033[1;34m")

    def notify(self, message: str, **kw):
        if not Notifier:
            return

        kw["title"] = "NewStore Toolbelt"
        kw["group"] = os.getpid()
        kw["appIcon"] = str(app_icon_path.absolute())
        try:
            Notifier.notify(message, **kw)
        except Exception as e:
            logger.exception(f"failed to send notification {message!r}: {e}")
