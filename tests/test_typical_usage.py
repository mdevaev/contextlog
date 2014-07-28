import logging
import logging.config
import contextlog
import textwrap
import pkgutil

import pytest
import yaml


# =====
@pytest.fixture(scope="module")
def typical_usage_stderr():
    return pkgutil.get_data(__package__, "data/typical_usage_stderr.txt").decode()


def test_typical_usage(capsys, typical_usage_stderr):
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

    captured_stderr = capsys.readouterr()[1]
    assert captured_stderr == typical_usage_stderr % (__file__, saved_logger[0], saved_logger[0])
