import sys
import inspect
import logging
import string
import pprint
import importlib


# =====
def get_logger(name=None, bind=1, **context):
    if name is None:
        caller_frame = _get_stack_frames()[bind]
        caller_module = inspect.getmodule(caller_frame)
        name = caller_module.__name__
    for frame in _get_stack_frames()[1:]:
        if "__logger_context" in frame.f_locals:
            context = _get_new_context(frame.f_locals["__logger_context"], context)
            break
    _get_stack_frames()[bind].f_locals["__logger_context"] = context
    logger = _ContextLogger(logging.getLogger(name), context=context)
    return logger


getlogger = get_logger


def _get_stack_frames():
    # Get a list of records for a frame and all higher (calling) frames.
    # XXX: We do not use inspect.stack(), because getframeinfo(), which he uses takes too much time under PyPy.
    frame = sys._getframe(1)
    frames = []
    while frame is not None:
        frames.append(frame)
        frame = frame.f_back
    return frames


def _get_new_context(old_context, new_context):
    context = old_context.copy()
    context.update(new_context)
    return context


class _ContextLogger(logging.Logger):
    def __init__(self, logger, context):
        super().__init__(logger.name)
        self._logger = logger
        self._context = context
        self.level = logger.level
        self.parent = logger.parent

    def get_logger(self, **context):
        return _ContextLogger(self._logger, _get_new_context(self._context, context))

    getlogger = get_logger

    def _log(self, level, msg, args, exc_info=None, stack_info=False, **context):
        context = _get_new_context(self._context, context)
        context["_extra"] = _PrettyDict(context)
        self._logger._log(level, msg, args, exc_info, context, stack_info)


class _PrettyDict(dict):
    def __format__(self, _):
        return " ".join(
            "{}={}".format(key, repr(value))
            for (key, value) in self.items()
        )


# =====
def make_mixed_formatter(*args, **kwargs):
    # XXX: About a naming: logger is configured by classes, so it should look like, as a class
    formatters = []
    for item in kwargs.pop("formatters", (logging.Formatter,)):
        if isinstance(item, str):
            parts = item.split(".")
            assert len(parts) >= 2, "Required <module.formatter>, not {}".format(item)
            formatter = getattr(importlib.import_module(".".join(parts[:-1])), parts[-1])
        else:
            formatter = item
        formatters.append(formatter)

    class _MixedFormatter(*formatters):
        pass

    return _MixedFormatter(*args, **kwargs)


class ExceptionLocalsFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self._max_vars_lines = kwargs.pop("max_vars_lines", 100)
        self._max_line_len = kwargs.pop("max_line_len", 100)
        super().__init__(*args, **kwargs)

    def formatException(self, exc_info):
        vars_lines = pprint.pformat(self._get_locals(exc_info)).split("\n")

        if len(vars_lines) > self._max_vars_lines:
            vars_lines = vars_lines[:self._max_vars_lines]
            vars_lines.append("...")

        for count in range(len(vars_lines)):
            line = vars_lines[count]
            if len(line) > self._max_line_len:
                vars_lines[count] = line[:self._max_line_len - 3] + "..."

        output = "\n".join([
            super().formatException(exc_info),
            "\nLocals at innermost frame:\n",
        ] + vars_lines)
        return output

    def _get_locals(self, exc_info):
        tb = exc_info[2]  # This is the outermost frame of the traceback
        while tb.tb_next is not None:
            tb = tb.tb_next  # Zoom to the innermost frame
        return tb.tb_frame.f_locals


class PartialFormatter(logging.Formatter):
    def formatMessage(self, record):
        return _PartialStringFormatter().format(self._style._fmt, **vars(record))


class _PartialStringFormatter(string.Formatter):
    def get_field(self, field_name, args, kwargs):
        try:
            val = super().get_field(field_name, args, kwargs)
        except (KeyError, AttributeError):
            val = ("", field_name)
        if "_extra" in kwargs:
            kwargs["_extra"].pop(field_name.split(".")[0], None)
        return val
