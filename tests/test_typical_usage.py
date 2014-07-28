import logging
import logging.config
import contextlog
import textwrap
import io

import mock
import yaml


# =====
class TestTypicalUsage:
    def test_usage(self, capsys):
        logging.config.dictConfig(yaml.load(textwrap.dedent("""
            version: 1
            disable_existing_loggers: false
            loggers:
                test:
                    level: DEBUG
                    handlers: [default]
            formatters:
                default:
                    (): contextlog.MixedFormatter
                    formatters:
                        - colorlog.ColoredFormatter
                        - contextlog.PartialFormatter
                        - contextlog.ExceptionLocalsFormatter
                    style: "{"
                    format: "{log_color}{levelname:>7} {purple}{name:20.20}{reset} CTX={ctx} CTX_INT={ctx_internal} {message}"
            handlers:
                default:
                    level: DEBUG
                    class: logging.StreamHandler
                    formatter: default
            root:
                level: DEBUG
                handlers: [default]
        """)))

        log = contextlog.get_logger(__name__, ctx="test")
        log.info("Message #1")

        saved_logger = []  # Only for test!

        def method():
            bar = 1
            log = contextlog.get_logger(__name__, ctx_internal="method")
            saved_logger.append(log)
            log.debug("Message #2")
            try:
                raise RuntimeError
            except:
                log.exception("Exception")
        method()

        log = contextlog.get_logger(__name__)
        log.info("Message #3")

        output = (
            "\x1b[32m   INFO \x1b[35mtests.test_typical_u\x1b[39;49;0m CTX=test CTX_INT= "
            "Message #1\x1b[39;49;0m\n"
            "\x1b[37m  DEBUG \x1b[35mtests.test_typical_u\x1b[39;49;0m CTX=test "
            "CTX_INT=method Message #2\x1b[39;49;0m\n"
            "\x1b[31m  ERROR \x1b[35mtests.test_typical_u\x1b[39;49;0m CTX=test "
            "CTX_INT=method Exception\n"
            "Traceback (most recent call last):\n"
            "  File "
            "\"%s\", line "
            "51, in method\n"
            "    raise RuntimeError\n"
            "RuntimeError\n"
            "\n"
            "Locals at innermost frame:\n"
            "\n"
            "{'__logger_context': {'ctx': 'test', 'ctx_internal': 'method'},\n"
            " 'bar': 1,\n"
            " 'log': %s,\n"
            " 'saved_logger': [%s]}\x1b[39;49;0m\n"
            "\x1b[32m   INFO \x1b[35mtests.test_typical_u\x1b[39;49;0m CTX=test CTX_INT= "
            "Message #3\x1b[39;49;0m\n"
        ) % (__file__, saved_logger[0], saved_logger[0])

        assert capsys.readouterr()[1] == output
