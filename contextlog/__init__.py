import inspect
import logging
import string
import pprint

import colorlog


# =====
def get_logger(name, bind=1, **context):
    for (frame, _, _, _, _, _) in inspect.stack()[1:]:
        if "__logger_context" in frame.f_locals:
            context = _get_new_context(frame.f_locals["__logger_context"], context)
            break
    inspect.stack()[bind][0].f_locals["__logger_context"] = context
    return _ContextLogger(logging.getLogger(name), context=context)


class PartialFormatter(colorlog.ColoredFormatter):
    def __init__(self, *args, **kwargs):
        self._max_vars_lines = kwargs.pop("max_vars_lines", 100)
        self._max_line_len = kwargs.pop("max_line_len", 100)
        super().__init__(*args, **kwargs)

    def formatMessage(self, record):
        return _PartialStringFormatter().format(self._style._fmt, **vars(record))  # pylint: disable=W0212

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


# =====
def _get_new_context(old_context, new_context):
    context = old_context.copy()
    context.update(new_context)
    return context


class _ContextLogger(logging.Logger):  # pylint: disable=R0904
    def __init__(self, logger, context):
        super().__init__(logger.name)
        self._logger = logger
        self._context = context
        self.level = logger.level
        self.parent = logger.parent

    def get_logger(self, **context):
        return _ContextLogger(self._logger, _get_new_context(self._context, context))

    def _log(self, level, msg, args, exc_info=None, stack_info=False, **context):
        context = _get_new_context(self._context, context)
        context["_extra"] = dict(context)
        self._logger._log(level, msg, args, exc_info, context, stack_info)  # pylint: disable=W0212


class _PartialStringFormatter(string.Formatter):  # pylint: disable=W0232
    def get_field(self, field_name, args, kwargs):
        if field_name == "_extra":
            extra_text = " ".join(
                "{}={}".format(key, repr(value))
                for (key, value) in kwargs["_extra"].items()
            )
            return (extra_text, field_name)

        try:
            val = super().get_field(field_name, args, kwargs)
        except (KeyError, AttributeError):
            val = ("", field_name)
        kwargs["_extra"].pop(field_name.split(".")[0], None)
        return val