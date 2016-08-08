import os
import logging
import logging.config
import pkgutil

import pytest
import yaml
import contextlog


# =====
def _get_content(name):
    return pkgutil.get_data(__package__, os.path.join("data", name)).decode()


@pytest.fixture(scope="module")
def typical_usage_config():
    return yaml.load(_get_content("typical_usage_config.yaml"))


@pytest.fixture(scope="module")
def typical_usage_stderr():
    return _get_content("typical_usage_stderr.txt")


def test_typical_usage_patched(  # pylint: disable=redefined-outer-name
    capsys, typical_usage_config, typical_usage_stderr,
):
    try:
        orig_logger_class = logging.getLoggerClass()
        contextlog.patch_logging()
        test_typical_usage(capsys, typical_usage_config, typical_usage_stderr)
    finally:
        logging.setLoggerClass(orig_logger_class)


def test_typical_usage(  # pylint: disable=redefined-outer-name
    capsys, typical_usage_config, typical_usage_stderr,
):
    try:
        logging.config.dictConfig(typical_usage_config)

        log = contextlog.get_logger(ctx="test")
        log.info("Message #1")

        saved_logger = None  # Only for test!

        def method():
            log = contextlog.get_logger(ctx_internal="method")
            nonlocal saved_logger
            saved_logger = log
            log.debug("Message #2")
            try:
                raise RuntimeError
            except Exception:
                log.exception("Exception")
        method()

        log = contextlog.get_logger()
        log.info("Message #3")

        captured_stderr = capsys.readouterr()[1]
        typical_usage_stderr = typical_usage_stderr.format(
            module_path=__file__,
            logger=saved_logger,
        )

        assert captured_stderr == typical_usage_stderr
    finally:
        logging.Logger.manager.loggerDict = {}
